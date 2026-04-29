import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 頁面配置
st.set_page_config(page_title="萬能 AI 指令中心 V3", page_icon="🌐", layout="wide")

# --- 核心模型資料庫 (更新 OpenRouter 2026 最新 ID) ---
MODEL_LIBRARY = {
    "OpenRouter (免費推薦)": [
        "google/gemini-2.0-flash-exp:free",      # 目前最推薦的免費模型
        "google/gemini-flash-1.5-8b",            # 去掉 :free 試試看
        "google/gemini-flash-1.5-8b:free", 
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/pixtral-12b:free",
        "手動輸入模型 ID"                        # 新增：讓使用者自定義
    ],
    "Google Gemini (原生)": [
        "models/gemini-2.5-flash", 
        "models/gemini-1.5-pro"
    ],
    "Groq (極速系列)": [
        "llama-3.1-70b-versatile", 
        "gemma2-9b-it"
    ],
    "OpenAI / Claude": [
        "gpt-4o-mini", 
        "claude-3-5-sonnet-20240620"
    ]
}

# --- 側邊欄設計 ---
with st.sidebar:
    st.title("🛡️ 資源調度中心")
    
    # 1. 選擇服務商
    selected_provider = st.selectbox("1. 選擇 API 服務來源：", list(MODEL_LIBRARY.keys()))
    
    # 2. 金鑰管理 (Session State 記憶)
    if "keys" not in st.session_state:
        st.session_state["keys"] = {}
        
    key_name = f"{selected_provider}_key"
    user_key = st.text_input(
        f"2. 輸入 {selected_provider} 金鑰：",
        value=st.session_state["keys"].get(key_name, st.secrets.get(key_name, "")),
        type="password"
    )
    st.session_state["keys"][key_name] = user_key

    # OpenRouter 申請引導
    if "OpenRouter" in selected_provider and not user_key:
        st.info("💡 尚未輸入金鑰？")
        st.link_button("👉 免費獲取 OpenRouter API Key", "https://openrouter.ai/keys")

    st.divider()

    # 3. 模型選擇邏輯
    temp_selected_model = st.selectbox("3. 選擇具體模型：", MODEL_LIBRARY[selected_provider])
    
    # 如果選擇手動輸入
    if temp_selected_model == "手動輸入模型 ID":
        selected_model = st.text_input("請輸入 OpenRouter 模型 ID：", placeholder="例如：google/gemini-2.0-pro-exp-02-05:free")
    else:
        selected_model = temp_selected_model

    st.caption(f"當前路徑：{selected_model}")

# --- 主畫面介面 ---
st.title("萬能指令優化器")
st.caption("透過不同的模型特性，將您的想法轉化為高品質提示詞。")

raw_prompt = st.text_area("原始指令內容：", placeholder="請輸入您想優化的指令...", height=150)

if st.button("執行優化"):
    api_key = st.session_state["keys"].get(key_name)
    
    if not api_key:
        st.error(f"❌ 請先輸入 {selected_provider} 的金鑰。")
    elif not selected_model:
        st.warning("請選擇或輸入模型 ID。")
    elif not raw_prompt:
        st.warning("請輸入指令。")
    else:
        system_instruction = "你是一名專業提示詞工程師，將輸入轉化為[角色任務]、[背景資訊]、[具體指令]、[約束條件]四個維度。使用正體中文。"
        
        with st.spinner(f"正在連線至 {selected_provider}..."):
            try:
                # --- 多路路由邏輯 ---
                if "Gemini (原生)" in selected_provider:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content(f"{system_instruction}\n\n輸入：{raw_prompt}")
                    res_text = response.text

                elif "OpenRouter" in selected_provider:
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                    # OpenRouter 規範：建議加入 HTTP-Referer 與 Site-Name
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}],
                        extra_headers={
                            "HTTP-Referer": "https://streamlit.io", 
                            "X-Title": "Prompt Optimizer"
                        }
                    )
                    res_text = response.choices[0].message.content

                elif "Groq" in selected_provider:
                    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
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

                # 顯示結果
                st.divider()
                st.subheader("✨ 優化完成")
                st.code(res_text, language="markdown")
                st.markdown(res_text)

            except Exception as e:
                st.error(f"❌ 連線異常：{str(e)}")
                if "404" in str(e):
                    st.info("💡 解決方案：請試著切換模型（例如 Gemini 2.0 Flash），或到 OpenRouter 官網確認該模型 ID 是否有變。")