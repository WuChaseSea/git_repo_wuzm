# 数据化分析工具

## 数据分析

## Agent功能拆分

根据常理分析，用户可能存在的数据分析动作有：

* 趋势分析
plot_trend(data, column, time_col, period)

* 分组统计
group_by_and_agg(data, group_col, agg_col, method)

* 时间段筛选
filter_by_time(data, start, end)

* Top-N 排名
get_top_n(data, group_col, target_col, n)

* 可视化图表
generate_bar_chart(...) / generate_line_chart(...)

* 自动洞察
auto_insight_summary(data)
