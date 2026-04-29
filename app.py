import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 深度 UI 修復
st.markdown("""
    <style>
    /* 解決選單被遮擋：調整側邊欄容器的內距與溢出處理 */
    [data-testid="stSidebarContent"] {
        padding-top: 3rem !important;
    }

    /* 解決文字重疊：強行撐開輸入框空間 */
    div[data-testid="stTextInput"] > div[data-baseweb="input"] {
        min-height: 75px !important;
        display: flex !important;
        align-items: flex-start !important;
        padding-top: 10px !important;
    }
    
    div[data-testid="stTextInput"] input {
        line-height: 1.5 !important;
        margin-bottom: 25px !important; /* 強制把底部的提示小字推開 */
    }

    /* 讓提示小字顯示在更合理的位置，且不與文字重合 */
    div[data-testid="stInputInstructions"] {
        position: absolute !important;
        bottom: 5px !important;
        font-size: 11px !important;
        color: #888 !important;
    }

    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 完整模型清單資料庫
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
        "自定義輸入", "Nemotron RAG"
    ],
    "OpenRouter": [
        "自定義輸入", "google/gemini-2.5-flash:free", "google/gemini-3-flash:free", 
        "meta-llama/llama-3.1-8b-instruct:free", "mistralai/pixtral-12b:free", "openai/gpt-4o-mini:free"
    ]
}

PROVIDER_LINKS = {
    "Google Gemini": "https://aistudio.google.com/app/apikey",
    "OpenRouter": "https://openrouter.ai/models",
    "OpenAI": "https://platform.openai.com/docs/models",
    "Anthropic Claude": "https://docs.anthropic.com/en/docs/about-claude/models"
}

# 4. 側邊欄
with st.sidebar:
    st.title("系統配置")
    
    # 服務商選擇
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()), key="main_p")
    
    # 金鑰管理
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}
    current_key_name = f"{provider}_key"
    
    user_key = st.text_input(
        "輸入 API 金鑰：", 
        value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")), 
        type="password",
        key=f"api_in_{provider}"
    )
    st.session_state["key_store"][current_key_name] = user_key

    st.write("---")

    # 模型選擇
    temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider], key=f"mod_in_{provider}")
    
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", key=f"cust_id_{provider}")
        st.caption("貼上模型 ID 後，請按下 Enter 鍵以套用。")
        st.caption(f"請參閱 [官方模型清單]({PROVIDER_LINKS.get(provider, '#')})")
    else:
        final_model = temp_model

# 5. 主介面
st.title("AI 指令優化工具")
st.text(f"當前模式：{provider} / {final_model}")

raw_prompt = st.text_area("原始指令內容：", placeholder="請輸入欲優化的指令內容...", height=150)

if st.button("執行優化"):
    api_key = st.session_state["key_store"].get(current_key_name)
    
    if not api_key:
        st.error("錯誤：未偵測到金鑰。")
    elif not final_model:
        st.warning("請先輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入內容。")
    else:
        system_instruction = (
            "你是一位具備深度語意分析能力的專家。你的任務是優化使用者的原始指令。 "
            "1. 語意診斷：若輸入中存在拼寫錯誤或非專業術語（例如: up down），請根據上下文推論其真實意圖並自動校正（例如: Top-Down）。 "
            "2. 專家分配：根據校正後的意圖自動分配專業角色。嚴禁提及自己是優化器。 "
            "3. 純淨輸出：僅輸出 Markdown 結構，嚴禁任何說明。 "
            "結構：[角色定義 (Role)]、[任務說明 (Task)]、[背景與上下文 (Context)]、[輸出格式 (Format)]、[思維鏈引導 (CoT)]。 "
            "使用正體中文。"
        )
        
        with st.spinner("語意診斷與指令優化中..."):
            try:
                if provider == "Google Gemini":
                    f_model = final_model if final_model.startswith("models/") else f"models/{final_model}"
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(f_model)
                    response = model.generate_content(f"{system_instruction}\n\n需求：{raw_prompt}")
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
                        "OpenAI": None, "xAI Grok": "https://api.x.ai/v1", "DeepSeek": "https://api.deepseek.com", 
                        "NVIDIA": "https://integrate.api.nvidia.com/v1", "OpenRouter": "https://openrouter.ai/api/v1"
                    }
                    client = OpenAI(api_key=api_key, base_url=base_urls.get(provider))
                    response = client.chat.completions.create(
                        model=final_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}],
                        extra_headers={"HTTP-Referer": "https://streamlit.io", "X-Title": "PromptOptimizer"} if provider == "OpenRouter" else None
                    )
                    res = response.choices[0].message.content

                # 6. 結果顯示
                st.write("---")
                tab_code, tab_preview = st.tabs(["指令複製", "結果預覽"])
                with tab_code:
                    st.info("說明：請點擊右上角按鈕複製專業指令。")
                    st.code(res, language="markdown")
                with tab_preview:
                    st.markdown(res)

            except Exception as e:
                st.error(f"連線失敗：{str(e)}")