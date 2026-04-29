import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="萬能提示詞優化器", layout="wide")

# 設定：從 Streamlit 的 Secrets 讀取 API Key (部署後會用到)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = ""

# --- 側邊欄 ---
with st.sidebar:
    st.title("⚙️ 設定")
    if not api_key:
        api_key = st.text_input("請輸入 Gemini API Key", type="password")
    st.info("本工具將幫助您優化提示詞。")

# --- 主畫面 ---
st.title("🚀 萬能提示詞優化器")
raw_prompt = st.text_area("請輸入原始提示詞：", placeholder="例如：幫我寫個簡單的行銷企劃")

if st.button("開始優化"):
    if not api_key:
        st.error("請提供 API Key！")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        system_instruction = "你是一名 AI 提示詞優化專家，請將使用者的輸入轉化為 [角色]、[背景]、[指令]、[約束] 四個維度。"
        
        with st.spinner("正在優化中..."):
            response = model.generate_content(f"{system_instruction}\n\n原始輸入：{raw_prompt}")
            st.subheader("✨ 優化後的建議指令：")
            st.markdown(response.text)