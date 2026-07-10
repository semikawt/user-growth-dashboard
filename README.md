# 📊 AARRR 用户增长运营看板

> 基于AARRR增长模型的企业级用户运营BI分析平台 · Streamlit + Pandas + Plotly + LLM

一站式覆盖「数据ETL清洗 → AARRR全链路漏斗分析 → 交互式可视化看板 → AI智能诊断 → 运营报告生成」完整增长分析链路。

## ✨ 核心亮点

- **完整AARRR模型**：获客(Acquisition) → 激活(Activation) → 留存(Retention) → 变现(Revenue) → 推荐(Referral) 全链路漏斗
- **13+核心指标体系**：CTR/CVR/CAC/ARPU/ARPPU/ROI/D1/D7/D30留存/付费率/K因子等自动计算
- **6大分析看板**：总览大盘、渠道分析、留存分析、营收变现、裂变推荐、AI智能诊断
- **智能数据接入**：支持CSV/Excel上传，自动映射中文列名，智能补全缺失字段
- **AI增强分析**：一键增长诊断、活动方案策划、自然语言问数据（支持DeepSeek/OpenAI/智谱等）
- **报告自动生成**：一键导出Markdown格式运营分析报告
- **模拟数据引擎**：可自定义天数/种子生成百万级逼真运营数据

## 🚀 快速开始

### 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

浏览器访问 `http://localhost:8501`

### 部署到 Streamlit Cloud

1. Fork 本仓库到你的 GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)，用 GitHub 登录
3. 点击 "New app"，选择本仓库，主文件 `app.py`
4. （可选）在 Secrets 中配置 API Key：
```toml
LLM_API_KEY = "your_api_key"
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"
```
5. 点击 Deploy，几分钟后获得公开访问链接

## 📁 项目结构

```
UserGrowthDashboard/
├── app.py                  # Streamlit 主应用（6大Tab页面）
├── requirements.txt        # 依赖清单
├── .streamlit/config.toml  # 主题配置
└── utils/
    ├── data_generator.py   # 模拟数据生成器（单表AARRR全字段）
    ├── data_loader.py      # 外部数据加载（CSV/Excel + 智能列映射）
    ├── analyzer.py         # ETL清洗 + 指标计算 + 自动洞察
    ├── visualizer.py       # Plotly 可视化图表（10种图表）
    ├── llm_client.py       # 大模型API封装（诊断/策划/问答）
    └── report_generator.py # Markdown报告生成
```

## 📋 数据格式要求

上传CSV/Excel文件需包含以下核心字段（支持中文别名，系统自动映射）：

| 标准字段 | 中文别名 | 说明 |
|---------|---------|------|
| stat_date | 日期/统计日期 | 数据日期 |
| channel | 渠道/渠道名称/来源 | 获客渠道 |
| exposure | 曝光量/展示量 | 广告曝光次数 |
| click | 点击量 | 点击次数 |
| new_user | 新增用户/注册用户 | 当日新增注册 |
| active_user | 活跃用户/日活/DAU | 当日活跃用户 |
| pay_user | 付费用户/支付用户 | 当日付费人数 |
| revenue | 营收/收入/销售额/GMV | 当日营收金额 |
| channel_cost | 投放成本/成本/花费 | 当日渠道投放费用 |
| return_user_1d/7d/30d | 次日/7日/30日留存 | 留存用户数（可选） |
| share_user/share_new_user | 分享/裂变 | 分享数据（可选） |

## 📊 指标体系

### 获客层(Acquisition)
- **CTR** 点击率 = 点击量 / 曝光量
- **CVR** 注册转化率 = 新增用户 / 点击量
- **CAC** 获客成本 = 投放成本 / 新增用户

### 激活层(Activation)
- 激活率 = 激活用户 / 活跃用户

### 留存层(Retention)
- D1/D7/D30 留存率

### 变现层(Revenue)
- **ARPU** 单用户收益 = 营收 / 活跃用户
- **ARPPU** 付费用户均消 = 营收 / 付费用户
- 付费转化率 = 付费用户 / 活跃用户
- **ROI** 投资回报率 = (营收 - 成本) / 成本

### 推荐层(Referral)
- K因子（病毒系数）= 分享带来新增 / 分享用户数
- K>1 时产品进入自传播阶段

## 🛠 技术栈

- **Streamlit** - Web应用框架
- **Pandas/Numpy** - 数据处理与ETL
- **Plotly** - 交互式可视化
- **OpenAI SDK** - 大模型接口（兼容DeepSeek/智谱/OpenAI）

## 💼 简历价值

- 数据工程能力：大规模模拟数据生成、高性能ETL清洗、指标体系搭建
- 业务分析能力：AARRR增长模型、渠道ROI分析、留存分层、裂变K因子
- BI可视化能力：企业级交互式看板、多维度下钻分析
- AI落地能力：大模型API对接、业务归因分析、自然语言数据查询
