import streamlit as st
import pandas as pd
import random
import re

# 读取敏感词表
@st.cache_data
def load_sensitive_words():
    try:
        df = pd.read_csv('sensitive_words.csv')
        sensitive_dict = {}
        for index, row in df.iterrows():
            category = row['category']
            word = row['word']
            if category in sensitive_dict:
                sensitive_dict[category].append(word)
            else:
                sensitive_dict[category] = [word]
        return sensitive_dict
    except Exception as e:
        st.error(f"敏感词库加载失败：{e}")
        return {}

def assess_risk(text, sensitive_words):
    matches = []
    suggestions = {}
    for category, words in sensitive_words.items():
        for word in words:
            if word in text:
                matches.append((category, word))
                replacement = generate_replacement(category)
                suggestions[word] = replacement
    if matches:
        risk_score = min(100 - len(matches) * 10, 30)
        risk_level = "高风险" if risk_score < 50 else "中风险"
    else:
        risk_score = 100
        risk_level = "低风险"
    return matches, risk_level, risk_score, suggestions

def generate_replacement(category):
    default_alternatives = {
        "政治相关": ["社会话题", "资讯分享"],
        "金融投资诱导": ["理财知识", "经验交流"],
        "色情低俗": ["趣味分享", "互动娱乐"],
        "夸大宣传": ["真实体验", "合理预期"],
        "医疗健康虚假": ["健康小贴士", "科学参考"],
        "诱导转移联系": ["官方咨询", "正规渠道"],
        "赌博博彩相关": ["娱乐内容", "兴趣讨论"],
        "其他高危词": ["信息提示", "内容优化"]
    }
    return random.choice(default_alternatives.get(category, ["内容优化"]))

def highlight_text(text, matches):
    highlighted = text
    for _, word in matches:
        highlighted = re.sub(
            word, 
            f"<mark style='background-color: #FFDD57'>{word}</mark>", 
            highlighted
        )
    return highlighted

def rewrite_text(text, suggestions):
    new_text = text
    for word, replacement in suggestions.items():
        new_text = new_text.replace(word, replacement)
    return new_text

# 页面设置（移动端适配优化）
st.set_page_config(page_title="抖音文案预审·手机适配版", page_icon="📱", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    textarea {
        font-size: 18px !important;
    }
    button {
        font-size: 20px !important;
        height: 50px !important;
    }
    .stTextArea label {
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📱 抖音内容预审核器（移动端版）")
st.markdown("快速检测文案，规避违规风险，手机党专用体验！")

user_input = st.text_area("请输入要审核的抖音文案：", height=300, label_visibility="visible")

sensitive_words = load_sensitive_words()

if st.button("🚀 开始审核", use_container_width=True):
    if not user_input.strip():
        st.warning("请先输入内容。")
    else:
        matches, risk_level, risk_score, suggestions = assess_risk(user_input, sensitive_words)
        st.subheader("审核结果")

        st.metric(label="内容安全得分", value=f"{risk_score}/100")
        st.write(f"违规等级评估：**{risk_level}**")

        if matches:
            st.error(f"⚠️ 共检测到 {len(matches)} 个敏感点：")
            for category, word in matches:
                st.write(f"- 类型：**{category}** ➡️ 敏感词：`{word}` ➡️ 建议替换为：`{suggestions[word]}`")
            
            st.subheader("违规词高亮")
            st.markdown(highlight_text(user_input, matches), unsafe_allow_html=True)
            
            st.subheader("智能改写文案")
            rewritten = rewrite_text(user_input, suggestions)
            st.success(rewritten)

            st.info("✅ 建议根据改写版优化发布，降低违规风险。")
        else:
            st.success("✅ 内容安全，无明显违规！")

st.markdown("---")
st.caption("数据源：抖音官方规则、社区公约、平台公告。保持同步更新。")
