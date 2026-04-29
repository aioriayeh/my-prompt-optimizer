import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 頁面配置
st.set_page_config(page_title="提示詞優化器", page_icon="🧪", layout="wide")

# --- 2026 全球模型資源庫 (校對版) ---
MODEL_DATA = {
    "Google Gemini (官方)": ["models/gemini-2.5-flash", "models/gemini-1.5-pro", "models/gemma-3-27b-it"],
    "OpenAI (官方)": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"],
    "Anthropic (官方)": ["claude-3-5-sonnet-latest", "claude-3-5-haiku-latest", "claude-3-opus-latest"],
    "OpenRouter (免費推薦)": [
        "google/gemini-2.5-flash:free",      # 2026 最新免費版
        "openai/gpt-oss-120b:free",          # 開源最強免費模型
        "meta-llama/llama-3.1-8b-instruct:free",
        "nvidia/nemotron-3-super:free",
        "deepseek/deepseek-r1:free",
        "qwen/qwen3-4b:free",
        "microsoft/phi-3.5-mini-128k:free"
    ],
    "Groq (極速)": ["llama-3.3-70b-versatile", "gemma2-9b-it"],
    "DeepSeek (官方)": ["deepseek-chat", "deepseek-coder"]
}

# --- 側邊欄：獨立配置面板 ---
with st.sidebar:
    st.title("API 資源調度中心")
    
    # 讓使用者先選大類，介面更清楚
    provider = st.selectbox("1. 選擇 AI 服務商：", list(MODEL_DATA.keys()))
    
    st.divider()

    # 每個服務商獨立記憶金鑰
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}

    current_key_name = f"{provider}_key"
    user_key = st.text_input(
        f"2. 輸入 {provider} 金鑰：",
        value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")),
        type="password"
    )
    st.session_state["key_store"][current_key_name] = user_key

    # OpenRouter 申請按鈕 (僅在選中時出現)
    if "OpenRouter" in provider and not user_key:
        st.link_button("👉 點我獲取免費 OpenRouter 金鑰", "https://openrouter.ai/keys")

    st.divider()

    # 3. 具體模型選單
    model_name = st.selectbox("3. 選擇具體模型：", MODEL_DATA[provider])
    st.caption(f"目前路徑：{model_name}")

# --- 主畫面 ---
st.title("🚀 指令優化器：全功能版")
st.markdown(f"連線狀態：使用 **{provider}** 下的 **{model_name}**")

raw_prompt = st.text_area("原始指令內容：", placeholder="幫我寫份完整的 python 學習計畫...", height=150)

if st.button("執行優化引擎"):
    api_key = st.session_state["key_store"].get(current_key_name)
    
    if not api_key:
        st.error(f"請先填入 {provider} 的金鑰。")
    elif not raw_prompt:
        st.warning("請輸入內容喔！")
    else:
        # 指令優化核心
        system_instruction = "你是一名專業提示詞工程師，將輸入轉化為[角色任務]、[背景資訊]、[具體指令]、[約束條件]四個維度。使用正體中文回答。"
        
        with st.spinner(f"正在連線至 {provider}..."):
            try:
                # --- 核心連線邏輯 (依廠商分流) ---
                if provider == "Google Gemini (官方)":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(f"{system_instruction}\n\n輸入：{raw_prompt}")
                    res = response.text

                elif provider == "OpenRouter (免費推薦)":
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}],
                        extra_headers={"HTTP-Referer": "https://streamlit.io", "X-Title": "PromptOptimizer"}
                    )
                    res = response.choices[0].message.content

                elif provider == "OpenAI (官方)":
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res = response.choices[0].message.content

                elif provider == "Anthropic (官方)":
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=model_name, max_tokens=2048, system=system_instruction,
                        messages=[{"role": "user", "content": raw_prompt}]
                    )
                    res = response.content[0].text

                elif provider == "Groq (極速)" or provider == "DeepSeek (官方)":
                    base_url = "https://api.groq.com/openai/v1" if "Groq" in provider else "https://api.deepseek.com"
                    client = OpenAI(api_key=api_key, base_url=base_url)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res = response.choices[0].message.content

                # --- 輸出區域 ---
                st.divider()
                st.subheader("優化後的專業提示詞")
                st.code(res, language="markdown")
                st.markdown(res)

            except Exception as e:
                st.error(f"⚠️ 連線出錯了：{str(e)}")
                if "404" in str(e):
                    st.info("提示：該模型在 2026 年可能已更新 ID。請嘗試在選單中更換為 'Gemini 2.5' 版本。")