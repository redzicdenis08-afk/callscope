# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- --output json flag for machine-readable batch results
- Confidence score alongside each signal flag
- Spanish-language IVR signal expansion

## [0.2.0] - 2026-07-08

### Added
- count_matches helper exported from signals module for weighted scoring
- HESITATION signal pack: detects phrases like "let me think" and "I'm not sure"
- URGENCY signal pack: detects "as soon as possible", "urgent", "emergency"
- examples/ directory with sample transcripts and expected output

### Changed
- ny_match now returns early on first hit for ~15% speedup on long transcripts
- README: expanded Quick Start section with real-world examples

### Fixed
- IVR detector false-positive on "press on" in casual speech (anchored word boundary)

## [0.1.0] - 2026-06-24

### Added
- Core signal packs: VOICEMAIL, IVR, OBJECTION, DNC, BOOKING, PRICE, CALLBACK
- SignalPack dataclass with full override support
- nalyze entry point that returns CallResult with all detected flags
- 20-case fictional benchmark in enchmark/calls.jsonl
- CSV and JSONL export via --output flag
- CLI: callscope score <transcript>, callscope batch <file>
- Zero runtime dependencies
- Test suite and CI across Python 3.9 / 3.11 / 3.13
