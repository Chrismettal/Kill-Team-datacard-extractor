#############################################################################
##                              kt3extract                                    ##
#############################################################################
# Command line tool to consolidate several DHL labels 
# for printing with less waste

import os
import sys
import argparse
import glob
import re
from copy import deepcopy
from pypdf import PdfWriter, PdfReader, Transformation, PaperSize
from pypdf.generic import RectangleObject

#############################################################################
##                           Global variables                              ##
#############################################################################
input_path: str
output_format: str
horizontal_range: str
vertical_range: str
padding_mm: float
padding_px: float

#############################################################################
##                           Global constants                              ##
#############################################################################
# PDF points per millimetre
MM = 72 / 25.4
# Physical size we output each card at, in mm.
# The cards as printed by Games Workshop measure 121mm x 70mm; we scale them
# down to the 120mm x 70mm blank we cut our own cards from.
CARD_LONG = 120
CARD_SHORT = 70
# Pixels per inch assumed when padding is given in pixels
PAD_DPI = 300
# Games Workshop draws a dashed stitch line for cutting the cards out by hand.
# It sits exactly on the card borders, is 0.5pt wide and centred on them, so
# 0.088mm of it lies inside every card. We cut this many millimetres off every
# side of every crop to get rid of it, which clears it by 0.41mm.
CROP_INSET = 0.5

CROPS = [
    [
    (126.141, 619.016, 469.134, 817.441), # Horizontal Line 1
    (126.141, 420.591, 469.134, 619.016), # Horizontal Line 2
    (126.141, 222.166, 469.134, 420.591), # Horizontal Line 3
    (126.141, 23.740, 469.134, 222.165)   # Horizontal Line 4
    ],
    [
    (99.212, 420.945, 297.638, 763.937),  # Vertical Top Left
    (297.638, 420.945, 496.063, 763.937), # Vertical Top Right
    (99.212, 77.953, 297.638, 420.945),   # Vertical Bottom Left
    (297.638, 77.953, 496.063, 420.945)   # Vertical Bottom Right
    ],
    #   (XBL, ZBL, XTR, ZTR)
]
# These are the exact clipping paths Games Workshop draws each card into,
# measured from the rules PDFs themselves. Each card is 342.993pt x 198.425pt,
# which is exactly 121mm x 70mm.

#############################################################################
##                               Helpers                                   ##
#############################################################################

def argset():
    """
    Sets command line arguments
    """
    global input_path
    global output_format
    global horizontal_range
    global vertical_range
    global padding_mm
    global padding_px

    parser = argparse.ArgumentParser(description=
        "Command line tool to extract Kill Team 3rd edition datacards from free rules downloads")

    # Horizontal range
    parser.add_argument(
        '-hr', '--horizontal', 
        default="",
        type=str,
        help="""
            Range of pages with horizontal datacards
            "1-2"
            """
    )

    # Vertical range
    parser.add_argument(
        '-vr', '--vertical', 
        default="",
        type=str,
        help="""
            Range of pages with vertical datacards
            "3-4"
            """
    )
    
    # Input path
    parser.add_argument(
        '-input_path', '-i',
        type=str,
        help="""
            Path to input PDF.
            """
    )

    # Output Format
    parser.add_argument(
        '--output_format', '-o',
        default="png",
        type=str,
        help="""
            Format of output file.
            Available Options:
            png, pdf
            """
    )

    # Padding, either in millimetres or in pixels, never both
    padding_group = parser.add_mutually_exclusive_group()

    padding_group.add_argument(
        '--padding_mm', '-p',
        default=0,
        type=float,
        help="""
            Amount of padding in mm to add around the cards for printing
            """
    )

    padding_group.add_argument(
        '--padding_px', '-px',
        default=0,
        type=float,
        help="""
            Amount of padding in pixels to add around the cards for printing.
            Converted using %d pixels per inch.
            """ % PAD_DPI
    )

    # Parse args
    args = parser.parse_args()
    input_path  = args.input_path
    output_format = args.output_format
    horizontal_range = args.horizontal
    vertical_range = args.vertical
    padding_mm = args.padding_mm
    padding_px = args.padding_px

    # Test for ranges to be valid
    pattern = r'^\d+-\d+$'
    if not re.match(pattern, horizontal_range) or not re.match(pattern, vertical_range):
        print("Ranges entered invalid, please format them like '1-2'")
        sys.exit()

    # Test if input file is valid
    if not input_path.lower().endswith('.pdf'):
        print("File does not seem to be a pdf file")
        sys.exit()
    if not os.path.isfile(input_path):
        print("Input file does not seem to be a file at all")
        sys.exit()

    # Test if a valid output was set
    if not output_format == "pdf" and not output_format == "png":
        print("File format chosen does not match either pdf or png")
        sys.exit()

    # Test if the padding is plausible
    if padding_mm < 0 or padding_px < 0:
        print("Padding can not be negative")
        sys.exit()


def padding_points():
    """
    Resolves the requested padding into PDF points
    """
    if padding_px:
        return padding_px / PAD_DPI * 72
    return padding_mm * MM


def read_file():
    """
    Read in and split file
    """
    global input_path
    global output_format
    global horizontal_range
    global vertical_range

    # Prepare reader and writer
    reader = PdfReader(input_path)
    buffer = PdfWriter()
    writer = PdfWriter()

    # Resolve padding once
    paddingPoints = padding_points()
    # Cut in on every side so the stitch line Games Workshop draws between two
    # neighbouring cards does not end up on the card
    inset = CROP_INSET * MM

    # Get page ranges
    horirange =  [int(num) for num in horizontal_range.split('-')]
    verirange =  [int(num) for num in vertical_range.split('-')]
    pageranges = [horirange, verirange]

    # Loop through the page ranges
    for pagerange in range(2):
        # The physical size of the card we output, in points
        if pagerange == 0:
            cardWidth = CARD_LONG * MM
            cardHeight = CARD_SHORT * MM
        else:
            cardWidth = CARD_SHORT * MM
            cardHeight = CARD_LONG * MM
        # Loop through the pages of the range
        for page in range(pageranges[pagerange][0], pageranges[pagerange][1]+1):
            inpPage = reader.pages[page-1]
            # Loop through the 4 boxes where a card might be
            for card in range(4):
                crop = CROPS[pagerange][card]
                cropXBL, cropZBL = crop[0] + inset, crop[1] + inset
                cropXTR, cropZTR = crop[2] - inset, crop[3] - inset
                cropWidth = cropXTR - cropXBL
                cropHeight = cropZTR - cropZBL
                cropRect = (cropXBL, cropZBL, cropXTR, cropZTR)

                # pagerange contains the number of the range we are currently reading
                # page is the actual page number of the current page we're looking at
                # card is the card slot number on the page we are looking at
                # CROPS[pagerange][card] should return the tuble of our current card cropbox
                
                # Read in single card with cropping
                cardPage = deepcopy(inpPage)
                cardPage.mediabox = cardPage.cropbox = RectangleObject(cropRect)

                # Paste it over to a new card that is also cropped just to discard everything outside of cropping range
                bufferPage = buffer.add_blank_page(width = cropWidth, height = cropHeight)
                bufferPage.mediabox = bufferPage.cropbox = RectangleObject(cropRect)
                bufferPage.merge_page(cardPage)

                # Another deep copy for exact scaling
                interPage = deepcopy(bufferPage)

                # Create a padded page and paste our cropped thingy onto it,
                # scaled so the card itself covers exactly cardWidth x cardHeight
                newPage = writer.add_blank_page(width = cardWidth + 2 * paddingPoints, height = cardHeight + 2 * paddingPoints)
                placement = Transformation()
                placement = placement.translate(-cropXBL, -cropZBL)
                placement = placement.scale(sx = cardWidth / cropWidth, sy = cardHeight / cropHeight)
                placement = placement.translate(paddingPoints, paddingPoints)
                newPage.merge_transformed_page(interPage, placement)

                # Rotate horizontal pages so everything is in the same orientation
                if pagerange == 0:
                    # horizontal pages
                    newPage.rotate(-90)

    # Prepare output directory
    cwd = os.path.dirname(input_path)
    dirname = os.path.splitext(os.path.basename(input_path))[0]
    dirpath = os.path.join(cwd, dirname)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    # Output file(s)
    if output_format == "png":
        print("png output not yet implemented, sorgy")
        sys.exit()
    elif output_format == "pdf":
        # Write resulting PDF
        outputname = os.path.join(dirpath, "output.pdf");
        with open(outputname, "wb") as op:
            writer.write(op)

    print("---")
    print("All cards output")
    print("---")

#############################################################################
##                               main()                                    ##
#############################################################################
def main():

    print("-----------------------")
    print("--Starting kt3extract--")
    print("-----------------------")

    # Set command line arguments
    argset()

    # Output recognized args
    print("Using input path:")
    print(input_path)
    print("Using output format:")
    print(output_format)
    print("---")
    print("Assuming horizontal page range:")
    print(horizontal_range)
    print("Assuming vertical page range:")
    print(vertical_range)
    print("---")
    if padding_px:
        print("Using padding:")
        print("%g px (%.2f mm)" % (padding_px, padding_px / PAD_DPI * 25.4))
    else:
        print("Using padding:")
        print("%g mm" % padding_mm)

    read_file()


#############################################################################
##                         main() idiom                                    ##
#############################################################################
if __name__ == "__main__":
    main()
