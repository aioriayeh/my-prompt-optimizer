import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 頁面配置
st.set_page_config(page_title="AI 模型大滿貫優化器", page_icon="🌐", layout="wide")

# --- 定義模型大清單 (25+ 模型預載) ---
# 注意：這些 ID 是 OpenRouter 與各大廠商的標準格式
MODEL_LIBRARY = {
    "OpenRouter (免費推薦)": [
        "google/gemini-flash-1.5-8b:free", 
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "qwen/qwen-2-72b-instruct:free",
        "nousresearch/hermes-3-llama-3.1-8b:free"
    ],
    "Groq (極速系列)": [
        "llama-3.1-70b-versatile", 
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ],
    "Google Gemini (原生)": [
        "models/gemini-2.5-flash", 
        "models/gemini-1.5-pro",
        "models/gemini-1.5-flash-latest"
    ],
    "DeepSeek (國產之光)": [
        "deepseek-chat", 
        "deepseek-coder"
    ],
    "OpenAI / Claude (高階)": [
        "gpt-4o", 
        "gpt-4o-mini", 
        "claude-3-5-sonnet-20240620"
    ]
}

# --- 側邊欄：進階 UI 設計 ---
with st.sidebar:
    st.title("🛡️ API 資源調度中心")
    
    # 1. 第一層：選擇服務商 (分類明確化)
    provider_list = list(MODEL_LIBRARY.keys())
    selected_provider = st.selectbox("1. 選擇 API 服務來源：", provider_list)
    
    st.divider()

    # 2. 獲取當前金鑰設定
    key_name = f"{selected_provider}_key"
    default_key = st.secrets.get(key_name, "")
    
    # Session State 記憶功能
    if "keys" not in st.session_state:
        st.session_state["keys"] = {}
        
    user_key = st.text_input(
        f"2. 輸入 {selected_provider} 金鑰：",
        value=st.session_state["keys"].get(key_name, default_key),
        type="password"
    )
    st.session_state["keys"][key_name] = user_key

    # OpenRouter 自動引導 (您的核心需求)
    if "OpenRouter" in selected_provider and not user_key:
        st.warning("💡 偵測到尚未輸入金鑰！")
        st.link_button("👉 點我免費獲取 OpenRouter 金鑰", "https://openrouter.ai/keys")
        st.caption("申請後貼回上方框框即可使用超過 20 種免費模型。")

    st.divider()

    # 3. 第二層：選擇具體模型
    selected_model = st.selectbox("3. 選擇具體模型 ID：", MODEL_LIBRARY[selected_provider])
    
    st.info(f"當前模式：{selected_model}")

# --- 主畫面介面 ---
st.title("指令優化器")
st.caption("整合全球頂尖模型，為您的 Prompt 提供最強大的重構能力。")

raw_prompt = st.text_area("原始指令內容：", placeholder="請輸入您想優化的指令，例如：幫我寫個讀書計畫...", height=150)

if st.button("啟動跨平台優化引擎"):
    api_key = st.session_state["keys"].get(key_name)
    
    if not api_key:
        st.error(f"❌ 錯誤：請先配置 {selected_provider} 的 API 金鑰。")
    elif not raw_prompt:
        st.warning("請輸入內容以進行優化。")
    else:
        system_instruction = "你是一名專業提示詞工程師，將輸入轉化為[角色任務]、[背景資訊]、[具體指令]、[約束條件]四個維度。使用正體中文。"
        
        with st.spinner(f"正在透過 {selected_provider} 調度資源..."):
            try:
                # --- 核心路由邏輯 ---
                if "Gemini (原生)" in selected_provider:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content(f"{system_instruction}\n\n輸入：{raw_prompt}")
                    res_text = response.text

                elif "OpenRouter" in selected_provider:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res_text = response.choices[0].message.content

                elif "Groq" in selected_provider or "DeepSeek" in selected_provider:
                    base_urls = {"Groq (極速系列)": "https://api.groq.com/openai/v1", "DeepSeek (國產之光)": "https://api.deepseek.com"}
                    client = OpenAI(api_key=api_key, base_url=base_urls.get(selected_provider))
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res_text = response.choices[0].message.content

                elif "Claude" in selected_provider:
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=selected_model, max_tokens=2048, system=system_instruction,
                        messages=[{"role": "user", "content": raw_prompt}]
                    )
                    res_text = response.content[0].text

                # --- 渲染結果 ---
                st.divider()
                st.subheader("✨ 優化後的專業提示詞")
                st.code(res_text, language="markdown")
                st.markdown(res_text)

            except Exception as e:
                st.error(f"❌ 連線異常：{str(e)}")
                if "404" in str(e):
                    st.info("💡 提示：OpenRouter 模型 ID 可能已更新，請檢查官方列表或更換其他免費模型。")