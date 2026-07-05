# Final launch checklist

## Already automated in the repo

- CI checks Python 3.9 through 3.12.
- CI runs unit tests, pytest, ruff, and the benchmark.
- Launch Ready runs on push, PR, manual trigger, and weekly schedule.
- Launch audit verifies README, docs, benchmark size, demo asset, and setup docs.
- Benchmark has 20 fictional cases.
- README shows a terminal demo and fast commands.

## Manual one-time setup

These cannot be done from repo files alone:

1. Set repository description to: `Offline QA benchmark and batch analytics for AI voice-agent call transcripts.`
2. Set topics from `docs/GITHUB_SETUP.md`.
3. Upload `docs/assets/social-preview.png` as the social preview.
4. Pin `callscope` first on the GitHub profile.
5. Post one launch message from `docs/LAUNCH_POSTS.md`.

## Done means

The repo is launch-ready when Launch Ready is green and the manual one-time setup above is complete.
