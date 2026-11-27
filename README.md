# Kill Team datacard extractor <!-- omit in toc -->

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-red?style=flat-square)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Shop: Elecrow](https://img.shields.io/badge/shop-Elecrow-blue?style=flat-square)](https://www.elecrow.com/store/Binary-6)
[![Donations: Coffee](https://img.shields.io/badge/donations-Coffee-brown?style=flat-square)](https://github.com/Chrismettal#donations)

This is a script to extract Kill Team 3rd Edition datacards from the free rules PDFs published by Games Workshop.

The free PDFs always start with a few pages of unit rule datacards, followed by faction rule datacards. These are intended to be printed at home and cut out manually. This script automates the cutting part and outputs one image per card, or a stacked PDF with one page per card rotated to be oriented the same way.

**If you like my work please consider [supporting me](https://github.com/Chrismettal#donations)!**

## Table of contents <!-- omit in toc -->

- [Installation](#installation)
- [Usage](#usage)
  - [Arguments](#arguments)
- [Todo](#todo)
- [Donations](#donations)
- [License](#license)

## Installation

This package is published to PyPi, so you can install it with:

`pip install kt3extract`

## Usage

- Go to [Warhammer-Community Kill Team downloads](https://www.warhammer-community.com/en-gb/downloads/kill-team/)
- Download the PDF for the Kill Team you want to play
- Take note of which pages have horizontally drawn datacards, and which pages have vertically drawn datacards.
  - (Unit cards are pasted as ~4 horizontal pages, while rule cards are pasted as ~6 vertical pages)
- Execute the script, making sure to set all required arguments

`kt3extract -hr "1-3" -vr "4-8" -o pdf -i /path/to/killteam.pdf`

Page ranges of the currently published rules PDFs:

| Kill Team | File | `-hr` | `-vr` |
| --- | --- | --- | --- |
| Battleclade | `eng_battleclade_online_rules-…` | `1-3` | `4-8` |
| Kommandos | `eng_17-06_…_kommandos_online_rules-…` | `1-3` | `4-7` |
| Brood Brothers | `eng_28-10_…_brood_brothers-…` | `1-5` | `6-10` |
| Raveners | `eng_28-10_…_raveners-…` | `1-2` | `3-7` |

### Arguments

All arguments are required.

- `-hr` / `--horizontal`: Range of pages where horizontal datacards are situated. `-hr "1-3"`
- `-vr` / `--vertical`: Range of pages where vertical datacards are situated. `-vr "4-5"`
- `-o` / `--output`: Format of output files. Allowed formats: `pdf`, `png`
- `-i` / `--input`: Path to your team's PDF file. `/path/to/killteam.pdf`
- `-p` / `--padding_mm`: Padding around the cards in millimetres, e.g. `-p 3`
- `-px` / `--padding_px`: Padding around the cards in pixels, e.g. `-px 100`.
  Converted using 300 pixels per inch.

`--padding_mm` and `--padding_px` are mutually exclusive. Without either, cards are
output without padding.

The datacards in the Games Workshop PDFs measure 121mm x 70mm. They are scaled
down to 120mm x 70mm, the size of the card blanks they are printed on, so the
printed card reaches all four edges of the blank.

Games Workshop draws a dashed stitch line along the card borders, for cutting the
cards out by hand. It is 0.5pt wide and centred on the border, so 0.088mm of it
lies inside the card. Every crop is therefore inset by 0.5mm on all four sides,
which removes the stitch line with 0.4mm to spare. The remaining 119.9mm x 68.9mm
of card art is stretched to the full 120mm x 70mm, by 0.08% along the long side
and 1.6% along the short side.

## Todo

- [x] Plausibility check input parameters, testing for range format
- [x] Plausibility check input path leads to a PDF
- [x] Read in PDF, splitting into two page stacks for horizontal and vertical pages
- [x] Cut and export each page stack
- [x] Export as stacked PDF
- [x] Add optional padding parameter
- [x] Scale pages to be exactly 70mm x 120mm before padding
- [x] Publish to PyPi
- [ ] Export as PNG

## Donations

**If you like my work please consider [supporting me](https://github.com/Chrismettal#donations)!**

## License

 <a rel="GPLlicense" href="https://www.gnu.org/licenses/gpl-3.0.html"><img alt="GPLv3" style="border-width:0" src="https://www.gnu.org/graphics/gplv3-or-later.png" /></a><br />This work is licensed under a <a rel="GPLlicense" href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPLv3 License</a>.
