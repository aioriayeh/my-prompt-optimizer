# 🚀 萬能提示詞優化器 (Universal Prompt Optimizer)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://my-prompt-optimizer-ualuaimeahqqtvstsoirm2.streamlit.app/)

這是一個基於 **Streamlit** 與 **Google Gemini API** 開發的互動式 Web 應用程式。旨在幫助使用者將模糊、簡短的原始指令，自動轉化為結構化、精確且高品質的 AI 提示詞 (Prompt)。

## ✨ 核心特色

* **結構化優化邏輯**：自動將提示詞重構成「角色任務、背景資訊、具體指令、約束條件」四大維度，大幅提升 AI 輸出品質。
* **多模型自由切換**：支援最新的 **Gemini 2.5 Flash**、**Gemini 1.5 Pro** 等多種模型，使用者可根據需求調整推論強度。
* **靈活的 API 管理**：
    * **隱形回退機制**：預設使用開發者配置的 API Key，確保新手能立即上手。
    * **自訂金鑰輸入**：支援使用者輸入私有 API Key，並具備會話記憶功能，保護隱私且不佔用他人額度。
* **響應式介面**：採用 Streamlit 框架，支援電腦與行動裝置流暢操作。

## 🛠️ 技術棧 (Tech Stack)

* **Language**: Python 3.14+
* **Frontend**: Streamlit
* **AI Engine**: Google Generative AI (Gemini API)
* **Deployment**: Streamlit Cloud
* **Version Control**: Git / GitHub

## 🚀 快速開始

### 1. 獲取 Gemini API Key
在使用本工具前，建議先前往 [Google AI Studio](https://aistudio.google.com/) 申請免費的 API Key。

### 2. 在地端執行 (Local Execution)
如果你想在自己的電腦上執行此專案：

```bash
# 複製儲存庫
git clone https://github.com/aioriayeh/my-prompt-optimizer.git

# 進入資料夾
cd my-prompt-optimizer

# 安裝必要套件
pip install -r requirements.txt

# 啟動應用程式
streamlit run app.py
```

### 3. 配置秘密參數 (Secrets)
若要像雲端版本一樣自動讀取金鑰，請在專案根目錄建立 `.streamlit/secrets.toml` 檔案：
```toml
GEMINI_API_KEY = "你的_API_KEY"
```

## 📝 使用範例

**原始輸入：**
> 幫我寫個簡單的行銷計畫

**優化後指令：**
1.  **[角色任務]**：你是一位資深的行銷策略顧問...
2.  **[背景資訊]**：使用者需要針對特定產品制定初步行動方案...
3.  **[具體指令]**：請分析目標客群、選擇傳播渠道並制定三步驟執行計畫...
4.  **[約束條件]**：字數限制在 500 字內，語氣專業且具備說服力...

## 🔒 隱私與安全說明

* **金鑰安全**：本程式不設有任何後端資料庫。使用者在網頁介面輸入的 API Key 僅儲存在當前瀏覽器的會話 (Session State) 中，重新整理或關閉分頁後即失效，開發者無法獲取您的私密資訊。
* **開源透明**：所有代碼均公開透明，無任何惡意腳本。

## 🤝 貢獻與反饋

如果你有任何建議或發現 Bug，歡迎透過 GitHub Issues 提交回饋。

---
**開發者**：aioriayeh
**專案連結**：[aioriayeh/my-prompt-optimizer](https://github.com/aioriayeh/my-prompt-optimizer)

---