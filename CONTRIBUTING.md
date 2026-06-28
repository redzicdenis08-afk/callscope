# Contributing to callscope

Thanks for considering a contribution. This project aims to stay small, fast, and dependency-free at its core.

## Development setup

```bash
git clone https://github.com/redzicdenis08-afk/callscope
cd callscope
pip install -e ".[dev]"
```

## Running tests

```bash
pytest -q
# or, with zero dependencies:
python tests/test_callscope.py
```

## Guidelines

- Keep the core dependency-free (standard library only). Optional features go behind extras (`pip install callscope[llm]`, etc.).
- Add a test for any new outcome, event, or parser you introduce.
- Run `ruff check .` before opening a PR.
- One focused change per PR. Describe the before/after behavior in the description.

## Adding a new transcript format

1. Add a `parse_<provider>` function in `callscope/parser.py` that returns a `Transcript`.
2. Wire it into `parse_transcript`.
3. Drop a sample under `examples/` and add a test in `tests/`.

## Tuning detection

Detection lives in `callscope/signals.py` as overridable regex packs. If you are adjusting behavior for a vertical or language, prefer adding patterns to a custom `SignalPack` over editing the defaults, and open an issue if you think a pattern belongs in the defaults.
