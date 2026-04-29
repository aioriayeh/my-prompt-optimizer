import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面基礎配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 介面淨化 CSS
st.markdown("""
    <style>
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
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("系統配置")
    
    with st.form("config_form"):
        provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()), key="main_provider")
        
        if "key_store" not in st.session_state:
            st.session_state["key_store"] = {}
        current_key_name = f"{provider}_key"
        
        user_key = st.text_input(
            f"輸入 {provider} API 金鑰：", 
            value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")), 
            type="password"
        )
        
        temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider])
        
        submit_config = st.form_submit_button("套用配置")
        if submit_config:
            st.session_state["key_store"][current_key_name] = user_key
            st.success("配置已套用")

    st.write("---")
    
    # 模型 ID 處理
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", key=f"c_id_{provider}")
        st.caption("請貼上 ID 並按 Enter 確認。")
        st.caption(f"請參閱 [官方模型清單]({PROVIDER_INFO[provider]})")
    else:
        final_model = temp_model

# 5. 主介面
st.title("AI 指令優化工具")
st.text(f"當前模式：{provider} / {final_model}")

with st.form("prompt_form"):
    raw_prompt = st.text_area("原始指令內容：", placeholder="請輸入欲優化的指令內容...", height=150)
    execute_button = st.form_submit_button("執行優化")

if execute_button:
    api_key = st.session_state["key_store"].get(current_key_name)
    
    if not api_key:
        st.error(f"錯誤：請先在側邊欄填入並『套用』 {provider} 的金鑰。")
    elif not final_model:
        st.warning("請設定模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入內容。")
    else:
        system_instruction = (
            "你是一位具備高度語意洞察力的提示詞工程師。你的任務是優化使用者的原始指令。 "
            "【SOP 第一步：語意診斷】：請先判斷使用者輸入中是否存在拼寫錯誤、口語化描述或非標準術語（例如：up down 應識別為 Top-Down）。 "
            "【SOP 第二步：意圖校準】：根據診斷結果，將內容自動校正為專業術語與精確意圖。 "
            "【SOP 第三步：結構重構】：輸出一個 Markdown 結構，嚴禁任何前言或自我介紹。 "
            "輸出僅含五個標題： "
            "[角色定義 (Role)]：根據『校正後』的需求分配合適的專家身份。 "
            "[任務說明 (Task)]：明確、具體的動作目標。 "
            "[背景與上下文 (Context)]：描述場景、目標對象與必須包含的專業邏輯。 "
            "[輸出格式 (Format)]：規範排版與深度要求。 "
            "[思維鏈引導 (CoT)]：引導 AI 一步步思考。 "
            "請確保輸出的指令具備高度的實戰價值。使用正體中文。"
        )
        
        with st.spinner("語意診斷與指令優化中..."):
            try:
                if provider == "Google Gemini":
                    f_model = final_model if final_model.startswith("models/") else f"models/{final_model}"
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(f_model)
                    response = model.generate_content(f"{system_instruction}\n\n使用者輸入：{raw_prompt}")
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
                    st.info("說明：請點擊右上方按鈕複製專業指令。")
                    st.code(res, language="markdown")
                with tab_preview:
                    st.markdown(res)

            except Exception as e:
                st.error(f"執行失敗：{str(e)}")