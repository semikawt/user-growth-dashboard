import numpy as np
import pandas as pd
from datetime import datetime, timedelta


CHANNELS = ["短视频信息流", "搜索引擎", "社群裂变", "应用商店", "KOL推广", "信息流广告", "自然流量"]
CHANNEL_WEIGHTS = [0.25, 0.18, 0.15, 0.12, 0.12, 0.10, 0.08]
CHANNEL_BASE_CAC = {"短视频信息流": 8, "搜索引擎": 12, "社群裂变": 3, "应用商店": 0, "KOL推广": 15, "信息流广告": 10, "自然流量": 0}
CHANNEL_BASE_CTR = {"短视频信息流": 0.085, "搜索引擎": 0.060, "社群裂变": 0.130, "应用商店": 0.150, "KOL推广": 0.070, "信息流广告": 0.080, "自然流量": 0.040}
CHANNEL_BASE_CVR = {"短视频信息流": 0.20, "搜索引擎": 0.25, "社群裂变": 0.30, "应用商店": 0.28, "KOL推广": 0.18, "信息流广告": 0.22, "自然流量": 0.15}
CHANNEL_RETENTION_FACTOR = {"短视频信息流": 0.85, "搜索引擎": 1.0, "社群裂变": 1.10, "应用商店": 1.05, "KOL推广": 0.90, "信息流广告": 0.80, "自然流量": 1.15}
CHANNEL_PAY_RATE = {"短视频信息流": 0.12, "搜索引擎": 0.15, "社群裂变": 0.18, "应用商店": 0.14, "KOL推广": 0.10, "信息流广告": 0.11, "自然流量": 0.16}


def generate_daily_data(days=90, seed=42):
    rng = np.random.default_rng(seed)
    end_date = datetime(2026, 6, 30)
    start_date = end_date - timedelta(days=days - 1)

    base_exposure = 30000
    records = []

    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5
        seasonal_factor = 1.0 + 0.3 * np.sin(day_offset / 14 * np.pi)
        trend_growth = 1.0 + day_offset * 0.003

        for ch in CHANNELS:
            ch_idx = CHANNELS.index(ch)
            ch_exp_base = base_exposure * CHANNEL_WEIGHTS[ch_idx] * seasonal_factor * trend_growth
            ch_exposure = int(rng.normal(ch_exp_base, ch_exp_base * 0.12))
            ch_exposure = max(1000, ch_exposure)

            ctr = CHANNEL_BASE_CTR[ch] * rng.normal(1.0, 0.08)
            ctr = max(0.02, min(ctr, 0.25))
            ch_click = int(ch_exposure * ctr)

            cvr = CHANNEL_BASE_CVR[ch] * rng.normal(1.0, 0.10) * (0.9 if is_weekend else 1.0)
            cvr = max(0.08, min(cvr, 0.40))
            ch_new_user = int(ch_click * cvr)

            daily_active_base = ch_new_user * (1 + rng.uniform(1.5, 3.0))
            ch_active = int(daily_active_base * seasonal_factor)

            activation_rate = rng.uniform(0.65, 0.90)
            ch_activated = int(ch_active * activation_rate)

            ret_factor = CHANNEL_RETENTION_FACTOR[ch]
            d1_rate = 0.42 * ret_factor * rng.normal(1.0, 0.05)
            d7_rate = 0.22 * ret_factor * rng.normal(1.0, 0.06)
            d30_rate = 0.10 * ret_factor * rng.normal(1.0, 0.08)
            ch_return_1d = int(ch_new_user * d1_rate)
            ch_return_7d = int(ch_new_user * d7_rate)
            ch_return_30d = int(ch_new_user * d30_rate)

            pay_rate = CHANNEL_PAY_RATE[ch] * rng.normal(1.0, 0.10)
            pay_rate = max(0.05, min(pay_rate, 0.30))
            ch_pay_user = int(ch_active * pay_rate)

            arppu = rng.lognormal(3.5, 0.6) * (1.2 if ch == "KOL推广" else 1.0)
            ch_revenue = round(ch_pay_user * arppu, 2)

            share_rate = rng.uniform(0.08, 0.20) * ret_factor
            ch_share_user = int(ch_active * share_rate)
            share_conv = rng.uniform(0.15, 0.35)
            ch_share_new = int(ch_share_user * share_conv)

            cac = CHANNEL_BASE_CAC[ch]
            if ch == "自然流量" or ch == "应用商店":
                ch_cost = round(rng.uniform(0, 200), 2)
            else:
                daily_cost = ch_new_user * cac * rng.normal(1.0, 0.15)
                ch_cost = round(max(0, daily_cost), 2)

            noise = rng.normal(0, ch_exposure * 0.01)
            ch_exposure = int(ch_exposure + noise)

            records.append({
                "stat_date": current_date.strftime("%Y-%m-%d"),
                "channel": ch,
                "exposure": ch_exposure,
                "click": ch_click,
                "new_user": ch_new_user,
                "active_user": ch_active,
                "activated_user": ch_activated,
                "return_user_1d": ch_return_1d,
                "return_user_7d": ch_return_7d,
                "return_user_30d": ch_return_30d,
                "pay_user": ch_pay_user,
                "revenue": ch_revenue,
                "share_user": ch_share_user,
                "share_new_user": ch_share_new,
                "channel_cost": ch_cost,
            })

    return pd.DataFrame(records)


def save_parquet(df, path):
    df.to_parquet(path, index=False)


def export_csv(df, path):
    df.to_csv(path, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    df = generate_daily_data(90, seed=42)
    print(f"生成数据: {len(df)} 条记录, {df['stat_date'].nunique()} 天, {df['channel'].nunique()} 个渠道")
    print(df.head(3).to_string())
