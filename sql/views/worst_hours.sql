# Question 2: which hours are riskiest for outdoor deliveries?

CREATE OR REPLACE VIEW aqp_db.v_worst_hours AS
SELECT city,
       hour(observation_ts) AS hour_of_day,
       round(avg(us_aqi), 1) AS avg_us_aqi,
       round(avg(pm2_5), 1) AS avg_pm2_5,
       count(us_aqi) AS observations,
       round(100.0 * count_if(us_aqi > 100) / nullif(count(us_aqi), 0), 1) AS pct_hours_above_100
FROM aqp_db.v_air_quality_latest
GROUP BY city, hour(observation_ts);