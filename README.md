# AI 指令優化工具 (AI Prompt Optimizer)

本專案是一個基於 Streamlit 框架開發的多模型指令優化平台。旨在協助使用者將模糊、不完整的原始指令（Prompt），透過全球頂尖的語言模型（LLM）轉化為結構化、高精確度的專業指令，內容涵蓋角色任務、背景資訊、具體指令與約束條件四大維度。

## 核心功能

* 多服務商整合：支援 Google Gemini、OpenRouter、OpenAI、Anthropic、Groq 與 DeepSeek 等主流 API 介面。
* 動態模型配置：提供預設熱門模型選單，並支援「自定義輸入」模型 ID 功能。當廠商更新模型名稱時，使用者可手動修正 ID，無需改動原始碼。
* 雙重結果輸出：
    * 指令複製 (Code)：提供純文字區塊，內建複製按鈕，確保擷取的指令不帶格式文字。
    * 結果預覽 (Markdown)：視覺化呈現排版後的結果，方便確認結構與內容。
* 智慧錯誤引導：當發生連線失敗或模型 ID 錯誤（404）時，系統將自動提供該服務商的官方模型清單連結。
* 安全與隱私：所有 API 金鑰均儲存於當前會話（Session State），不記錄於後端伺服器，關閉網頁後自動清除。

## 使用指南

1. 配置服務商：在側邊欄選擇欲使用的 AI 服務提供商。
2. 輸入金鑰：填入對應服務商的 API Key（系統亦支援讀取 Streamlit Secrets 設定）。
3. 選取模型：從選單中挑選預設模型，或選擇「自定義輸入」並手動填入精確的模型 ID。
4. 輸入指令：在主畫面的文字區域輸入欲優化的原始內容。
5. 執行優化：點擊「執行優化」按鈕進行運算。
6. 擷取結果：優化完成後，可於「指令複製」分頁點擊按鈕獲取指令。

## 本地端部署

請確保您的電腦已安裝 Python 3.9 或以上版本。

1. 複製儲存庫：
   git clone https://github.com/您的帳號/專案名稱.git

2. 安裝必要套件：
   pip install streamlit google-generativeai openai anthropic

3. 啟動應用程式：
   streamlit run app.py

## 技術架構與安全說明

* 介面架構：採用 Streamlit 作為前端介面，並透過 CSS 淨化 UI 元素，確保極簡視覺體驗。
* 資料隔離：不同使用者之間的會話完全隔離，金鑰與輸入內容互不干涉。
* 異常處理：針對模型 API 的常見錯誤（如額度限制、路徑錯誤）設有攔截機制，提升系統魯棒性。

## 資源清單

若需查詢最新模型 ID，請參閱以下連結：

* Google AI Studio: https://aistudio.google.com/
* OpenRouter Models: https://openrouter.ai/models
* OpenAI Models: https://platform.openai.com/docs/models
* Anthropic Models: https://docs.anthropic.com/en/docs/about-claude/models

---
開發者：aioriayeh
專案版本：2026 穩定版