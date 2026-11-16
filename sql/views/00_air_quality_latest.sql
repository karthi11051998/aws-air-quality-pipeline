CREATE OR REPLACE VIEW aqp_db.v_air_quality_latest AS
SELECT city, latitude, longitude, observation_ts,
       pm2_5, pm10, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone,
       us_aqi, aqi_category, ingested_at, dt
FROM (
  SELECT *,
         row_number() OVER (PARTITION BY city, observation_ts ORDER BY ingested_at DESC) AS rn
  FROM aqp_db.air_quality
)
WHERE rn = 1;