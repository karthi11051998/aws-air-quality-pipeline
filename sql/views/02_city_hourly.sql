# air quality and weather joined, one row per city per hour

CREATE OR REPLACE VIEW aqp_db.v_city_hourly AS
SELECT a.city, a.observation_ts,
       a.pm2_5, a.pm10, a.nitrogen_dioxide, a.ozone, a.us_aqi, a.aqi_category,
       w.temperature_2m, w.relative_humidity_2m, w.precipitation, w.wind_speed_10m
FROM aqp_db.v_air_quality_latest a
JOIN aqp_db.v_weather_latest w
  ON a.city = w.city AND a.observation_ts = w.observation_ts;