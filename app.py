import streamlit as st
import google.generativeai as genai

# 基本頁面設定
st.set_page_config(page_title="萬能提示詞優化器", page_icon="🚀", layout="wide")

# 1. 安全讀取 API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("❌ 找不到 API Key！請檢查 Streamlit Secrets 設定。")

# --- 介面設計 ---
st.title("🚀 萬能提示詞優化器")
st.markdown("本工具將幫助您將模糊的原始指令，轉化為 AI 易於精確判斷的專業提示詞。")

with st.sidebar:
    st.title("⚙️ 系統狀態")
    st.success("API 連線正常")
    st.info("目前使用模型：Gemini 2.5 Flash")

# 輸入區
raw_prompt = st.text_area("請輸入原始提示詞：", placeholder="例如：幫我寫個簡單的行銷企劃", height=150)

# 執行按鈕
if st.button("開始精煉指令"):
    if not raw_prompt:
        st.warning("請先輸入內容喔！")
    elif not api_key:
        st.error("請設定 API Key 後再執行。")
    else:
        # 使用診斷清單中確認存在的精確名稱
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # 專家優化逻辑
        system_instruction = (
            "你是一名專業的提示詞工程師 (Prompt Engineer)。"
            "請將使用者的輸入轉化為結構化指令，包含以下維度：\n"
            "1. [角色任務]：定義專業身分。\n"
            "2. [背景資訊]：提供必要的情境。\n"
            "3. [具體指令]：拆解明確的操作步驟。\n"
            "4. [約束條件]：規定字數、語氣、格式，一律使用正向表述。\n"
            "請使用正體中文回答。"
        )
        
        with st.spinner("AI 正在深度思考並重構指令..."):
            try:
                # 執行 API 調用
                response = model.generate_content(f"{system_instruction}\n\n原始輸入：{raw_prompt}")
                
                st.divider()
                st.subheader("✨ 優化後的專業提示詞：")
                st.info("您可以直接複製下方內容供其他 AI 模型使用")
                st.code(response.text, language="markdown")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"⚠️ 執行失敗：{str(e)}")
