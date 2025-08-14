
-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS misinfo_analytics;

-- External table over Parquet data lake (partitioned by dt)
CREATE EXTERNAL TABLE IF NOT EXISTS misinfo_analytics.twitter_clean (
  id    string,
  text  string,
  label int
)
PARTITIONED BY (dt string)
STORED AS PARQUET
LOCATION 's3://YOUR_BUCKET/clean/twitter/'
TBLPROPERTIES ('parquet.compress'='SNAPPY');

-- Option A: Let Glue Crawler discover partitions (recommended)
-- Or Option B: Add a partition explicitly (example for one dt)
ALTER TABLE misinfo_analytics.twitter_clean
ADD IF NOT EXISTS PARTITION (dt='2025-08-12')
LOCATION 's3://YOUR_BUCKET/clean/twitter/dt=2025-08-12/';

-- After writing more days, repair partitions in Athena:
MSCK REPAIR TABLE misinfo_analytics.twitter_clean;



-- Basic row counts
SELECT COUNT(*) AS total_rows FROM misinfo_analytics.twitter_clean;
SELECT dt, COUNT(*) AS rows_per_day FROM misinfo_analytics.twitter_clean GROUP BY dt ORDER BY dt;

-- Label distribution overall and per day
SELECT label, COUNT(*) AS n FROM misinfo_analytics.twitter_clean GROUP BY label ORDER BY n DESC;
SELECT dt, label, COUNT(*) AS n FROM misinfo_analytics.twitter_clean GROUP BY dt, label ORDER BY dt, label;

-- Simple text length stats (needs a UDF or length on text)
SELECT dt, AVG(LENGTH(text)) AS avg_len FROM misinfo_analytics.twitter_clean GROUP BY dt ORDER BY dt;
