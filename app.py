import streamlit as st
import google.generativeai as genai

# 基本頁面設定
st.set_page_config(page_title="萬能提示詞優化器 V2", page_icon="🚀", layout="wide")

# --- 側邊欄：配置區 ---
with st.sidebar:
    st.title("⚙️ 控制面板")
    
    # 1. API Key 輸入區 (使用 session_state 記憶)
    # 若系統 Secrets 有預設值，則作為預設顯示
    default_key = st.secrets.get("GEMINI_API_KEY", "")
    
    user_api_key = st.text_input(
        "請輸入您的 Gemini API Key：",
        value=st.session_state.get("saved_key", default_key),
        type="password",
        help="金鑰僅會儲存在此對話視窗中，重新整理後需視情況重新確認。"
    )
    
    # 儲存金鑰到 session_state
    st.session_state["saved_key"] = user_api_key

    # 2. 模型切換選單 (根據診斷清單設定)
    model_option = st.selectbox(
        "選擇 AI 模型：",
        options=[
            "models/gemini-2.5-flash", 
            "models/gemini-1.5-pro", 
            "models/gemini-1.5-flash",
            "models/gemini-flash-latest"
        ],
        index=0,
        help="Flash 速度較快，Pro 邏輯推論能力較強。"
    )

    st.divider()
    if user_api_key:
        st.success("✅ API 已就緒")
    else:
        st.warning("⚠️ 請輸入 API Key 以啟動功能")

# --- 主畫面設計 ---
st.title("🚀 萬能提示詞優化器")
st.markdown("現在您可以自由切換不同的 Gemini 模型，並使用自己的 API Key 進行優化。")

# 配置 API
if user_api_key:
    genai.configure(api_key=user_api_key)

# 輸入區
raw_prompt = st.text_area("請輸入原始提示詞：", placeholder="例如：幫我寫個簡單的行銷企劃", height=150)

if st.button("開始精煉指令"):
    if not user_api_key:
        st.error("❌ 請先在左側欄位輸入 API Key！")
    elif not raw_prompt:
        st.warning("請先輸入內容喔！")
    else:
        with st.spinner(f"正在使用 {model_option} 進行深度優化..."):
            try:
                # 建立模型實例
                model = genai.GenerativeModel(model_option)
                
                system_instruction = (
                    "你是一名專業的提示詞工程師 (Prompt Engineer)。"
                    "請將使用者的輸入轉化為結構化指令，包含以下維度：\n"
                    "1. [角色任務]：定義專業身分。\n"
                    "2. [背景資訊]：提供必要的情境。\n"
                    "3. [具體指令]：拆解明確的操作步驟。\n"
                    "4. [約束條件]：規定字數、語氣、格式，一律使用正體中文回答並採正向表述。"
                )
                
                response = model.generate_content(f"{system_instruction}\n\n原始輸入：{raw_prompt}")
                
                st.divider()
                st.subheader("✨ 優化後的專業提示詞：")
                st.info(f"（當前模型：{model_option}）")
                st.code(response.text, language="markdown")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"⚠️ 執行失敗：{str(e)}")
                st.info("若出現 404，請嘗試切換到其他模型。")