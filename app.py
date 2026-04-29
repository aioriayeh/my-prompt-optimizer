import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 頁面配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 1. 廠商資訊與模型參考連結
PROVIDER_INFO = {
    "Google Gemini (官方)": "https://aistudio.google.com/app/model",
    "OpenRouter (聚合)": "https://openrouter.ai/models?order=per_request_usd_asc&types=free",
    "OpenAI (官方)": "https://platform.openai.com/docs/models",
    "Anthropic (官方)": "https://docs.anthropic.com/en/docs/about-claude/models",
    "Groq (高流速)": "https://console.groq.com/docs/models",
    "DeepSeek (官方)": "https://api-docs.deepseek.com/zh-cn/information/model_list"
}

# 預設模型清單
MODEL_DATA = {
    "Google Gemini (官方)": ["models/gemini-2.5-flash", "models/gemini-1.5-pro", "自定義輸入"],
    "OpenRouter (聚合)": ["google/gemini-2.5-flash:free", "google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.1-8b-instruct:free", "自定義輸入"],
    "OpenAI (官方)": ["gpt-4o", "gpt-4o-mini", "自定義輸入"],
    "Anthropic (官方)": ["claude-3-5-sonnet-latest", "自定義輸入"],
    "Groq (高流速)": ["llama-3.3-70b-versatile", "自定義輸入"],
    "DeepSeek (官方)": ["deepseek-chat", "自定義輸入"]
}

# 2. 側邊欄：配置面板
with st.sidebar:
    st.title("系統配置")
    
    # 選擇服務商
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()))
    
    # 金鑰管理
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}
    current_key_name = f"{provider}_key"
    user_key = st.text_input(f"輸入 {provider} API 金鑰：", value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")), type="password")
    st.session_state["key_store"][current_key_name] = user_key

    st.write("---")

    # 3. 模型選擇
    temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider])
    
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", placeholder="例如: google/gemini-2.0-flash-exp:free")
        st.caption(f"請參閱 [官方模型清單]({PROVIDER_INFO[provider]})")
    else:
        final_model = temp_model

# 3. 主畫面介面
st.title("AI 指令優化工具")
st.text(f"當前配置：{provider} / {final_model}")

raw_prompt = st.text_area("原始指令內容：", placeholder="請輸入欲優化的指令...", height=150)

if st.button("執行優化"):
    api_key = st.session_state["key_store"].get(current_key_name)
    
    if not api_key:
        st.error(f"錯誤：未偵測到 {provider} 的金鑰。")
    elif not final_model:
        st.warning("請選擇或輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入指令內容。")
    else:
        system_instruction = "你是一名專業提示詞工程師，將輸入轉化為[角色任務]、[背景資訊]、[具體指令]、[約束條件]四個維度。使用正體中文回答。"
        
        with st.spinner("執行中..."):
            try:
                # 路由邏輯
                if provider == "Google Gemini (官方)":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(final_model)
                    response = model.generate_content(f"{system_instruction}\n\n輸入：{raw_prompt}")
                    res = response.text

                elif provider == "OpenRouter (聚合)":
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                    response = client.chat.completions.create(
                        model=final_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}],
                        extra_headers={"HTTP-Referer": "https://streamlit.io", "X-Title": "PromptOptimizer"}
                    )
                    res = response.choices[0].message.content

                elif provider in ["OpenAI (官方)", "Groq (高流速)", "DeepSeek (官方)"]:
                    urls = {"OpenAI (官方)": None, "Groq (高流速)": "https://api.groq.com/openai/v1", "DeepSeek (官方)": "https://api.deepseek.com"}
                    client = OpenAI(api_key=api_key, base_url=urls.get(provider))
                    response = client.chat.completions.create(
                        model=final_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res = response.choices[0].message.content

                elif provider == "Anthropic (官方)":
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(model=final_model, max_tokens=2048, system=system_instruction, messages=[{"role": "user", "content": raw_prompt}])
                    res = response.content[0].text

                # 結果顯示
                st.write("---")
                st.subheader("優化結果")
                st.code(res, language="markdown")
                st.markdown(res)

            except Exception as e:
                # 錯誤處理與導向
                error_msg = str(e)
                st.error(f"連線失敗：{error_msg}")
                
                if "404" in error_msg or "not found" in error_msg.lower():
                    st.info(f"偵測到模型 ID 錯誤。請確認模型清單並於左側自定義輸入。")
                    st.link_button(f"查詢 {provider} 最新模型 ID", PROVIDER_INFO[provider])