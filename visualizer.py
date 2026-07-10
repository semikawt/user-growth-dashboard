import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


CHART_THEME = "plotly_white"
COLORS = px.colors.qualitative.Set2


def plot_aarrr_funnel(funnel_df):
    fig = go.Figure(go.Funnel(
        y=funnel_df["stage"],
        x=funnel_df["users"],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=funnel_df["color"]),
        connector=dict(line=dict(color="#ddd", width=1))
    ))
    fig.update_layout(
        title="AARRR 全链路转化漏斗",
        height=450,
        template=CHART_THEME,
        margin=dict(t=50, b=30)
    )
    return fig


def plot_daily_active_trend(daily_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=daily_df["stat_date"], y=daily_df["active_user"],
                   name="DAU", line=dict(color="#4D96FF", width=2.5), fill="tozeroy", opacity=0.2),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=daily_df["stat_date"], y=daily_df["new_user"],
                   name="新增用户", line=dict(color="#FF6B6B", width=2, dash="dot")),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=daily_df["stat_date"], y=daily_df["roi"],
                   name="ROI(%)", line=dict(color="#6BCB77", width=2), opacity=0.7),
        secondary_y=True
    )
    fig.update_layout(
        title="DAU / 新增用户 / ROI 日趋势",
        height=380, template=CHART_THEME,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=30)
    )
    fig.update_yaxes(title_text="用户数", secondary_y=False)
    fig.update_yaxes(title_text="ROI (%)", secondary_y=True)
    return fig


def plot_channel_roi_bar(channel_df):
    ch = channel_df.sort_values("roi", ascending=True)
    colors = ["#FF6B6B" if x < 0 else "#6BCB77" if x > 100 else "#FFD93D" for x in ch["roi"]]
    fig = go.Figure(go.Bar(
        x=ch["roi"], y=ch["channel"], orientation="h",
        marker_color=colors, text=ch["roi"].round(1).astype(str) + "%", textposition="outside"
    ))
    fig.update_layout(
        title="各渠道 ROI 对比（%）", height=380,
        template=CHART_THEME, margin=dict(t=50, b=30, l=10, r=60)
    )
    fig.add_vline(x=100, line_dash="dash", line_color="#999", annotation_text="盈亏平衡线(100%)")
    return fig


def plot_channel_cac_vs_arpu(channel_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=channel_df["channel"], y=channel_df["cac"], name="CAC 获客成本",
        marker_color="#FF6B6B", opacity=0.7
    ))
    fig.add_trace(go.Bar(
        x=channel_df["channel"], y=channel_df["arpu"], name="ARPU 单用户收益",
        marker_color="#6BCB77", opacity=0.7
    ))
    fig.update_layout(
        title="渠道 CAC vs ARPU 对比", barmode="group", height=380,
        template=CHART_THEME, legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=30)
    )
    return fig


def plot_retention_curves(ret_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ret_df["stat_date"], y=ret_df["d1"],
                             name="次日留存(D1)", line=dict(color="#FF6B6B", width=2)))
    fig.add_trace(go.Scatter(x=ret_df["stat_date"], y=ret_df["d7"],
                             name="7日留存(D7)", line=dict(color="#4D96FF", width=2)))
    fig.add_trace(go.Scatter(x=ret_df["stat_date"], y=ret_df["d30"],
                             name="30日留存(D30)", line=dict(color="#9B59B6", width=2)))
    fig.update_layout(
        title="留存率趋势（%）", height=380, template=CHART_THEME,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=30), yaxis_title="留存率(%)"
    )
    return fig


def plot_channel_retention_heatmap(df):
    ch_ret = df.groupby("channel").agg(
        d1=("d1_retention", "mean"),
        d7=("d7_retention", "mean"),
        d30=("d30_retention", "mean"),
    ).round(2).reset_index()
    data_matrix = ch_ret[["d1", "d7", "d30"]].values
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=["D1 次日留存", "D7 周留存", "D30 月留存"],
        y=ch_ret["channel"],
        colorscale="YlGnBu",
        text=data_matrix, texttemplate="%{text:.1f}%", textfont={"size": 12},
        colorbar=dict(title="留存率(%)")
    ))
    fig.update_layout(
        title="各渠道留存率热力图", height=380,
        template=CHART_THEME, margin=dict(t=50, b=30)
    )
    return fig


def plot_revenue_trend(daily_df):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=daily_df["stat_date"], y=daily_df["revenue"], name="营收",
        marker_color="#4D96FF", opacity=0.7
    ), secondary_y=False)
    fig.add_trace(go.Bar(
        x=daily_df["stat_date"], y=daily_df["channel_cost"], name="投放成本",
        marker_color="#FF6B6B", opacity=0.5
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=daily_df["stat_date"], y=daily_df["profit"], name="净利润",
        line=dict(color="#6BCB77", width=2.5)
    ), secondary_y=True)
    fig.update_layout(
        title="营收 / 成本 / 利润趋势",
        height=380, template=CHART_THEME, barmode="overlay",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=30)
    )
    fig.update_yaxes(title_text="金额(¥)", secondary_y=False)
    fig.update_yaxes(title_text="净利润(¥)", secondary_y=True)
    return fig


def plot_pay_metrics(df):
    daily_pay = df.groupby("stat_date").agg(
        pay_rate=("pay_rate", "mean"),
        arppu=("arppu", "mean")
    ).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=daily_pay["stat_date"], y=daily_pay["pay_rate"],
        name="付费转化率(%)", line=dict(color="#FFD93D", width=2.5), fill="tozeroy", opacity=0.2
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=daily_pay["stat_date"], y=daily_pay["arppu"],
        name="ARPPU(¥)", line=dict(color="#FF8E72", width=2)
    ), secondary_y=True)
    fig.update_layout(
        title="付费转化率 & ARPPU 趋势", height=380, template=CHART_THEME,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60, b=30)
    )
    return fig


def plot_referral_analysis(ref_df):
    fig = make_subplots(rows=1, cols=2, subplot_titles=("各渠道分享率(%)", "K因子(病毒系数)"))

    fig.add_trace(go.Bar(
        x=ref_df["channel"], y=ref_df["share_rate"],
        marker_color=COLORS[:len(ref_df)], showlegend=False
    ), row=1, col=1)

    kf = ref_df.sort_values("k_factor", ascending=True)
    colors_k = ["#6BCB77" if x >= 0.2 else "#FFD93D" if x >= 0.1 else "#FF6B6B" for x in kf["k_factor"]]
    fig.add_trace(go.Bar(
        x=kf["k_factor"], y=kf["channel"], orientation="h",
        marker_color=colors_k, showlegend=False,
        text=kf["k_factor"].round(3), textposition="outside"
    ), row=1, col=2)

    fig.update_layout(
        title="裂变传播分析", height=380, template=CHART_THEME,
        margin=dict(t=60, b=30)
    )
    fig.add_vline(x=1, line_dash="dash", line_color="red",
                  annotation_text="病毒传播临界线(K=1)", row=1, col=2)
    return fig


def plot_channel_conversion_funnel(channel_df):
    ch_top = channel_df.nlargest(4, "new_user")
    fig = go.Figure()
    for i, (_, row) in enumerate(ch_top.iterrows()):
        fig.add_trace(go.Funnel(
            name=row["channel"],
            y=["曝光", "点击", "新增", "付费"],
            x=[row["exposure"], row["click"], row["new_user"], row["pay_user"]],
            textinfo="value+percent initial",
            opacity=0.75
        ))
    fig.update_layout(
        title="TOP4渠道转化漏斗对比", height=420, template=CHART_THEME,
        margin=dict(t=50, b=30)
    )
    return fig
