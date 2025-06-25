-- Campaign Performance Query - Raw Data Only
-- Working query with correct column names, filtered for attribution data

SELECT 
    cpt.unique_key,
    cpt.client,
    cpt.product,
    cpt.market,
    cpt.station,
    cbd.cdaypart AS daypart,
    cpt.dtspot,
    cpt.buyrate AS spot_cost,
    
    -- Attribution metrics (raw data only)
    lam.online_revenue,
    lam.online_visits,
    lam.online_orders,
    lam.online_leads,
    lam.impressions

FROM core_post_time cpt
INNER JOIN linear_attribution_metrics lam ON cpt.unique_key = lam.unique_key
INNER JOIN core_buy_detail cbd ON cbd.nbuydetid = cpt.buydetid
    
WHERE cpt.dtspot >= NOW() - INTERVAL '%s days'
    AND lam.online_visits IS NOT NULL
    AND CAST(lam.online_visits AS TEXT) != 'NULL'
    
ORDER BY cpt.dtspot DESC