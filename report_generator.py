from datetime import datetime


def generate_report(metrics, channel_df, daily_trend, insights, ai_diag="", ai_plan=""):
    date_range = f"{daily_trend['stat_date'].min().strftime('%Y-%m-%d')} ~ {daily_trend['stat_date'].max().strftime('%Y-%m-%d')}"

    ch_table = "| 渠道 | 曝光量 | 点击量 | 新增用户 | 付费用户 | 营收(¥) | 成本(¥) | CTR(%) | CVR(%) | CAC(¥) | ROI(%) | 利润(¥) |\n"
    ch_table += "|------|--------|--------|----------|----------|---------|---------|--------|--------|--------|--------|--------|\n"
    for _, row in channel_df.iterrows():
        ch_table += (
            f"| {row['channel']} | {int(row['exposure']):,} | {int(row['click']):,} | {int(row['new_user']):,} | "
            f"{int(row['pay_user']):,} | {row['revenue']:,.2f} | {row['channel_cost']:,.2f} | "
            f"{row['ctr']:.2f} | {row['cvr']:.2f} | {row['cac']:.2f} | {row['roi']:.1f} | {row['profit']:,.2f} |\n"
        )

    insight_md = "\n".join([f"- {ins}" for ins in insights])

    md = f"""# 📊 用户增长运营分析报告

> 报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}  
> 数据周期：{date_range}

---

## 一、大盘总览

| 指标 | 数值 | 指标 | 数值 |
|------|------|------|------|
| 总曝光量 | {metrics['total_exposure']:,} | 总点击量 | {metrics['total_click']:,} |
| 总新增用户 | {metrics['total_new_user']:,} | 总活跃用户 | {metrics['total_active']:,} |
| 总付费用户 | {metrics['total_pay']:,} | 总营收 | ¥{metrics['total_revenue']:,.2f} |
| 总投放成本 | ¥{metrics['total_cost']:,.2f} | 净利润 | ¥{metrics['total_profit']:,.2f} |
| 点击率(CTR) | {metrics['ctr']}% | 注册转化率(CVR) | {metrics['cvr']}% |
| 获客成本(CAC) | ¥{metrics['cac']} | 单用户收益(ARPU) | ¥{metrics['arpu']} |
| 付费用户均消(ARPPU) | ¥{metrics['arppu']} | 付费转化率 | {metrics['pay_rate']}% |
| 次日留存(D1) | {metrics['d1_retention']}% | 7日留存(D7) | {metrics['d7_retention']}% |
| 30日留存(D30) | {metrics['d30_retention']}% | 整体ROI | {metrics['roi']}% |

---

## 二、关键洞察

{insight_md}

---

## 三、渠道效果分析

{ch_table}

### 渠道结论

"""
    if len(channel_df) > 0:
        best = channel_df.loc[channel_df["roi"].idxmax()]
        worst = channel_df.loc[channel_df["roi"].idxmin()]
        md += f"- **最优渠道**：{best['channel']}，ROI {best['roi']}%，建议重点追加预算。\n"
        if worst["roi"] < 100:
            md += f"- **需优化渠道**：{worst['channel']}，ROI {worst['roi']}%，建议优化投放素材或缩减预算。\n"
        low_cac = channel_df.loc[channel_df["cac"].idxmin()]
        if low_cac["roi"] > 50:
            md += f"- **低成本渠道**：{low_cac['channel']}，CAC仅¥{low_cac['cac']}，可作为规模化放量首选。\n"

    md += f"""
---

## 四、留存分析

- D1次日留存：{metrics['d1_retention']}%（行业基准35-45%）
- D7周留存：{metrics['d7_retention']}%（行业基准20-30%）
- D30月留存：{metrics['d30_retention']}%（行业基准8-15%）

---

## 五、变现分析

- 总营收：¥{metrics['total_revenue']:,.2f}
- 付费用户数：{metrics['total_pay']:,}人
- 付费转化率：{metrics['pay_rate']}%
- ARPPU（付费用户均消）：¥{metrics['arppu']}

---
"""

    if ai_diag:
        md += f"\n## 六、AI 智能诊断\n\n{ai_diag}\n\n---\n"
    if ai_plan:
        md += f"\n## 七、AI 增长活动方案\n\n{ai_plan}\n\n---\n"

    md += f"\n> 本报告由 UserGrowthDashboard 自动生成 | AARRR 用户增长运营看板"
    return md
