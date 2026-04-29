import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="模型診斷器")
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    st.title("🔍 您的 API 可用模型清單")
    st.write("如果下方有出現清單，請複製帶有 'models/' 的名稱。")
    
    try:
        # 獲取所有支援生成內容的模型
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if available_models:
            for name in available_models:
                st.code(name)
            st.success("✅ 找到可用模型！請複製上方其中一個名稱替換到原本的程式碼中。")
        else:
            st.warning("⚠️ 雖然連線成功，但沒有找到可用的生成模型。")
            
    except Exception as e:
        st.error(f"❌ 無法獲取模型清單，錯誤訊息：{str(e)}")
        st.info("提示：這通常代表 API Key 權限不足，或是您的專案尚未在 AI Studio 啟用。")
else:
    st.error("❌ 找不到 API Key，請檢查 Streamlit Secrets 設定。")
