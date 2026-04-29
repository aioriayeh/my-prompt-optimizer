import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面基礎配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 介面淨化：CSS 隱藏內建提示，確保不重疊
st.markdown("""
    <style>
    /* 隱藏所有輸入框內建的指令文字 */
    div[data-testid="stInputInstructions"] {
        display: none !important;
    }
    /* 調整分頁標籤樣式 */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 系統資料：更新 2026 最新官方連結與模型清單
PROVIDER_INFO = {
    "Google Gemini": "https://aistudio.google.com/app/prompts/new",
    "OpenAI": "https://platform.openai.com/docs/models",
    "Anthropic Claude": "https://docs.anthropic.com/en/docs/about-claude/models",
    "xAI Grok": "https://console.x.ai/",
    "DeepSeek": "https://api-docs.deepseek.com/zh-cn/information/model_list",
    "NVIDIA": "https://build.nvidia.com/explore/discover",
    "OpenRouter": "https://openrouter.ai/models"
}

MODEL_DATA = {
    "Google Gemini": [
        "自定義輸入", 
        "gemini-3.1-flash-lite (免費)", 
        "gemini-3-flash (免費)", 
        "gemini-3.1-pro", 
        "gemini-2.5-flash", 
        "gemini-2.5-pro"
    ],
    "OpenAI": [
        "自定義輸入", "GPT-5.2", "GPT-5 mini", "GPT-5 nano", "GPT-5", "o3-deep-research"
    ],
    "Anthropic Claude": [
        "自定義輸入", "Claude Opus 4.7", "Claude Sonnet 4.6", "Claude Haiku 4.5"
    ],
    "xAI Grok": [
        "自定義輸入", "grok-4.1", "grok-4.1-mini", "grok-3"
    ],
    "DeepSeek": [
        "自定義輸入", "DeepSeek-V4", "DeepSeek-V4 Pro", "DeepSeek R1"
    ],
    "NVIDIA": [
        "自定義輸入", "Nemotron RAG (嵌入與語言重排序)"
    ],
    "OpenRouter": [
        "自定義輸入", "google/gemini-2.5-flash:free", "meta-llama/llama-3.1-8b-instruct:free"
    ]
}

# 4. 側邊欄配置
with st.sidebar:
    st.title("系統配置")
    
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()))
    
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
        st.caption("輸入或貼上後請按下 Enter 鍵以套用內容。")
        st.caption(f"請參閱 [官方模型清單]({PROVIDER_INFO[provider]})")
    else:
        final_model = temp_model.split(" (")[0]

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
        # 純淨指令結構設定
        system_instruction = (
            "你是一位專業的提示詞工程師。請將輸入內容重構為高品質的 Markdown 提示詞結構。 "
            "輸出結果必須僅包含以下標題及其詳盡內容：[角色定義 (Role)]、[任務說明 (Task)]、[背景與上下文 (Context)]、[輸出格式 (Format)]、[思維鏈引導 (CoT)]。 "
            "嚴禁輸出任何前言、優化說明、對話文字或後記。確保內容具備專業深度與細節。使用正體中文。"
        )
        
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
                        model=final_model, max_tokens=4096, system=system_instruction,
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
                    if base_urls[provider]: client_args["base_url"] = base_urls[provider]
                    client = OpenAI(**client_args)
                    
                    response = client.chat.completions.create(
                        model=final_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}],
                        extra_headers={"HTTP-Referer": "https://streamlit.io", "X-Title": "PromptOptimizer"} if provider == "OpenRouter" else None
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
                    st.info(f"偵測到模型 ID 錯誤。請點擊左側連結查詢最新 ID 並使用自定義輸入。")
                    st.link_button(f"查詢 {provider} 模型清單", PROVIDER_INFO[provider])