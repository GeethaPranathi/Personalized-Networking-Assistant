# 🤝 Personalized Network Assistant

> **AI-powered conversation starter generator** that extracts themes from networking event descriptions, generates tailored icebreakers using GPT-2, and verifies facts via Wikipedia — all wrapped in a sleek dark-themed web interface.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)

---
## 🚀 Live Demo
**https://personalized-networking-assistant-mzjnhmehchghqniqhlrbg6.streamlit.app/**

---

## 📖 Project Documentation

We have moved the detailed documentation, API reference, architecture explanation, and technical guidelines to a separate file:

👉 **[Read the Full Documentation here](documentation.md)**

---

## ⚡ Quick Start

### 1. Setup Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
# Install deps
pip install -r requirements.txt
```

### 2. Run Backend (Terminal 1)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run Frontend (Terminal 2)
```bash
streamlit run frontend/streamlit_app.py
```

Access the web interface at **http://localhost:8501**!

---

## 🧪 Run Tests
```bash
pytest tests/ -v
```

---

## 👥 Authors
- **GeethaPranathi** — [GitHub Profile](https://github.com/GeethaPranathi)
