drop table if exists summary_funnel_mediumrevenue;
create table if not exists summary_funnel_mediumrevenue as select medium, avg(totalTransactionRevenue) as avg_totalTransactionRevenue from hive_funnel group by medium order by avg_totalTransactionRevenue desc;
