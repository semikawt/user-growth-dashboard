import json
from openai import OpenAI


def _json_default(obj):
    from datetime import datetime, date
    if isinstance(obj, (datetime, date)):
        return obj.strftime("%Y-%m-%d %H:%M:%S") if isinstance(obj, datetime) else obj.strftime("%Y-%m-%d")
    if hasattr(obj, "item"):
        return obj.item()
    return str(obj)


class LLMClient:
    def __init__(self, api_key, base_url="https://api.deepseek.com", model="deepseek-chat"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def _call(self, system_prompt, user_content):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=2500,
        )
        return resp.choices[0].message.content

    def diagnose_growth(self, metrics, channel_df, retention_trend, daily_trend):
        ch_summary = channel_df.to_string(index=False)
        ret_summary = f"D1均值:{metrics['d1_retention']}%, D7均值:{metrics['d7_retention']}%, D30均值:{metrics['d30_retention']}%"
        daily_summary = (
            f"总曝光:{metrics['total_exposure']:,}, 总点击:{metrics['total_click']:,}, 总新增:{metrics['total_new_user']:,}, "
            f"总营收:¥{metrics['total_revenue']:,.2f}, 总成本:¥{metrics['total_cost']:,.2f}, ROI:{metrics['roi']}%, "
            f"CTR:{metrics['ctr']}%, CVR:{metrics['cvr']}%, CAC:¥{metrics['cac']}, ARPU:¥{metrics['arpu']}, "
            f"付费率:{metrics['pay_rate']}%, 整体利润:¥{metrics['total_profit']:,.2f}"
        )

        system = (
            "你是一位资深互联网用户增长专家，精通AARRR增长模型、渠道投放优化、用户留存分析和增长策略。"
            "请根据用户提供的运营数据，给出专业、具体、可落地的增长诊断分析，直接输出Markdown格式，不要多余客套。"
            "分析需包含：1.整体大盘诊断 2.渠道优化建议(指出优劣渠道) 3.留存问题分析 4.变现转化问题 5.具体可执行的3-5条增长策略"
        )
        user = f"## 核心指标\n{daily_summary}\n\n## 留存情况\n{ret_summary}\n\n## 渠道详情\n{ch_summary}"
        return self._call(system, user)

    def suggest_campaign(self, metrics, channel_df):
        ch_summary = channel_df.to_string(index=False)
        summary = (
            f"当前总新增{metrics['total_new_user']:,}人，总营收¥{metrics['total_revenue']:,.2f}，ROI {metrics['roi']}%，"
            f"CAC ¥{metrics['cac']}，D7留存{metrics['d7_retention']}%，付费率{metrics['pay_rate']}%。"
        )
        system = (
            "你是一位资深互联网运营策划专家，擅长设计增长活动方案。"
            "请根据数据情况，设计3个具体可落地的运营活动方案，帮助提升用户增长。"
            "每个方案需包含：活动名称、活动目标、目标人群、活动机制、预期效果、预算建议、核心指标。"
            "直接输出Markdown格式，条理清晰，方案可直接执行。"
        )
        user = f"## 当前数据概况\n{summary}\n\n## 渠道数据\n{ch_summary}"
        return self._call(system, user)

    def answer_question(self, question, metrics, channel_df, daily_trend):
        ch_json = channel_df.head(10).to_dict(orient="records")
        daily_json = daily_trend.tail(30).to_dict(orient="records")
        context = {
            "overview": metrics,
            "channels": ch_json,
            "daily_trend_recent": daily_json
        }
        context_str = json.dumps(context, ensure_ascii=False, default=_json_default, indent=2)

        system = (
            "你是用户增长数据分析师，请根据提供的数据回答用户的问题。"
            "回答要有数据支撑，引用具体数字，给出结论和建议。"
            "如果数据中找不到答案，直接说明。回答使用Markdown格式。"
        )
        user = f"## 数据上下文\n{context_str}\n\n## 用户问题\n{question}"
        return self._call(system, user)
