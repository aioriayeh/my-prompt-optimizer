import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 1. 頁面配置
st.set_page_config(page_title="AI 指令優化工具", layout="wide")

# 2. 介面淨化 CSS
st.markdown("""
    <style>
    /* 1. 刪除所有輸入框內的 "Press Enter to apply" 提示 */
    div[data-testid="stInputInstructions"] {
        display: none !important;
    }
    /* 2. 修正分頁標籤字體大小 */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 系統靜態資料
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
    "Google Gemini": ["自定義輸入", "gemini-3.1-flash-lite", "gemini-3-flash", "gemini-2.5-pro", "gemini-2.5-flash"],
    "OpenAI": ["自定義輸入", "gpt-5.2", "gpt-5-mini", "gpt-4o", "o3-deep-research"],
    "Anthropic Claude": ["自定義輸入", "claude-3-5-sonnet-latest", "claude-4-preview"],
    "xAI Grok": ["自定義輸入", "grok-4.1", "grok-3"],
    "DeepSeek": ["自定義輸入", "deepseek-v4", "deepseek-r1"],
    "NVIDIA": ["自定義輸入", "nemotron-3-8b-instruct"],
    "OpenRouter": ["自定義輸入", "google/gemini-2.5-flash:free", "meta-llama/llama-3.1-8b-instruct:free"]
}

# 4. 側邊欄配置 (穩定佈局版)
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("系統配置")
    
    # 服務商選擇
    provider = st.selectbox("選擇服務提供商：", list(MODEL_DATA.keys()), key="main_provider")
    
    if "key_store" not in st.session_state:
        st.session_state["key_store"] = {}
    current_key_name = f"{provider}_key"
    
    # API 金鑰輸入
    user_key = st.text_input(
        f"輸入 {provider} API 金鑰：", 
        value=st.session_state["key_store"].get(current_key_name, st.secrets.get(current_key_name, "")), 
        type="password",
        key=f"k_in_{provider}"
    )
    st.session_state["key_store"][current_key_name] = user_key

    st.write("---")

    # 模型選取
    temp_model = st.selectbox("選擇預設模型：", MODEL_DATA[provider], key=f"m_sel_{provider}")
    
    if temp_model == "自定義輸入":
        final_model = st.text_input("輸入精確模型 ID：", key=f"c_id_{provider}")
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
        st.error(f"錯誤：請填入 {provider} 的金鑰。")
    elif not final_model:
        st.warning("請設定模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入內容。")
    else:
        # 指令優化核心 (邏輯修正版)
        system_instruction = (
            "你是一個專業的提示詞工程師。你的任務是將使用者的原始需求重構為高品質的 Markdown 指令。 "
            "【關鍵要求】：在 [角色定義 (Role)] 部分，請根據使用者需求「自動分配合適的專業專家身份」。 "
            "例如：使用者想學物理，Role 應為物理教授；使用者想理財，Role 應為資深財務顧問。 "
            "嚴禁在輸出中稱呼自己為「提示詞工程師」。產出的結果必須可直接貼給另一個 AI 執行。 "
            "輸出僅限五個部分：[角色定義 (Role)]、[任務說明 (Task)]、[背景與上下文 (Context)]、[輸出格式 (Format)]、[思維鏈引導 (CoT)]。 "
            "嚴禁任何優化說明或前言。使用正體中文。"
        )
        
        with st.spinner("優化中..."):
            try:
                # 路由分流
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
                    # 相容接口 (OpenAI, xAI, DeepSeek, OpenRouter)
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
                    st.info("請點擊右上方按鈕複製專業指令。")
                    st.code(res, language="markdown")
                with tab_preview:
                    st.info("排版視覺預覽區。")
                    st.markdown(res)

            except Exception as e:
                st.error(f"連線失敗：{str(e)}")