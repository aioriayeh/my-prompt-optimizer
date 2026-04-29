import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 頁面基本設定
st.set_page_config(page_title="全能 AI 指令轉接站", page_icon="🤖", layout="wide")

# --- 側邊欄：配置與記憶功能 ---
with st.sidebar:
    st.title("⚙️ 模型配置面板")
    
    # 1. 選擇服務商
    provider = st.radio("選擇 AI 服務商：", ["Google Gemini", "OpenAI ChatGPT", "Anthropic Claude"])
    
    st.divider()
    
    # 2. 動態顯示對應的金鑰輸入框
    # 讀取 Secrets 作為隱形回退值
    def_gemini = st.secrets.get("GEMINI_API_KEY", "")
    def_openai = st.secrets.get("OPENAI_API_KEY", "")
    def_claude = st.secrets.get("ANTHROPIC_API_KEY", "")

    if provider == "Google Gemini":
        st.session_state["active_key"] = st.text_input("Gemini API Key:", value=st.session_state.get("g_key", def_gemini), type="password")
        st.session_state["g_key"] = st.session_state["active_key"]
        model_name = st.selectbox("選擇模型:", ["models/gemini-2.5-flash", "models/gemini-1.5-pro", "models/gemini-flash-latest"])
        
    elif provider == "OpenAI ChatGPT":
        st.session_state["active_key"] = st.text_input("OpenAI API Key:", value=st.session_state.get("o_key", def_openai), type="password")
        st.session_state["o_key"] = st.session_state["active_key"]
        model_name = st.selectbox("選擇模型:", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"])
        
    elif provider == "Anthropic Claude":
        st.session_state["active_key"] = st.text_input("Claude API Key:", value=st.session_state.get("c_key", def_claude), type="password")
        st.session_state["c_key"] = st.session_state["active_key"]
        model_name = st.selectbox("選擇模型:", ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307"])

    st.divider()
    if st.session_state.get("active_key"):
        st.success(f"✅ {provider} 已就緒")
    else:
        st.warning(f"⚠️ 請輸入 {provider} 的金鑰")

# --- 主畫面介面 ---
st.title("🤖 全能 AI 指令優化器")
st.markdown(f"目前正在使用 **{provider}** 的 **{model_name}** 進行優化作業。")

raw_prompt = st.text_area("原始指令：", placeholder="輸入你想優化的內容...", height=150)

if st.button("開始跨模型優化"):
    current_key = st.session_state.get("active_key")
    
    if not current_key:
        st.error(f"❌ 偵測不到 {provider} 的 API 金鑰，請在左側面板配置。")
    elif not raw_prompt:
        st.warning("請輸入內容喔！")
    else:
        system_instruction = "你是一名專業的提示詞工程師，請將輸入轉化為 [角色任務]、[背景資訊]、[具體指令]、[約束條件] 四個維度。"
        
        with st.spinner(f"正在透過 {provider} 進行運算..."):
            try:
                # --- 分流處理邏輯 ---
                if provider == "Google Gemini":
                    genai.configure(api_key=current_key)
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(f"{system_instruction}\n\n輸入：{raw_prompt}")
                    result_text = response.text

                elif provider == "OpenAI ChatGPT":
                    client = OpenAI(api_key=current_key)
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    result_text = response.choices[0].message.content

                elif provider == "Anthropic Claude":
                    client = anthropic.Anthropic(api_key=current_key)
                    response = client.messages.create(
                        model=model_name,
                        max_tokens=2048,
                        system=system_instruction,
                        messages=[{"role": "user", "content": raw_prompt}]
                    )
                    result_text = response.content[0].text

                # --- 顯示結果 ---
                st.divider()
                st.subheader("✨ 優化結果")
                st.code(result_text, language="markdown")
                st.markdown(result_text)

            except Exception as e:
                st.error(f"⚠️ API 呼叫失敗：{str(e)}")