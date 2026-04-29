import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. UI 空間優化
st.markdown("""
    <style>
    /* 增加輸入框高度，確保使用者文字與系統提示不重疊 */
    div[data-testid="stTextInput"] input {
        height: 55px !important;
        padding-top: 10px !important;
        padding-bottom: 20px !important;
    }
    /* 側邊欄頂部預留空間，防止第一個選項被裁切 */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 系統資料：完整模型清單與連結
PROVIDER_INFO = {
    "Google Gemini": "https://aistudio.google.com/app/apikey",
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
        "自定義輸入", "Nemotron RAG"
    ],
    "OpenRouter": [
        "自定義輸入", 
        "google/gemini-2.5-flash:free", 
        "google/gemini-3-flash:free", 
        "meta-llama/llama-3.1-8b-instruct:free", 
        "mistralai/pixtral-12b:free",
        "openai/gpt-4o-mini:free"
    ]
}

# 4. 側邊欄配置
with st.sidebar:
    st.title("系統配置")
    
    # 服務商選擇
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()), key="p_select")
    
    # 統一金鑰記憶
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}
    current_key_name = f"{provider}_key"
    
    user_key = st.text_input(
        "輸入 API 金鑰：", 
        value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")), 
        type="password",
        key=f"k_in_{provider}"
    )
    st.session_state["key_store"][current_key_name] = user_key

    st.write("---")

    # 模型選擇
    temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider], key=f"m_select_{provider}")
    
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", key=f"c_id_{provider}")
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
        st.error("錯誤：未偵測到金鑰。")
    elif not final_model:
        st.warning("請先輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入內容。")
    else:
        system_instruction = (
            "你是一位具備深度語意分析能力的專家。你的任務是優化使用者的原始指令。 "
            "1. 語意診斷：若輸入中存在不明術語或拼寫錯誤（例如: up down），請自動校正為專業術語（例如: Top-Down）。 "
            "2. 專家分配：根據需求自動分配解決問題的專業角色，嚴禁在輸出中提及自己是工程師。 "
            "3. 純淨輸出：嚴禁前言與說明。輸出僅包含以下 Markdown 結構： "
            "[角色定義 (Role)]、[任務說明 (Task)]、[背景與上下文 (Context)]、[輸出格式 (Format)]、[思維鏈引導 (CoT)]。 "
            "確保內容詳盡且具備實戰價值。使用正體中文。"
        )
        
        with st.spinner("語意優化中..."):
            try:
                # 服務商路由
                if provider == "Google Gemini":
                    f_model = final_model if final_model.startswith("models/") else f"models/{final_model}"
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(f_model)
                    response = model.generate_content(f"{system_instruction}\n\n需求內容：{raw_prompt}")
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

                # 6. 結果輸出
                st.write("---")
                tab_code, tab_preview = st.tabs(["指令複製", "結果預覽"])
                with tab_code:
                    st.info("請點擊右上方按鈕複製專業指令。")
                    st.code(res, language="markdown")
                with tab_preview:
                    st.markdown(res)

            except Exception as e:
                st.error(f"連線失敗：{str(e)}")