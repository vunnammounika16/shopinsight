# 🛒 ShopInsight: E-Commerce Intelligence & ML Prediction Platform

ShopInsight is an end-to-end customer analytics and predictive intelligence system. It transforms raw, high-volume transactional records into actionable business KPIs and real-time customer churn risk predictions through an interactive, modern web dashboard.

---

## 📌 Key Takeaway (System Impact)
> **Product over Notebooks:** Instead of leaving this model trapped inside a Jupyter notebook, ShopInsight serves it as a live predictive service (FastAPI) paired with a reactive dashboard (React/Vite). This is a production-ready application demonstrating complete full-stack machine learning engineering capabilities.

---

## 🏗️ System Architecture

The platform is designed with modularity and separation of concerns in mind:

```text
                      SHOPINSIGHT PLATFORM
                  
                     ┌───────────────┐
                     │ React (Vite)  │ <--- Interactive Dashboard (Vercel)
                     └───────┬───────┘
                             │
                        JSON API/CORS
                             │
                             ▼
                     ┌───────────────┐
                     │    FastAPI    │ <--- Predictive Engine (Render)
                     └───────┬───────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
     ┌───────────────┐ ┌───────────┐ ┌───────────────┐
     │  Cleaned CSV  │ │ ML Model  │ │   Calamine    │
     │  Database     │ │ (RF Model)│ │  Excel Loader │
     └───────────────┘ └───────────┘ └───────────────┘


---

## 🚀 Key Engineering Features

* 🧹 **Messy Data Cleaning Pipeline:** Built a custom preprocessing script using the Rust-based `calamine` engine to clean and optimize 540,000+ raw transactional records down to 397,884 production-ready records in seconds.
* ⚙️ **RFM Feature Engineering:** Automatically aggregates transaction-level records to the customer level, generating Recency, Frequency, Monetary (RFM), and purchase quantity metrics without data leakage.
* 🧠 **Predictive Churn Engine:** Trained an optimized Random Forest Classifier to identify customer churn risk, yielding a strong **0.7711 ROC-AUC** and **70.85% Accuracy**.
* ⚡ **High-Performance API Backend:** Developed a REST API with FastAPI featuring automated input schema validation (via Pydantic) and real-time model inference in under **50ms**.
* 🎨 **Interactive User Interface:** Designed a clean, responsive single-page dashboard using React, Vite, and Recharts to display real-time sales KPIs and query the churn model on live parameters.

---

## 📊 Dataset Overview & Baseline Metrics

The platform processes the real-world **UCI Machine Learning Online Retail Dataset** (UK-based non-store retail transactions):

| Metric | Value | Description |
|---|---|---|
| **Raw Transaction Volume** | 541,909 rows | Original messy transaction logs. |
| **Pristine Cleaned Records** | 397,884 rows | Filtered for valid CustomerIDs, positive unit prices, and quantities. |
| **Total Revenue Analyzed** | $8,911,407.90 | Cumulative transactional sales. |
| **Total Orders Processed** | 18,536 | Unique invoices placed. |
| **Unique Customers Served** | 4,338 | Unique buyers modeled for predictive churn. |

---

## 📦 Directory Structure

```text
shopinsight/
├── api/
│   ├── main.py            # FastAPI backend & predictive endpoints
│   ├── models.py          # Database schema structures
│   └── schemas.py         # Pydantic input schemas (Type safety)
├── data/
│   ├── raw/               # Pristine raw input Excel workbook (Git ignored)
│   └── processed/         # Highly optimized processed CSV database
├── src/
│   ├── clean_data.py      # Automated high-performance cleaning pipeline
│   └── train_model.py     # RFM engineering & Random Forest training
├── models/
│   └── churn_model.joblib # Serialized Random Forest binary
├── frontend/              # React frontend workspace (Vite + Recharts)
├── download_dataset.py    # Robust, stream-based dataset downloader
└── requirements.txt       # Unified Python dependencies
