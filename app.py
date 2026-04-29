import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面基礎配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 介面淨化：使用更精確的 CSS，只隱藏文字，不影響點擊功能
st.markdown("""
    <style>
    /* 準確隱藏輸入框下方的提示文字 (Press Enter to apply) */
    div[data-testid="stInputInstructions"] {
        display: none !important;
    }
    /* 調整分頁組件的字體與間距 */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 系統靜態資料
PROVIDER_INFO = {
    "Google Gemini (官方)": "https://aistudio.google.com/app/model",
    "OpenRouter (聚合)": "https://openrouter.ai/models?order=per_request_usd_asc&types=free",
    "OpenAI (官方)": "https://platform.openai.com/docs/models",
    "Anthropic (官方)": "https://docs.anthropic.com/en/docs/about-claude/models",
    "Groq (高流速)": "https://console.groq.com/docs/models",
    "DeepSeek (官方)": "https://api-docs.deepseek.com/zh-cn/information/model_list"
}

MODEL_DATA = {
    "Google Gemini (官方)": ["models/gemini-2.5-flash", "models/gemini-1.5-pro", "自定義輸入"],
    "OpenRouter (聚合)": ["google/gemini-2.5-flash:free", "google/gemini-2.0-flash-exp:free", "meta-llama/llama-3.1-8b-instruct:free", "自定義輸入"],
    "OpenAI (官方)": ["gpt-4o", "gpt-4o-mini", "自定義輸入"],
    "Anthropic (官方)": ["claude-3-5-sonnet-latest", "自定義輸入"],
    "Groq (高流速)": ["llama-3.3-70b-versatile", "自定義輸入"],
    "DeepSeek (官方)": ["deepseek-chat", "自定義輸入"]
}

# 4. 側邊欄配置
with st.sidebar:
    st.title("系統配置")
    
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()))
    
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}
    current_key_name = f"{provider}_key"
    
    # 這裡增加了一個 key 參數，確保 Streamlit 能正確追蹤輸入框狀態
    user_key = st.text_input(
        f"輸入 {provider} API 金鑰：", 
        value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")), 
        type="password",
        key=f"input_{current_key_name}"
    )
    st.session_state["key_store"][current_key_name] = user_key

    st.write("---")

    temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider])
    
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", key="custom_model_id_field")
        st.caption(f"請參閱 [官方模型清單]({PROVIDER_INFO[provider]})")
    else:
        final_model = temp_model

# 5. 主介面
st.title("AI 指令優化工具")
st.text(f"當前模式：{provider} / {final_model}")

raw_prompt = st.text_area("原始指令內容：", placeholder="請輸入欲優化的指令內容...", height=150)

if st.button("執行優化"):
    api_key = st.session_state["key_store"].get(current_key_name)
    
    if not api_key:
        st.error(f"錯誤：未偵測到 {provider} 的金鑰。")
    elif not final_model:
        st.warning("請先選擇或手動輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入指令內容。")
    else:
        system_instruction = "你是一名專業提示詞工程師，將輸入轉化為[角色任務]、[背景資訊]、[具體指令]、[約束條件]四個維度。使用正體中文回答。"
        
        with st.spinner("執行中..."):
            try:
                if provider == "Google Gemini (官方)":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(final_model)
                    response = model.generate_content(f"{system_instruction}\n\n輸入內容：{raw_prompt}")
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
                    response = client.messages.create(
                        model=final_model, 
                        max_tokens=2048, 
                        system=system_instruction, 
                        messages=[{"role": "user", "content": raw_prompt}]
                    )
                    res = response.content[0].text

                # 6. 結果輸出
                st.write("---")
                tab_code, tab_preview = st.tabs(["指令複製", "結果預覽"])
                
                with tab_code:
                    st.info("說明：請點擊右上角按鈕複製原始指令。")
                    st.code(res, language="markdown")
                
                with tab_preview:
                    st.info("說明：此處顯示排版後的視覺效果。")
                    st.markdown(res)

            except Exception as e:
                error_detail = str(e)
                st.error(f"連線失敗：{error_detail}")
                
                if "404" in error_detail or "not found" in error_detail.lower():
                    st.warning("偵測到模型 ID 錯誤。")
                    st.link_button(f"查詢 {provider} 模型清單", PROVIDER_INFO[provider])