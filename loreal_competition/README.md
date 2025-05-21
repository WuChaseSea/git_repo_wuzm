# 数据化分析工具

## 数据分析

## Agent功能拆分

根据常理分析，用户可能存在的数据分析动作有：

* 趋势分析
plot_trend(data, column, time_col, period)

1）支持查询不同属性随日期的变化；
例如：
帮我分析2024年上半年每日销售额的变化情况；

2）支持按照一种属性查找另一种属性；
例如：
请统计不同品牌的销售额分布并用柱状图展示
分析各商品类型的订单数量，生成饼图

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
