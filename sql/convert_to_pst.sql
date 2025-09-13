SELECT 
    FORMAT_DATETIME(
        '%Y-%m-%d %H:%M:%S', 
        TIMESTAMP_SECONDS(CAST(time / 1000000000 AS INT64)),
        'America/Los_Angeles' 
    ) AS time_pst, 
    * 
FROM `your-project.weather_dataset.weather_data` 
WHERE DATE(
    TIMESTAMP_SECONDS(CAST(time / 1000000000 AS INT64)),
    'America/Los_Angeles'
    ) = @run_date;