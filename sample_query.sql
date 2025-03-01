-- A sample query to get deps.jsonl from the BigQuery endpoint
WITH ranked_versions AS (
  SELECT
    name,
    version,
    summary,
    description,
    requires_dist,
    requires_python,
    author_email,
    home_page,
    project_urls,
    ROW_NUMBER() OVER (PARTITION BY name ORDER BY version DESC) AS rank
  FROM `bigquery-public-data.pypi.distribution_metadata`
  WHERE requires_dist IS NOT NULL
    AND summary IS NOT NULL
    AND requires_python IS NOT NULL
    AND home_page IS NOT NULL
    AND author_email IS NOT NULL
    AND project_urls IS NOT NULL
    AND description IS NOT NULL
    AND ARRAY_LENGTH(project_urls) > 1 -- 
)
SELECT
  name,
  requires_dist,
  requires_python
FROM ranked_versions
WHERE rank = 1;