CREATE OR REPLACE VIEW aqp_db.v_weather_latest AS
SELECT city, observation_ts, temperature_2m, relative_humidity_2m,
       precipitation, wind_speed_10m, ingested_at, dt
FROM (
  SELECT *,
         row_number() OVER (PARTITION BY city, observation_ts ORDER BY ingested_at DESC) AS rn
  FROM aqp_db.weather
)
WHERE rn = 1;