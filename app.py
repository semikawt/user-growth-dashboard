import os
import sys
import streamlit as st
import pandas as pd

from data_generator import generate_daily_data
from data_loader import load_external_data
from analyzer import (
    clean_data, get_overview_metrics, get_funnel_data, get_daily_trend,
    get_channel_analysis, get_retention_trend, get_referral_analysis,
    auto_insights
)
from visualizer import (
    plot_aarrr_funnel, plot_daily_active_trend, plot_channel_roi_bar,
    plot_channel_cac_vs_arpu, plot_retention_curves, plot_channel_retention_heatmap,
    plot_revenue_trend, plot_pay_metrics, plot_referral_analysis, plot_channel_conversion_funnel
)
from llm_client import LLMClient
from report_generator import generate_report

st.set_page_config(
    page_title="AARRR 用户增长运营看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea11 0%, #764ba211 100%);
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid #667eea;
        margin: 4px 0;
    }
    .metric-label { font-size: 13px; color: #888; margin-bottom: 4px; }
    .metric-value { font-size: 26px; font-weight: 700; color: #333; }
    .metric-sub { font-size: 12px; color: #999; margin-top: 2px; }
    .good { color: #27ae60 !important; }
    .bad { color: #e74c3c !important; }
</style>
""", unsafe_allow_html=True)


# --- Session State ---
DEFAULTS = {
    "api_config": {
        "api_key": os.getenv("LLM_API_KEY", ""),
        "api_base": os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
        "model": os.getenv("LLM_MODEL", "deepseek-chat"),
    },
    "ai_diag": None, "ai_diag_loading": False,
    "ai_plan": None, "ai_plan_loading": False,
    "ai_qa_result": None, "ai_qa_loading": False,
    "data_mode": "simulate", "raw_df": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# --- Sidebar ---
with st.sidebar:
    st.title("📊 AARRR 增长看板")
    st.caption("一站式用户增长BI分析平台")
    st.divider()

    st.subheader("💾 数据源")
    data_mode = st.radio("选择数据来源", ["🎲 模拟数据", "📁 上传文件"],
                         index=0 if st.session_state["data_mode"] == "simulate" else 1,
                         horizontal=True)

    if "模拟" in data_mode:
        st.session_state["data_mode"] = "simulate"
        days = st.slider("模拟天数", 14, 180, 90, 7)
        seed = st.number_input("随机种子", 1, 9999, 42, 1)
        if st.button("🔄 重新生成模拟数据", type="primary", use_container_width=True):
            st.session_state["raw_df"] = None
            for k in ["ai_diag", "ai_plan", "ai_qa_result"]:
                st.session_state[k] = None
            st.cache_data.clear()
            st.rerun()

        @st.cache_data
        def _gen_sim(d, s):
            return generate_daily_data(days=d, seed=s)

        raw_df = _gen_sim(days, seed)
    else:
        st.session_state["data_mode"] = "upload"
        uploaded = st.file_uploader("上传 CSV/Excel 文件", type=["csv", "xlsx", "xls"],
                                     help="需包含：日期(stat_date)、渠道(channel)、曝光量(exposure)、点击量(click)、新增用户(new_user)")
        st.markdown("""
        **字段说明**（支持中文别名）：
        - 日期、渠道名称
        - 曝光量、点击量、新增注册
        - 活跃用户、付费用户、营收
        - 投放成本、分享数据
        """)
        if uploaded:
            df, err = load_external_data(uploaded)
            if err:
                st.error(err)
                raw_df = generate_daily_data(90, 42)
            else:
                raw_df = df
                st.success(f"✅ 加载成功：{len(df)} 条，{df['channel'].nunique()} 渠道，{df['stat_date'].nunique()} 天")
        else:
            raw_df = st.session_state["raw_df"] or generate_daily_data(90, 42)

    st.divider()
    with st.expander("🔑 大模型API配置"):
        cfg = st.session_state["api_config"]
        api_key = st.text_input("API Key", value=cfg["api_key"], type="password",
                                 help="支持 DeepSeek/OpenAI/智谱等兼容接口")
        api_base = st.text_input("API Base URL", value=cfg["api_base"])
        model = st.text_input("模型", value=cfg["model"])
        if st.button("💾 保存配置", use_container_width=True):
            st.session_state["api_config"] = {"api_key": api_key, "api_base": api_base, "model": model}
            st.success("已保存")

    cfg = st.session_state["api_config"]


# --- Data Pipeline ---
df = clean_data(raw_df)
metrics = get_overview_metrics(df)
funnel_df = get_funnel_data(df)
daily_df = get_daily_trend(df)
channel_df = get_channel_analysis(df)
retention_df = get_retention_trend(df)
referral_df = get_referral_analysis(df)
insights = auto_insights(metrics, df)


# --- Sidebar Metrics ---
with st.sidebar:
    st.divider()
    st.subheader("📈 核心指标")
    col1, col2 = st.columns(2)
    col1.metric("总新增", f"{metrics['total_new_user']:,}")
    col2.metric("总营收", f"¥{metrics['total_revenue']:,.0f}")
    col1.metric("整体ROI", f"{metrics['roi']}%")
    col2.metric("净利润", f"¥{metrics['total_profit']:,.0f}")
    col1.metric("CAC", f"¥{metrics['cac']}")
    col2.metric("D7留存", f"{metrics['d7_retention']}%")


# --- Title ---
st.title("📊 AARRR 用户增长运营看板")
st.caption(f"数据周期：{daily_df['stat_date'].min().strftime('%Y-%m-%d')} ~ {daily_df['stat_date'].max().strftime('%Y-%m-%d')} | "
           f"共 {df['channel'].nunique()} 个渠道 · {df['stat_date'].nunique()} 天数据")


# --- Tabs ---
tabs = st.tabs([
    "🏠 总览大盘",
    "📢 渠道分析",
    "🔁 留存分析",
    "💰 营收变现",
    "🔗 裂变推荐",
    "🤖 AI智能诊断",
])


# ============ Tab1: 总览 ============
with tabs[0]:
    st.subheader("🎯 核心指标卡")
    mcols = st.columns(4)
    cards = [
        ("总曝光量", f"{metrics['total_exposure']:,}", "次", ""),
        ("总点击", f"{metrics['total_click']:,}", f"CTR {metrics['ctr']}%", "good" if metrics['ctr'] >= 5 else "bad"),
        ("总新增用户", f"{metrics['total_new_user']:,}", f"CVR {metrics['cvr']}%", "good" if metrics['cvr'] >= 20 else "bad"),
        ("总活跃用户", f"{metrics['total_active']:,}", f"激活率 {metrics['activation_rate']}%", ""),
        ("总营收", f"¥{metrics['total_revenue']:,.0f}", f"ARPU ¥{metrics['arpu']}", "good"),
        ("总投放成本", f"¥{metrics['total_cost']:,.0f}", f"CAC ¥{metrics['cac']}", "bad" if metrics['cac'] > 20 else "good"),
        ("净利润", f"¥{metrics['total_profit']:,.0f}", f"ROI {metrics['roi']}%", "good" if metrics['roi'] > 100 else "bad"),
        ("付费转化", f"{metrics['pay_rate']}%", f"ARPPU ¥{metrics['arppu']}", "good" if metrics['pay_rate'] >= 10 else "bad"),
    ]
    for i, (label, value, sub, cls) in enumerate(cards):
        with mcols[i % 4]:
            cls_html = f' class="{cls}"' if cls else ''
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value"{cls_html}>{value}</div>
                <div class="metric-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.subheader("🔍 数据洞察")
    for ins in insights:
        st.info(ins)

    c1, c2 = st.columns([2, 3])
    with c1:
        st.plotly_chart(plot_aarrr_funnel(funnel_df), use_container_width=True, key="overview_funnel")
    with c2:
        st.plotly_chart(plot_daily_active_trend(daily_df), use_container_width=True, key="overview_daily")

    with st.expander("📋 数据明细（最近7天）"):
        show = daily_df.tail(7).copy()
        show["stat_date"] = show["stat_date"].dt.strftime("%Y-%m-%d")
        numeric_cols = show.select_dtypes(include=["float64"]).columns
        show[numeric_cols] = show[numeric_cols].round(2)
        st.dataframe(show, use_container_width=True, hide_index=True)


# ============ Tab2: 渠道分析 ============
with tabs[1]:
    st.subheader("📢 渠道ROI分析")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.plotly_chart(plot_channel_roi_bar(channel_df), use_container_width=True, key="ch_roi")
    with cc2:
        st.plotly_chart(plot_channel_cac_vs_arpu(channel_df), use_container_width=True, key="ch_cac_arpu")

    st.plotly_chart(plot_channel_conversion_funnel(channel_df), use_container_width=True, key="ch_funnel")

    st.subheader("📋 渠道详情表")
    show_ch = channel_df.copy()
    for c in ["ctr", "cvr", "cac", "arpu", "pay_rate", "roi", "profit", "revenue", "channel_cost"]:
        if c in show_ch.columns:
            show_ch[c] = show_ch[c].round(2)
    st.dataframe(show_ch, use_container_width=True, hide_index=True,
                 column_config={"channel": "渠道", "exposure": "曝光", "click": "点击",
                                "new_user": "新增", "active_user": "活跃", "pay_user": "付费"})


# ============ Tab3: 留存分析 ============
with tabs[2]:
    st.subheader("🔁 留存率趋势")
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric("次日留存 (D1)", f"{metrics['d1_retention']}%",
               delta="健康" if metrics['d1_retention'] >= 35 else "偏低",
               delta_color="normal" if metrics['d1_retention'] >= 35 else "inverse")
    rc2.metric("7日留存 (D7)", f"{metrics['d7_retention']}%",
               delta="健康" if metrics['d7_retention'] >= 20 else "偏低",
               delta_color="normal" if metrics['d7_retention'] >= 20 else "inverse")
    rc3.metric("30日留存 (D30)", f"{metrics['d30_retention']}%",
               delta="健康" if metrics['d30_retention'] >= 8 else "偏低",
               delta_color="normal" if metrics['d30_retention'] >= 8 else "inverse")

    st.plotly_chart(plot_retention_curves(retention_df), use_container_width=True, key="ret_curves")
    st.plotly_chart(plot_channel_retention_heatmap(df), use_container_width=True, key="ret_heatmap")


# ============ Tab4: 营收变现 ============
with tabs[3]:
    st.subheader("💰 营收趋势")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("总营收", f"¥{metrics['total_revenue']:,.0f}")
    r2.metric("付费用户", f"{metrics['total_pay']:,}")
    r3.metric("付费转化率", f"{metrics['pay_rate']}%")
    r4.metric("ARPPU", f"¥{metrics['arppu']}")

    st.plotly_chart(plot_revenue_trend(daily_df), use_container_width=True, key="rev_trend")
    st.plotly_chart(plot_pay_metrics(df), use_container_width=True, key="pay_metrics")


# ============ Tab5: 裂变推荐 ============
with tabs[4]:
    st.subheader("🔗 裂变传播分析")
    total_share = int(referral_df["share_user"].sum())
    total_share_new = int(referral_df["share_new_user"].sum())
    avg_k = referral_df["k_factor"].mean()
    viral_pct = (total_share_new / max(1, metrics["total_new_user"]) * 100)

    rf1, rf2, rf3, rf4 = st.columns(4)
    rf1.metric("分享用户数", f"{total_share:,}")
    rf2.metric("裂变带来新增", f"{total_share_new:,}")
    rf3.metric("平均K因子", f"{avg_k:.3f}",
               delta="自传播" if avg_k >= 1 else "需优化",
               delta_color="normal" if avg_k >= 1 else "inverse")
    rf4.metric("裂变贡献占比", f"{viral_pct:.1f}%")

    st.plotly_chart(plot_referral_analysis(referral_df), use_container_width=True, key="ref_plot")

    with st.expander("📋 裂变详情"):
        st.dataframe(referral_df.round(2), use_container_width=True, hide_index=True)


# ============ Tab6: AI智能诊断 ============
with tabs[5]:
    st.subheader("🤖 AI 增长智能助手")

    if not cfg["api_key"]:
        st.warning("⚠️ 请先在左侧侧边栏配置大模型 API Key 后使用AI功能")
    else:
        ac1, ac2 = st.columns(2)
        with ac1:
            if st.button("🩺 一键AI增长诊断", type="primary", use_container_width=True):
                st.session_state["ai_diag_loading"] = True
                with st.spinner("AI正在深度分析增长数据..."):
                    try:
                        client = LLMClient(cfg["api_key"], cfg["api_base"], cfg["model"])
                        result = client.diagnose_growth(metrics, channel_df, retention_df, daily_df)
                        st.session_state["ai_diag"] = result
                    except Exception as e:
                        st.error(f"AI诊断失败：{e}")
                st.session_state["ai_diag_loading"] = False

        with ac2:
            if st.button("🎯 生成增长活动方案", use_container_width=True):
                st.session_state["ai_plan_loading"] = True
                with st.spinner("AI正在策划运营活动方案..."):
                    try:
                        client = LLMClient(cfg["api_key"], cfg["api_base"], cfg["model"])
                        result = client.suggest_campaign(metrics, channel_df)
                        st.session_state["ai_plan"] = result
                    except Exception as e:
                        st.error(f"AI生成失败：{e}")
                st.session_state["ai_plan_loading"] = False

        st.divider()
        st.markdown("##### 💬 自然语言问数据")
        q = st.text_input("输入你的问题，例如：7月短视频渠道CAC过高的原因是什么？", key="qa_input")
        if st.button("🔍 提问", use_container_width=True) and q:
            with st.spinner("AI正在分析数据..."):
                try:
                    client = LLMClient(cfg["api_key"], cfg["api_base"], cfg["model"])
                    result = client.answer_question(q, metrics, channel_df, daily_df)
                    st.session_state["ai_qa_result"] = result
                except Exception as e:
                    st.error(f"提问失败：{e}")

        if st.session_state.get("ai_qa_result"):
            st.markdown("**📝 回答：**")
            st.markdown(st.session_state["ai_qa_result"])
            st.divider()

        if st.session_state.get("ai_diag"):
            st.markdown("---")
            st.markdown("### 🩺 AI 增长诊断报告")
            st.markdown(st.session_state["ai_diag"])

        if st.session_state.get("ai_plan"):
            st.markdown("---")
            st.markdown("### 🎯 AI 活动策划方案")
            st.markdown(st.session_state["ai_plan"])


# --- Report Download ---
st.divider()
with st.expander("📄 生成完整运营分析报告"):
    ai_d = st.session_state.get("ai_diag", "")
    ai_p = st.session_state.get("ai_plan", "")
    if st.button("📥 生成报告", type="primary", use_container_width=True):
        report_md = generate_report(metrics, channel_df, daily_df, insights, ai_d, ai_p)
        st.session_state["report_md"] = report_md

    if "report_md" in st.session_state:
        st.download_button(
            "⬇️ 下载 Markdown 报告",
            st.session_state["report_md"],
            file_name=f"AARRR增长分析报告_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True
        )
        st.markdown(st.session_state["report_md"])
