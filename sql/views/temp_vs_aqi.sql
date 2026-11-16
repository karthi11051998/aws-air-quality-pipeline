CREATE OR REPLACE VIEW aqp_db.v_temp_vs_aqi AS
SELECT city,
       CASE WHEN temperature_2m < 20 THEN '1 - Cool (under 20 C)'
            WHEN temperature_2m < 30 THEN '2 - Warm (20 to 30 C)'
            ELSE '3 - Hot (30 C or more)' END AS temp_band,
       count(*) AS hours,
       round(avg(us_aqi), 1) AS avg_us_aqi,
       round(avg(pm2_5), 1) AS avg_pm2_5
FROM aqp_db.v_city_hourly
WHERE us_aqi IS NOT NULL AND temperature_2m IS NOT NULL
GROUP BY 1, 2;