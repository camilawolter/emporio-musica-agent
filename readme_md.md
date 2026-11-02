# Empório da Música - AI Customer Support Agent

An intelligent, lightweight customer support agent built in Python for **Empório da Música**, a musical instruments retailer located in Campo Grande/MS.

## 🎯 Project Overview
This project provides an automated conversational assistant designed to handle routine customer inquiries, query product inventory/prices, check order status, enforce business rules, and answer store policy questions through a clean, modern web chat interface.

---

## 🏗️ Technical Architecture & Decisions

### 1. Agent Strategy & Architecture
* **Hybrid Tool Routing:** Uses native function calling combined with structured data querying (`Pandas` for CSV operations and a lightweight document reader for store policy PDFs).
* **Scope Control:** Enforces strict business scope boundaries (e.g., refusing accessories like cables, strings, picks, or amplifiers as mandated by Store Policy Section 1 & 7.1).

### 2. Model & Framework Choice
* **Language:** Python 3.10+
* **Framework:** Streamlit web framework integrated with the Groq API for ultra-fast, free inference and reliable function calling.
* **Model:** `openai/gpt-oss-120be` (via Groq API).
* **Data Retrieval:**
  * **Structured Data:** Pandas DataFrames loaded dynamically from `data/*.csv`.
  * **Unstructured Policy:** Text index derived from `data/politicas_da_loja.pdf`.

### 3. Interface & Session State Management
* **Interface:** Interactive Streamlit Web UI featuring a WhatsApp-style conversational chat layout.
* **State Management:** Uses `st.session_state` to maintain structured message history (role/content dictionaries) and function-calling contexts across browser rerenders.

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* Free Groq API Key ([console.groq.com](https://console.groq.com/))

### Installation & Execution
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/emporio-musica-agent.git
   cd emporio-musica-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key:**
   * **PowerShell (Windows):**
     ```powershell
     $env:GROQ_API_KEY="your-groq-api-key"
     ```
   * **Linux/macOS:**
     ```bash
     export GROQ_API_KEY="your-groq-api-key"
     ```

4. **Run the Streamlit Web Application:**
   ```bash
   python -m streamlit run app.py
   ```

---

## 🤖 AI Assistant & Tool Usage Disclosure
* **Code Generation & Structure:** AI coding assistants (e.g., Cursor / ChatGPT / Claude) were used to generate boilerplate code, format Markdown documentation, and structure sample test conversations. All business logic, prompt rules, and error handling were verified manually.

---

## ⚠️ Known Limitations & Future Improvements
1. **Vector Embeddings (RAG):** Future versions will integrate persistent vector databases (e.g., ChromaDB / FAISS) for dense semantic search over complex PDFs.
2. **Database Integration:** Transition CSV file reading to SQLite/PostgreSQL for scalable query execution under concurrent traffic.
3. **Multi-Channel Adapters:** Add a WhatsApp Webhook / Telegram Bot adapter for direct production deployment on customer channels.