# TMKP KGX DuckDB analysis

This repository contains a small, reproducible analysis of the latest TMKP KGX release from the NCATS Translator KGX storage service.

The large KGX data files are not committed. The notebook expects a local DuckDB database at:

```text
downloads/tmkp/2026_04_21/tmkp.duckdb
```

## Included artifacts

- `scripts/load_tmkp_duckdb.sql` loads extracted KGX JSONL into DuckDB.
- `notebooks/tmkp_category_summary.ipynb` summarizes nodes, edges, sources, qualifiers, evidence, and category flows.
- `notebooks/tmkp_category_summary.html` is the rendered notebook.

## Data release

Latest release inspected:

```text
https://kgx-storage.rtx.ai/releases/tmkp/2026_04_21/
```

Release metadata:

```text
source: tmkp
source_version: tmkp-2023-03-05
transform_version: 6dadae40
node_norm_version: 2025sep1
biolink_version: 4.3.6
release_version: 2026_04_21
```

## Reproduce locally

Install dependencies with `uv`:

```sh
uv sync
```

Download and extract the KGX payload:

```sh
mkdir -p downloads/tmkp/2026_04_21/kgx

curl -fsSL -o downloads/tmkp/2026_04_21/latest-release.json \
  https://kgx-storage.rtx.ai/releases/tmkp/latest-release.json

curl -fsSL -o downloads/tmkp/2026_04_21/graph-metadata.json \
  https://kgx-storage.rtx.ai/releases/tmkp/latest/graph-metadata.json

curl -fL --retry 3 --continue-at - \
  -o downloads/tmkp/2026_04_21/tmkp.tar.zst \
  https://kgx-storage.rtx.ai/releases/tmkp/latest/tmkp.tar.zst

tar --zstd -xf downloads/tmkp/2026_04_21/tmkp.tar.zst \
  -C downloads/tmkp/2026_04_21/kgx
```

Load DuckDB:

```sh
duckdb downloads/tmkp/2026_04_21/tmkp.duckdb \
  < scripts/load_tmkp_duckdb.sql
```

Execute the notebook:

```sh
uv run python -m jupyter nbconvert --to notebook --execute --inplace \
  notebooks/tmkp_category_summary.ipynb \
  --ExecutePreprocessor.timeout=900
```

Render HTML:

```sh
uv run python -m jupyter nbconvert --to html \
  notebooks/tmkp_category_summary.ipynb \
  --output tmkp_category_summary.html \
  --output-dir notebooks
```

## Quick DuckDB examples

```sh
duckdb -readonly downloads/tmkp/2026_04_21/tmkp.duckdb
```

```sql
SELECT category[1] AS primary_node_category, count(*) AS nodes
FROM nodes
GROUP BY 1
ORDER BY nodes DESC;

SELECT
  subject_primary_category,
  predicate,
  object_primary_category,
  count(*) AS edges
FROM edges_enriched
GROUP BY 1, 2, 3
ORDER BY edges DESC
LIMIT 25;
```

## Notes

Initial checks found that actual KGX counts match `graph-metadata.json`: `32,276` nodes and `1,861,988` edges. The archive has no duplicate node IDs or edge IDs and no dangling edge endpoints. The rendered notebook includes grouped summaries and quality checks by category.

