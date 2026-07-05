# Benchmark

`callscope benchmark` runs a JSONL yardstick of expected call outcomes and expected customer events.

## Run the bundled seed benchmark

```bash
python -m callscope benchmark benchmark/calls.jsonl
```

The command prints each case, expected outcome, actual outcome, score, and missing expected events.
It exits with code `0` only when every case passes.

## JSONL format

Each line is one case:

```json
{"id":"human_price","format":"text","transcript":"Agent: Hi\nCustomer: How much does it cost?","expected_outcome":"human_reached","expected_events":["price_discussed"]}
```

VAPI-style message lists are supported too:

```json
{"id":"vapi_price","format":"vapi","messages":[{"role":"assistant","message":"Hi"},{"role":"user","message":"What are your rates?"}],"expected_outcome":"human_reached","expected_events":["price_discussed"]}
```

## Why this matters

A public benchmark makes the repo easier to trust because future parser and scoring changes have a visible yardstick.
The bundled cases are fictional and intentionally small so contributors can add coverage without touching private call data.
