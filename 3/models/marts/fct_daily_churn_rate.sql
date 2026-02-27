-- models/marts/fct_daily_churn_rate.sql

/* 
   dbt Mart Model: SaaS Customer Analytics
   Business Goal: Track churn trends, revenue impact, and growth metrics over a 30-day window.
*/

-- CTE to pull clean data from intermediate layer
with customer_data as (
    select * 
    from {{ ref('int_customer_orders') }}
),

-- Aggregate data by day to calculate SaaS-specific metrics
daily_metrics as (
    select
        -- Granularity: Daily periods
        date_trunc('day', order_date) as report_date,
        
        -- Customer Metrics
        count(distinct customer_id) as active_customers,
        sum(case when status = 'cancelled' then 1 else 0 end) as churned_customers,
        sum(case when status = 'new' then 1 else 0 end) as new_customers,
        
        -- Revenue Metrics (Assuming 'order_value' represents MRR/Revenue)
        sum(order_value) as total_revenue,
        sum(case when status = 'cancelled' then order_value else 0 end) as churned_revenue

    from customer_data
    
    -- Business requirement: Analyze trends over the last 30 days
    where order_date >= current_date - interval '30 days'
    
    group by 1
),

-- Final calculations for Rates and ARPU
final_marts as (
    select
        report_date,
        active_customers,
        new_customers,
        churned_customers,
        total_revenue,
        churned_revenue,
        
        -- SaaS Metric: Churn Rate (%)
        round(
            cast(churned_customers as numeric) / nullif(active_customers, 0), 
            4
        ) as churn_rate,

        -- SaaS Metric: ARPU (Average Revenue Per User)
        round(
            cast(total_revenue as numeric) / nullif(active_customers, 0),
            2
        ) as arpu,

        -- SaaS Metric: Net Customer Growth
        (new_customers - churned_customers) as net_customer_growth

    from daily_metrics
)

-- Ordered chronologically for easy consumption by BI tools (dashboards)
select * from final_marts
order by report_date desc
