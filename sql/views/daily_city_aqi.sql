# Question 1: which cities had unhealthy air most often?

CREATE OR REPLACE VIEW aqp_db.v_daily_city_aqi AS
SELECT city,
       date(observation_ts) AS obs_date,
       round(avg(us_aqi), 1) AS avg_us_aqi,
       max(us_aqi) AS max_us_aqi,
       round(avg(pm2_5), 1) AS avg_pm2_5,
       count_if(us_aqi > 100) AS hours_aqi_above_100,
       count(us_aqi) AS hours_measured,
       round(100.0 * count_if(us_aqi > 100) / nullif(count(us_aqi), 0), 1) AS pct_hours_above_100
FROM aqp_db.v_air_quality_latest
GROUP BY city, date(observation_ts);