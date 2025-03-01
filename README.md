# A Map of PyPi Packages


This contains some material to recreate [this](https://fi-le.net/pypi/) visualization of around 100000 PyPi packages and their dependencies.

<img src=pypi.png>

## Reproduction Guide
1. Execute a query like `sample_query.sql` in [BigQuery](https://console.cloud.google.com/bigquery) and export to `.jsonl`.
2. Use `process_json.py` to filter, format and export to `.gexf`.
3. Find a graph layout in e.g. Gephi, export back to `.gexf`.
4. Either visualize with `graph.py` or export to `.json` and visualize with the source of [https://fi-le.net/pypi](https://fi-le.net/pypi/).

