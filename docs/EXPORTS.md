# Batch exports

`callscope` can analyze a folder of transcripts and write two portable output formats.

## CSV

Use CSV when you want to sort, filter, or chart results in a spreadsheet.

```bash
python -m callscope analyze examples --csv report.csv
```

## JSONL

Use JSONL when you want one machine-readable report per line for pipelines, notebooks, or dashboards.

```bash
python -m callscope analyze examples --jsonl report.jsonl
```

Folder paths are expanded recursively, but only `.json` and `.txt` files are analyzed.
