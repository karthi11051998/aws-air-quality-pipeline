# Question 3: how do rain and temperature relate to AQI?

CREATE OR REPLACE VIEW aqp_db.v_rain_vs_aqi AS
SELECT city,
       CASE WHEN precipitation = 0 THEN '1 - No rain'
            WHEN precipitation < 1 THEN '2 - Light (under 1 mm/h)'
            ELSE '3 - Moderate or heavy (1 mm/h or more)' END AS rain_bucket,
       count(*) AS hours,
       round(avg(us_aqi), 1) AS avg_us_aqi,
       round(avg(pm2_5), 1) AS avg_pm2_5
FROM aqp_db.v_city_hourly
WHERE us_aqi IS NOT NULL AND precipitation IS NOT NULL
GROUP BY 1, 2;