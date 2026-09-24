# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np
import os

app = FastAPI(
    title="🛒 ShopInsight API Platform", 
    description="Production-ready predictive intelligence backend for e-commerce.",
    version="1.0"
)

# Enable CORS (Cross-Origin Resource Sharing) so our React frontend can query us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded resources
MODEL_PATH = os.path.join("..", "models", "churn_model.joblib")
DATA_PATH = os.path.join("..", "data", "processed", "cleaned_retail.csv")

model = None
df = None

@app.on_event("startup")
def load_resources():
    global model, df
    print("⏳ Loading machine learning resources...")
    try:
        # Load pre-trained Random Forest
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            print("✅ Churn Model loaded successfully.")
        else:
            # Fallback path if running from the root instead of the api folder
            fallback_model = os.path.join("models", "churn_model.joblib")
            model = joblib.load(fallback_model)
            print("✅ Churn Model loaded successfully (from fallback).")
            
        # Load cleaned transaction database
        if os.path.exists(DATA_PATH):
            df = pd.read_csv(DATA_PATH)
            print(f"✅ Transaction Database loaded ({len(df):,} records).")
        else:
            fallback_data = os.path.join("data", "processed", "cleaned_retail.csv")
            df = pd.read_csv(fallback_data)
            print(f"✅ Transaction Database loaded ({len(df):,} records from fallback).")
            
    except Exception as e:
        print(f"❌ Error loading startup resources: {str(e)}")
        raise RuntimeError(f"Startup failed: {e}")

# Define the Pydantic data schema for prediction input requests
class ChurnInputSchema(BaseModel):
    frequency: int = Field(..., gt=0, description="Total number of historical orders placed")
    total_spend: float = Field(..., gt=0.0, description="Total historical spending amount ($)")
    avg_order_value: float = Field(..., gt=0.0, description="Average monetary value per order ($)")
    total_items: int = Field(..., gt=0, description="Total number of items purchased historically")

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "ShopInsight API Platform",
        "features_loaded": model is not None and df is not None
    }

@app.get("/api/analytics")
def get_analytics_metrics():
    """Generates real-time KPIs and Top Products directly from our dataset."""
    if df is None:
        raise HTTPException(status_code=503, detail="Analytics database not loaded.")
    
    try:
        # 1. Compute High-Level KPIs
        total_revenue = float(df['TotalSpend'].sum())
        total_orders = int(df['InvoiceNo'].nunique())
        unique_customers = int(df['CustomerID'].nunique())
        avg_order_val = float(total_revenue / total_orders)
        
        # 2. Get Top 5 Best-Selling Products by Revenue
        top_products_series = df.groupby('Description')['TotalSpend'].sum().nlargest(5)
        top_products = [
            {"product": name, "revenue": round(float(val), 2)}
            for name, val in top_products_series.items()
        ]
        
        return {
            "kpis": {
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "unique_customers": unique_customers,
                "avg_order_value": round(avg_order_val, 2)
            },
            "top_products": top_products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate analytics: {str(e)}")

@app.post("/api/predict")
def predict_churn(input_data: ChurnInputSchema):
    """Processes customer data through the Random Forest to predict churn probability."""
    if model is None:
        raise HTTPException(status_code=503, detail="Machine Learning model not loaded.")
    
    try:
        # Features must be in the exact order trained: [frequency, total_spend, avg_order_value, total_items]
        features = np.array([[
            input_data.frequency,
            input_data.total_spend,
            input_data.avg_order_value,
            input_data.total_items
        ]])
        
        # Get probability of class 1 (Churned)
        probability = model.predict_proba(features)[0][1]
        prediction = int(model.predict(features)[0])
        
        return {
            "churn_risk": "HIGH" if prediction == 1 or probability >= 0.50 else "LOW",
            "probability": round(float(probability) * 100, 2),
            "recommendation": (
                "Alert: Highly inactive customer. Target with retention email campaign or coupon."
                if probability >= 0.50 else 
                "Healthy: Customer is regularly engaged. Standard marketing funnel applies."
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline failed: {str(e)}")

