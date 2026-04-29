import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面基礎配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 精確 UI 淨化
st.markdown("""
    <style>
    /* 隱藏輸入框下方的提示小字 (Press Enter to apply) */
    div[data-testid="stInputInstructions"] {
        display: none !important;
    }
    /* 確保側邊欄頂部有適當空間，防止選單被裁切 */
    [data-testid="stSidebar"] {
        padding-top: 1rem;
    }
    /* 調整分頁標籤字體 */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 系統靜態資料
PROVIDER_INFO = {
    "Google Gemini": "https://aistudio.google.com/app/apikey",
    "OpenRouter": "https://openrouter.ai/models",
    "OpenAI": "https://platform.openai.com/docs/models",
    "Anthropic Claude": "https://docs.anthropic.com/en/docs/about-claude/models",
    "xAI Grok": "https://console.x.ai/",
    "DeepSeek": "https://api-docs.deepseek.com/zh-cn/information/model_list"
}

MODEL_DATA = {
    "Google Gemini": ["自定義輸入", "gemini-3.1-flash-lite", "gemini-2.5-pro", "gemini-1.5-flash"],
    "OpenRouter": ["自定義輸入", "google/gemini-2.5-flash:free", "meta-llama/llama-3.1-8b-instruct:free"],
    "OpenAI": ["自定義輸入", "gpt-5.2", "gpt-4o", "o3-deep-research"],
    "Anthropic Claude": ["自定義輸入", "claude-3-5-sonnet-latest", "claude-4-preview"],
    "xAI Grok": ["自定義輸入", "grok-4.1", "grok-3"],
    "DeepSeek": ["自定義輸入", "deepseek-v4", "deepseek-r1"]
}

# 4. 側邊欄配置
with st.sidebar:
    st.title("系統配置")
    
    # 服務商選擇
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()), key="p_select")
    
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

    temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider], key=f"m_select_{provider}")
    
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", key=f"custom_id_{provider}")
        st.caption("貼上模型 ID 後，請按下 Enter 鍵以套用。")
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
        st.error(f"錯誤：未偵測到金鑰。")
    elif not final_model:
        st.warning("請先選取或手動輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入指令內容。")
    else:
        system_instruction = (
            "你是一位具備高度語意洞察力的專家。你的任務是將使用者的原始需求重構為專業指令。 "
            "1. 語意校準：若發現術語錯誤（如：up down），請自動更正為專業術語（如：Top-Down）。 "
            "2. 專家分配：根據需求自動分配專業角色，嚴禁在輸出中提及自己是優化器或工程師。 "
            "3. 純淨輸出：僅輸出 Markdown 結構，嚴禁任何前言或優化說明。 "
            "輸出結構：[角色定義 (Role)]、[任務說明 (Task)]、[背景與上下文 (Context)]、[輸出格式 (Format)]、[思維鏈引導 (CoT)]。 "
            "使用正體中文回答。"
        )
        
        with st.spinner("優化中..."):
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
                        "OpenAI": None, "xAI Grok": "https://api.x.ai/v1", "DeepSeek": "https://api.deepseek.com", "OpenRouter": "https://openrouter.ai/api/v1"
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
                    st.info("請點擊右上方按鈕複製專業指令。")
                    st.code(res, language="markdown")
                with tab_preview:
                    st.markdown(res)

            except Exception as e:
                st.error(f"連線失敗：{str(e)}")