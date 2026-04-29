import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="萬能提示詞優化器", layout="wide")

# 1. 讀取 API Key (增加更強的防呆)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("❌ 找不到 API Key！請檢查 Streamlit Secrets 設定。")

st.title("🚀 萬能提示詞優化器")

with st.sidebar:
    st.title("⚙️ 設定")
    st.info("目前使用模型: gemini-1.5-flash")

raw_prompt = st.text_area("請輸入原始提示詞：", placeholder="例如：幫我寫個簡單的行銷企劃")

if st.button("開始優化"):
    if not raw_prompt:
        st.warning("請先輸入內容喔！")
    else:
        # 使用 models/ 前綴是解決 NotFound 的常見偏方
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        system_instruction = "你是一名 AI 提示詞優化專家，請將使用者的輸入轉化為 [角色任務]、[背景資訊]、[具體指令]、[約束條件] 四個維度。"
        
        with st.spinner("正在優化中..."):
            try:
                # 執行生成
                response = model.generate_content(f"{system_instruction}\n\n原始輸入：{raw_prompt}")
                st.subheader("✨ 優化後的建議指令：")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"⚠️ 發生錯誤：{str(e)}")
                st.info("提示：如果是 NotFound，請確認您的 API Key 是否在 Google AI Studio 顯示為 Active。")