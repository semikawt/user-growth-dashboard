import pandas as pd
import numpy as np
from io import StringIO


COLUMN_MAPPING = {
    "stat_date": ["日期", "统计日期", "date", "时间", "stat_date", "dt", "统计时间", "day"],
    "channel": ["渠道", "渠道名称", "channel", "来源", "获客渠道", "投放渠道", "媒体"],
    "exposure": ["曝光量", "曝光", "exposure", "展示量", "impression", "展现量", "曝光数"],
    "click": ["点击量", "点击", "click", "点击数", "click_count", "clicks"],
    "new_user": ["新增注册用户", "增注册用户", "新增用户", "注册用户", "新用户", "new_user", "注册量", "新增", "注册人数", "new_users"],
    "active_user": ["活跃用户", "日活", "dau", "active_user", "活跃人数", "active_users", "激活用户"],
    "activated_user": ["激活用户", "activated_user", "激活数", "完成激活"],
    "return_user_1d": ["次日留存用户", "次日留存人数", "return_user_1d", "d1_return", "1日留存", "d1_retention_users"],
    "return_user_7d": ["7日留存用户", "7天留存", "return_user_7d", "d7_return", "周留存"],
    "return_user_30d": ["30日留存用户", "30天留存", "return_user_30d", "d30_return", "月留存"],
    "pay_user": ["付费用户", "支付用户", "pay_user", "付费人数", "购买用户", "付费数"],
    "revenue": ["营收", "收入", "revenue", "销售额", "成交金额", "gmv", "付费金额", "支付金额", "总营收", "金额"],
    "channel_cost": ["投放成本", "成本", "channel_cost", "花费", "消耗", "cost", "广告成本", "渠道成本", "投放花费"],
    "share_user": ["分享用户", "分享人数", "share_user", "分享数"],
    "share_new_user": ["分享新增", "分享拉新", "share_new_user", "邀请注册", "裂变新增"],
}


def _to_numeric(s):
    if s.dtype == object:
        s = s.astype(str).str.strip().str.replace("%", "").str.replace(",", "").str.replace("¥", "").str.replace("元", "")
    return pd.to_numeric(s, errors="coerce")


def _auto_map_columns(df):
    rename_map = {}
    df_cols_lower = {str(c).lower().strip(): c for c in df.columns}

    for std_name, aliases in COLUMN_MAPPING.items():
        for alias in aliases:
            alias_l = alias.lower().strip()
            if alias_l in df_cols_lower:
                rename_map[df_cols_lower[alias_l]] = std_name
                break

    return df.rename(columns=rename_map)


def load_external_data(uploaded_file):
    try:
        name = uploaded_file.name.lower()
        if name.endswith(".csv"):
            raw = uploaded_file.getvalue().decode("utf-8-sig", errors="replace")
            df = pd.read_csv(StringIO(raw))
        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "不支持的文件格式，请使用 CSV 或 Excel"

        df = _auto_map_columns(df)

        if "stat_date" not in df.columns:
            return None, f"未检测到日期列（日期/stat_date/date），当前列名：{list(df.columns)}"
        if "channel" not in df.columns:
            return None, f"未检测到渠道列（渠道/channel），当前列名：{list(df.columns)}"
        if "exposure" not in df.columns and "click" not in df.columns:
            return None, "未检测到曝光或点击数据列"

        df["stat_date"] = pd.to_datetime(df["stat_date"], errors="coerce")
        df = df[df["stat_date"].notna()]

        numeric_cols = ["exposure", "click", "new_user", "active_user", "activated_user",
                        "return_user_1d", "return_user_7d", "return_user_30d",
                        "pay_user", "revenue", "channel_cost", "share_user", "share_new_user"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = _to_numeric(df[col]).fillna(0)
            else:
                df[col] = 0

        if "new_user" not in df.columns or df["new_user"].sum() == 0:
            if "click" in df.columns and df["click"].sum() > 0:
                df["new_user"] = (df["click"] * 0.2).astype(int)

        if "active_user" not in df.columns or df["active_user"].sum() == 0:
            df["active_user"] = (df["new_user"] * 2.5).astype(int)

        if df["revenue"].sum() == 0 and df["pay_user"].sum() > 0:
            df["revenue"] = df["pay_user"] * 30

        if df["channel_cost"].sum() == 0:
            df["channel_cost"] = df["new_user"] * 8

        df = df[df["exposure"].fillna(0) > 0]

        return df, None
    except Exception as e:
        import traceback
        return None, f"数据解析失败：{str(e)}\n{traceback.format_exc()}"
