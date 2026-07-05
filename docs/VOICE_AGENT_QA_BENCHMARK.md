# Voice Agent QA Benchmark

This repo starts with a tiny fictional benchmark for checking whether a voice-agent QA tool can separate useful calls from noise.

## What to measure

A useful first pass should answer:

- Did a human actually engage?
- Was the call voicemail, IVR, or no answer?
- Did the customer mention price?
- Did the customer request a callback?
- Did the call turn into a booked appointment?
- Was there an objection signal?

## Current seed set

The bundled `examples/` folder is intentionally small and fictional. It proves the shape of the output without exposing private calls.

## Expansion plan

Add 20 to 50 fictional transcripts across common buckets, then keep expected outcomes and events next to each sample so future parser changes can be tested against the same public yardstick.
