WITH vl_map AS 
(
    /* [DASH] VL -> region/AM map (analytics.am_vl). Small dim table for region rollups. */
    SELECT toString(mitra_id) AS vl_id,
           anyHeavy(cluster) AS region,
           anyHeavy(am_name) AS am_name
    FROM analytics.am_vl
    GROUP BY mitra_id
),

cte AS
(
    SELECT user_id,
           co."phone_number",
           JSON_VALUE(co.ujf_meta_data,'$.candidateRegisteredUid') AS candidateRegisteredUid,
           co."product_source" AS lead_referral_type,
           company_name,
           JSON_VALUE(co.ujf_meta_data, '$.jobCity') AS jobCity,
           CASE WHEN mitras."managerMitraID" IS NULL THEN mitras."name" ELSE mitras1."name" END AS mitra_name,
           -- DERIVED ID: Matching the logic used for mitra_name to ensure correct mapping
           toString(CASE WHEN mitras."managerMitraID" IS NULL THEN mitras."id" ELSE mitras1."id" END) AS resolved_mitra_id,
           JSON_VALUE(co.ujf_meta_data,'$.workLocality') AS workLocality,
           JSON_VALUE(co.ujf_meta_data,'$.jobCityZone') AS job_city_zone,
           co."source" AS lead_source,
           referral_date_si AS referral_date_si,
           toDate(marked_unique) AS marked_unique,
           toDate(activation_date) AS activation_date,
           toDate(first_date_of_work) AS first_date_of_work,
           toDate("5th_order_date") AS "5th_order_date",
           toDate("10th_order_date") AS "10th_order_date",
           toDate("20th_order_date") AS "20th_order_date",
           toDate("30th_order_date") AS "30th_order_date",
           toDate("50th_order_date") AS "50th_order_date",
           toDate("60th_order_date") AS "60th_order_date",
           toDate("80th_order_date") AS "80th_order_date",
           toDate("100th_order_date") AS "100th_order_date",
           toDate("120th_order_date") AS "120th_order_date",
           toDate("150th_order_date") AS "150th_order_date",
           toDate("200th_order_date") AS "200th_order_date",
           candidate_lifetime_orders_trips
    FROM jobfinder.candidates_olap co 
    LEFT JOIN jobfinder.mitras ON mitras."id" = co."si_source_id"
    LEFT JOIN jobfinder.mitras AS mitras1 ON mitras1."id" = mitras."managerMitraID"
    WHERE toDate(first_date_of_work) BETWEEN today() - 70 AND today() - 1
      AND lower(company_name) IN ({{ Client }})
)

SELECT c."phone_number",
       c.candidateRegisteredUid,
       c.lead_source,
       c.lead_referral_type,
       c.company_name,
       c.jobCity,
       c.mitra_name AS vl_name,
       m.region,
       m.am_name,
       c.referral_date_si,
       c.marked_unique,
       c.activation_date,
       c.first_date_of_work,
       c."5th_order_date",
       c."10th_order_date",
       c."20th_order_date",
       c."30th_order_date",
       c."50th_order_date",
       c."60th_order_date",
       c."80th_order_date",
       c."100th_order_date",
       c."120th_order_date",
       c."150th_order_date",
       c."200th_order_date",
       c.candidate_lifetime_orders_trips
FROM cte c
LEFT JOIN vl_map m ON c.resolved_mitra_id = m.vl_id;
