import pandas as pd
import numpy as np


REQUIRED_COLS = [
    "stat_date", "channel", "exposure", "click", "new_user",
    "active_user", "pay_user", "revenue", "channel_cost"
]
OPTIONAL_COLS = [
    "activated_user", "return_user_1d", "return_user_7d", "return_user_30d",
    "share_user", "share_new_user"
]


def clean_data(df):
    df = df.copy()
    df["stat_date"] = pd.to_datetime(df["stat_date"], errors="coerce")
    df = df[df["stat_date"].notna()]

    for col in ["exposure", "click", "new_user", "active_user", "pay_user",
                 "revenue", "channel_cost", "activated_user", "return_user_1d",
                 "return_user_7d", "return_user_30d", "share_user", "share_new_user"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df[(df["exposure"] > 0) & (df["channel_cost"] >= 0) & (df["revenue"] >= 0)]

    df["ctr"] = np.where(df["exposure"] > 0, df["click"] / df["exposure"] * 100, 0)
    df["cvr"] = np.where(df["click"] > 0, df["new_user"] / df["click"] * 100, 0)
    df["activation_rate"] = np.where(df["active_user"] > 0,
                                     df.get("activated_user", df["active_user"] * 0.8) / df["active_user"] * 100, 0)
    df["pay_rate"] = np.where(df["active_user"] > 0, df["pay_user"] / df["active_user"] * 100, 0)
    df["arppu"] = np.where(df["pay_user"] > 0, df["revenue"] / df["pay_user"], 0)
    df["arpu"] = np.where(df["active_user"] > 0, df["revenue"] / df["active_user"], 0)
    df["cac"] = np.where(df["new_user"] > 0, df["channel_cost"] / df["new_user"], 0)
    df["roi"] = np.where(df["channel_cost"] > 0, (df["revenue"] - df["channel_cost"]) / df["channel_cost"] * 100, np.nan)
    df["d1_retention"] = np.where(df["new_user"] > 0,
                                   df.get("return_user_1d", 0) / df["new_user"] * 100, 0)
    df["d7_retention"] = np.where(df["new_user"] > 0,
                                   df.get("return_user_7d", 0) / df["new_user"] * 100, 0)
    df["d30_retention"] = np.where(df["new_user"] > 0,
                                    df.get("return_user_30d", 0) / df["new_user"] * 100, 0)
    if "share_user" in df.columns and "share_new_user" in df.columns:
        df["share_rate"] = np.where(df["active_user"] > 0, df["share_user"] / df["active_user"] * 100, 0)
        df["share_k_factor"] = np.where(df["share_user"] > 0, df["share_new_user"] / df["share_user"], 0)
    else:
        df["share_rate"] = 0
        df["share_k_factor"] = 0

    return df


def get_overview_metrics(df):
    total_exposure = df["exposure"].sum()
    total_click = df["click"].sum()
    total_new = df["new_user"].sum()
    total_active = df["active_user"].sum()
    total_pay = df["pay_user"].sum()
    total_revenue = df["revenue"].sum()
    total_cost = df["channel_cost"].sum()

    d1_avg = df[df["new_user"] > 0]["d1_retention"].mean()
    d7_avg = df[df["new_user"] > 0]["d7_retention"].mean()
    d30_avg = df[df["new_user"] > 0]["d30_retention"].mean()
    roi = (total_revenue - total_cost) / total_cost * 100 if total_cost > 0 else 0
    arpu = total_revenue / max(1, total_active)
    pay_rate = total_pay / max(1, total_active) * 100

    return {
        "total_exposure": int(total_exposure),
        "total_click": int(total_click),
        "total_new_user": int(total_new),
        "total_active": int(total_active),
        "total_pay": int(total_pay),
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "ctr": round(total_click / total_exposure * 100, 2),
        "cvr": round(total_new / total_click * 100, 2),
        "activation_rate": round(df["activation_rate"].mean(), 2),
        "d1_retention": round(d1_avg, 2),
        "d7_retention": round(d7_avg, 2),
        "d30_retention": round(d30_avg, 2),
        "pay_rate": round(pay_rate, 2),
        "arppu": round(total_revenue / max(1, total_pay), 2),
        "arpu": round(arpu, 2),
        "cac": round(total_cost / max(1, total_new), 2),
        "roi": round(roi, 2),
        "total_profit": round(total_revenue - total_cost, 2),
    }


def get_funnel_data(df):
    return pd.DataFrame([
        {"stage": "曝光(Acquisition)", "users": int(df["exposure"].sum()), "color": "#FF6B6B"},
        {"stage": "点击", "users": int(df["click"].sum()), "color": "#FF8E72"},
        {"stage": "新增用户", "users": int(df["new_user"].sum()), "color": "#FFD93D"},
        {"stage": "激活(Activation)", "users": int(df.get("activated_user", df["active_user"] * 0.8).sum()), "color": "#6BCB77"},
        {"stage": "留存(Retention)", "users": int(df.get("return_user_7d", 0).sum()), "color": "#4D96FF"},
        {"stage": "付费(Revenue)", "users": int(df["pay_user"].sum()), "color": "#9B59B6"},
        {"stage": "分享(Referral)", "users": int(df.get("share_new_user", 0).sum()), "color": "#E74C3C"},
    ])


def get_daily_trend(df):
    daily = df.groupby("stat_date").agg(
        exposure=("exposure", "sum"),
        click=("click", "sum"),
        new_user=("new_user", "sum"),
        active_user=("active_user", "sum"),
        pay_user=("pay_user", "sum"),
        revenue=("revenue", "sum"),
        channel_cost=("channel_cost", "sum"),
    ).reset_index()
    daily["ctr"] = daily["click"] / daily["exposure"] * 100
    daily["cvr"] = daily["new_user"] / daily["click"].replace(0, 1) * 100
    daily["roi"] = (daily["revenue"] - daily["channel_cost"]) / daily["channel_cost"].replace(0, 1) * 100
    daily["profit"] = daily["revenue"] - daily["channel_cost"]
    return daily


def get_channel_analysis(df):
    ch = df.groupby("channel").agg(
        exposure=("exposure", "sum"),
        click=("click", "sum"),
        new_user=("new_user", "sum"),
        active_user=("active_user", "sum"),
        pay_user=("pay_user", "sum"),
        revenue=("revenue", "sum"),
        channel_cost=("channel_cost", "sum"),
    ).reset_index()
    ch["ctr"] = (ch["click"] / ch["exposure"] * 100).round(2)
    ch["cvr"] = (ch["new_user"] / ch["click"].replace(0, 1) * 100).round(2)
    ch["cac"] = (ch["channel_cost"] / ch["new_user"].replace(0, 1)).round(2)
    ch["arpu"] = (ch["revenue"] / ch["active_user"].replace(0, 1)).round(2)
    ch["pay_rate"] = (ch["pay_user"] / ch["active_user"].replace(0, 1) * 100).round(2)
    ch["roi"] = ((ch["revenue"] - ch["channel_cost"]) / ch["channel_cost"].replace(0, 1) * 100).round(2)
    ch["profit"] = (ch["revenue"] - ch["channel_cost"]).round(2)
    ch = ch.sort_values("revenue", ascending=False)
    return ch


def get_retention_trend(df):
    daily_ret = df.groupby("stat_date").agg(
        new_user=("new_user", "sum"),
        return_1d=("return_user_1d", "sum"),
        return_7d=("return_user_7d", "sum"),
        return_30d=("return_user_30d", "sum"),
    ).reset_index()
    daily_ret["d1"] = (daily_ret["return_1d"] / daily_ret["new_user"].replace(0, 1) * 100).round(2)
    daily_ret["d7"] = (daily_ret["return_7d"] / daily_ret["new_user"].replace(0, 1) * 100).round(2)
    daily_ret["d30"] = (daily_ret["return_30d"] / daily_ret["new_user"].replace(0, 1) * 100).round(2)
    return daily_ret


def get_revenue_trend(df):
    rev = df.groupby("stat_date").agg(
        revenue=("revenue", "sum"),
        pay_user=("pay_user", "sum"),
        new_user=("new_user", "sum"),
        channel_cost=("channel_cost", "sum"),
    ).reset_index()
    rev["arppu"] = (rev["revenue"] / rev["pay_user"].replace(0, 1)).round(2)
    rev["pay_rate"] = (rev["pay_user"] / rev.groupby("stat_date")["active_user"].transform("sum") * 100 if "active_user" in df.columns else 0)
    rev["profit"] = rev["revenue"] - rev["channel_cost"]
    return rev


def get_referral_analysis(df):
    ref = df.groupby("channel").agg(
        share_user=("share_user", "sum"),
        share_new_user=("share_new_user", "sum"),
        new_user=("new_user", "sum"),
        active_user=("active_user", "sum"),
    ).reset_index()
    ref["share_rate"] = (ref["share_user"] / ref["active_user"].replace(0, 1) * 100).round(2)
    ref["k_factor"] = (ref["share_new_user"] / ref["share_user"].replace(0, 1)).round(3)
    ref["viral_contribution"] = (ref["share_new_user"] / ref["new_user"].replace(0, 1) * 100).round(2)
    return ref


def auto_insights(metrics, df):
    insights = []
    if metrics["roi"] < 50:
        insights.append(f"⚠️ 整体ROI仅{metrics['roi']}%，低于行业健康线(100%)，建议优化高CAC渠道。")
    else:
        insights.append(f"✅ 整体ROI为{metrics['roi']}%，处于健康水平。")

    if metrics["d7_retention"] < 20:
        insights.append(f"⚠️ 7日留存率仅{metrics['d7_retention']}%，低于行业基准(25%)，需加强新手引导和核心功能触达。")
    else:
        insights.append(f"✅ 7日留存率为{metrics['d7_retention']}%，表现良好。")

    ch = get_channel_analysis(df)
    if len(ch) > 0:
        best_ch = ch.loc[ch["roi"].idxmax()]
        worst_ch = ch.loc[ch["roi"].idxmin()]
        insights.append(f"📈 最优渠道：**{best_ch['channel']}**，ROI {best_ch['roi']}%，CAC ¥{best_ch['cac']}，建议加大预算。")
        if worst_ch["roi"] < 0:
            insights.append(f"📉 亏损渠道：**{worst_ch['channel']}**，ROI {worst_ch['roi']}%，建议暂停或优化投放策略。")

    if metrics["pay_rate"] < 10:
        insights.append(f"⚠️ 付费转化率仅{metrics['pay_rate']}%，可优化付费点设计或推出限时优惠活动。")

    daily = get_daily_trend(df)
    if len(daily) >= 14:
        dau_trend = daily["active_user"].tail(7).mean() / daily["active_user"].tail(14).head(7).mean()
        if dau_trend > 1.05:
            insights.append(f"📈 DAU近7日较前7日增长{(dau_trend-1)*100:.1f}%，增长势头良好。")
        elif dau_trend < 0.95:
            insights.append(f"📉 DAU近7日较前7日下降{(1-dau_trend)*100:.1f}%，需关注用户流失问题。")

    return insights
