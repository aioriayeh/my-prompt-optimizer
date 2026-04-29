import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import anthropic

# 頁面配置
st.set_page_config(page_title="萬能 AI 指令中心", page_icon="🌐", layout="wide")

# --- 初始化 Session State ---
if "api_keys" not in st.session_state:
    st.session_state["api_keys"] = {}

# --- 側邊欄：進階模型選單 ---
with st.sidebar:
    st.title("🛡️ 模型總署")
    
    # 分組選單配置
    provider_groups = {
        "主流巨頭": ["Google Gemini", "OpenAI ChatGPT", "Anthropic Claude"],
        "模型聚合器": ["OpenRouter (推薦)", "Groq (極速)", "Together AI"],
        "獨立服務商": ["DeepSeek", "Mistral AI", "Perplexity", "Perplexity Sonar"]
    }
    
    # 扁平化列表用於 selectbox
    all_providers = []
    for group, p_list in provider_groups.items():
        all_providers.extend(p_list)

    selected_provider = st.selectbox("請選擇服務提供商：", all_providers, index=0)
    
    st.divider()

    # 動態顯示金鑰輸入與獲取引導
    current_key_name = f"{selected_provider}_key"
    default_key = st.secrets.get(current_key_name, "")
    
    user_key = st.text_input(
        f"輸入 {selected_provider} API Key:",
        value=st.session_state["api_keys"].get(current_key_name, default_key),
        type="password"
    )
    st.session_state["api_keys"][current_key_name] = user_key

    # --- OpenRouter 特別引導 (解決您的需求) ---
    if selected_provider == "OpenRouter (推薦)" and not user_key:
        st.info("💡 尚未擁有金鑰？OpenRouter 提供許多免費模型！")
        st.link_button("👉 前往獲取免費 API Key", "https://openrouter.ai/keys")

    # 模型細項選擇 (範例，可根據需求擴充)
    model_mapping = {
        "Google Gemini": ["models/gemini-2.5-flash", "models/gemini-1.5-pro"],
        "OpenAI ChatGPT": ["gpt-4o", "gpt-4o-mini"],
        "Anthropic Claude": ["claude-3-5-sonnet-20240620"],
        "OpenRouter (推薦)": ["google/gemini-flash-1.5", "meta-llama/llama-3.1-8b-instruct:free"],
        "Groq (極速)": ["llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
        "DeepSeek": ["deepseek-chat", "deepseek-coder"]
    }
    
    selected_model = st.selectbox("選擇具體模型：", model_mapping.get(selected_provider, ["default"]))

# --- 主畫面介面 ---
st.title("🚀 萬能指令優化器：專業版")
st.caption(f"當前連線：{selected_provider} / {selected_model}")

raw_prompt = st.text_area("原始指令：", placeholder="輸入你想優化的內容...", height=150)

if st.button("啟動跨平台優化"):
    api_key = st.session_state["api_keys"].get(current_key_name)
    
    if not api_key:
        st.error(f"❌ 缺少 {selected_provider} 的金鑰，優化無法啟動。")
    elif not raw_prompt:
        st.warning("請先輸入一點內容。")
    else:
        system_instruction = "你是一名提示詞工程師，將輸入轉化為角色、背景、指令、約束四個維度。使用正體中文。"
        
        with st.spinner(f"正在連線至 {selected_provider}..."):
            try:
                # --- 多路分流處理器 ---
                if selected_provider == "Google Gemini":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content(f"{system_instruction}\n\n輸入：{raw_prompt}")
                    res = response.text

                elif selected_provider in ["OpenAI ChatGPT", "Groq (極速)", "DeepSeek"]:
                    # 這些都相容 OpenAI 格式，只需換 base_url
                    urls = {
                        "OpenAI ChatGPT": "https://api.openai.com/v1",
                        "Groq (極速)": "https://api.groq.com/openai/v1",
                        "DeepSeek": "https://api.deepseek.com"
                    }
                    client = OpenAI(api_key=api_key, base_url=urls.get(selected_provider))
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res = response.choices[0].message.content

                elif selected_provider == "OpenRouter (推薦)":
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[{"role": "system", "content": system_instruction}, {"role": "user", "content": raw_prompt}]
                    )
                    res = response.choices[0].message.content

                elif selected_provider == "Anthropic Claude":
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model=selected_model, max_tokens=2048, system=system_instruction,
                        messages=[{"role": "user", "content": raw_prompt}]
                    )
                    res = response.content[0].text

                # 輸出結果
                st.divider()
                st.subheader("✨ 優化指令")
                st.code(res, language="markdown")
                st.markdown(res)

            except Exception as e:
                st.error(f"連線異常：{str(e)}")