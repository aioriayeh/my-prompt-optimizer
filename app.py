import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面基礎配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 介面淨化：CSS 隱藏提示文字並維持輸入框功能
st.markdown("""
    <style>
    div[data-testid="stInputInstructions"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 系統資料：廠商清單與 2026 最新模型列表
PROVIDER_INFO = {
    "Google Gemini": "https://aistudio.google.com/app/model",
    "OpenAI": "https://platform.openai.com/docs/models",
    "Anthropic Claude": "https://docs.anthropic.com/en/docs/about-claude/models",
    "xAI Grok": "https://console.x.ai/",
    "DeepSeek": "https://api-docs.deepseek.com/zh-cn/information/model_list",
    "NVIDIA": "https://build.nvidia.com/explore/discover",
    "OpenRouter": "https://openrouter.ai/models"
}

MODEL_DATA = {
    "Google Gemini": [
        "自定義輸入", "Gemini 3.1 Pro", "Gemini 3 Flash", "Gemini 3.1 Flash-Lite", 
        "Gemini 2.5 Flash", "Gemini 2.5 Pro", "Gemini 2.5 Flash-Lite", "Gemini Embedding 2"
    ],
    "OpenAI": [
        "自定義輸入", "GPT-5.2", "GPT-5 mini", "GPT-5 nano", "GPT-5.2 pro", "GPT-5", 
        "GPT-4.1", "gpt-oss-120b", "gpt-oss-20b", "o3-deep-research", "o4-mini-deep-research"
    ],
    "Anthropic Claude": [
        "自定義輸入", "Claude Opus 4.7", "Claude Opus 4.6", "Claude Sonnet 4.6", "Claude Haiku 4.5"
    ],
    "xAI Grok": [
        "自定義輸入", "grok-4.1", "grok-4.1-mini", "grok-3", "grok-3-mini"
    ],
    "DeepSeek": [
        "自定義輸入", "DeepSeek-V4", "DeepSeek-V4 Flash", "DeepSeek-V4 Pro", "DeepSeek-V3.1", 
        "DeepSeek R1", "DeepSeek Math-7B"
    ],
    "NVIDIA": [
        "自定義輸入", "Nemotron RAG (嵌入與語言重排序)"
    ],
    "OpenRouter": [
        "自定義輸入", "google/gemini-2.5-flash:free", "meta-llama/llama-3.1-8b-instruct:free"
    ]
}

# 4. 側邊欄：系統配置
with st.sidebar:
    st.title("系統配置")
    
    # 選擇提供商
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()))
    
    # 狀態管理
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}
    current_key_name = f"{provider}_key"
    
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
        final_model = st.text_input("輸入精確模型 ID：", key=f"custom_{provider}_id")
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
        st.warning("請輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入指令內容。")
    else:
        system_instruction = "你是一名專業提示詞工程師，將輸入轉化為[角色任務]、[背景資訊]、[具體指令]、[約束條件]四個維度。使用正體中文回答。"
        
        with st.spinner("執行中..."):
            try:
                if provider == "Google Gemini":
                    formatted_model = final_model if final_model.startswith("models/") else f"models/{final_model}"
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(formatted_model)
                    response = model.generate_content(f"{system_instruction}\n\n輸入內容：{raw_prompt}")
                    res = response.text

                elif provider == "Anthropic Claude":
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=final_model, max_tokens=2048, system=system_instruction,
                        messages=[{"role": "user", "content": raw_prompt}]
                    )
                    res = response.content[0].text

                else:
                    base_urls = {
                        "OpenAI": None,
                        "xAI Grok": "https://api.x.ai/v1",
                        "DeepSeek": "https://api.deepseek.com",
                        "NVIDIA": "https://integrate.api.nvidia.com/v1",
                        "OpenRouter": "https://openrouter.ai/api/v1"
                    }
                    
                    client_args = {"api_key": api_key}
                    if base_urls[provider]:
                        client_args["base_url"] = base_urls[provider]
                    
                    client = OpenAI(**client_args)
                    
                    headers = {}
                    if provider == "OpenRouter":
                        headers = {"HTTP-Referer": "https://streamlit.io", "X-Title": "PromptOptimizer"}
                    
                    response = client.chat.completions.create(
                        model=final_model,
                        messages=[
                            {"role": "system", "content": system_instruction},
                            {"role": "user", "content": raw_prompt}
                        ],
                        extra_headers=headers if headers else None
                    )
                    res = response.choices[0].message.content

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
                    st.info("偵測到模型 ID 錯誤。請點擊左側連結查詢最新 ID 並使用自定義輸入。")
                    st.link_button(f"查詢 {provider} 模型清單", PROVIDER_INFO[provider])