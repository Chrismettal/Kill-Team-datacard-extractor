 # Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Card crops now use the exact clipping paths Games Workshop draws its cards into
  (measured from the rules PDFs), instead of rounded approximations that were
  inset about 1pt from the real card edge.
- Output pages are no longer a fixed 120mm x 70mm while the card art is 121mm x
  70mm. That mismatch left an empty strip along the left edge of horizontal
  cards and along the right edge of vertical cards, and clipped the other side.

### Changed
- Cards are scaled to exactly 120mm x 70mm, the size of the card blanks they are
  printed on, so the card art reaches all four edges of the output page.
- Padding is now given either in millimetres (`-p` / `--padding_mm`) or in
  pixels (`-px` / `--padding_px`, assumed 300 dpi). The two are mutually exclusive.

### Added
- Documented the horizontal/vertical page ranges of the currently published
  Kill Team rules PDFs.

## [0.0.1]

### Added
- Initial version
  
### Changed
- nothing

### Deprecated
- nothing

### Removed
- nothing
  
### Fixed
- nothing
  
### Security
- nothing
  