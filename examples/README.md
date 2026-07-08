# Examples

Sample transcripts for testing and integration. Each line in sample_transcripts.jsonl is
a JSON object with id, 	ranscript, and expected fields.

## Run against samples

`ash
python -m callscope batch examples/sample_transcripts.jsonl --output csv
`

## Expected output

| id       | outcome  | booking | objection | dnc  |
|----------|----------|---------|-----------|------|
| call-001 | human    | false   | false     | false|
| call-002 | voicemail| false   | false     | false|
| call-003 | human    | false   | true      | true |
| call-004 | human    | true    | false     | false|
| call-005 | ivr      | false   | false     | false|
