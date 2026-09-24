# src/train_model.py
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

def build_features_and_train(cleaned_csv_path, model_output_path):
    print("⚙️ Loading cleaned data and engineering customer features...")
    df = pd.read_csv(cleaned_csv_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 1. Establish the business snapshot date (the last date in the dataset)
    snapshot_date = df['InvoiceDate'].max()
    print(f"📅 Business Snapshot Date: {snapshot_date.strftime('%Y-%m-%d')}")
    
    # 2. Aggregate transactions to Customer Level (RFM + Engagement)
    customer_df = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,  # Recency (Days since last order)
        'InvoiceNo': 'nunique',                                   # Frequency (Total orders placed)
        'TotalSpend': ['sum', 'mean'],                            # Monetary (Total spend & average order size)
        'Quantity': 'sum'                                         # Engagement (Total items bought)
    })
    
    # Flatten the hierarchical column index
    customer_df.columns = ['recency', 'frequency', 'total_spend', 'avg_order_value', 'total_items']
    customer_df = customer_df.reset_index()
    
    # 3. Define the Target Variable (Churn)
    # If a customer hasn't purchased in > 90 days, we label them as Churned (1), else Active (0)
    customer_df['churned'] = (customer_df['recency'] > 90).astype(int)
    
    print(f"📊 Dataset class balance: {customer_df['churned'].value_counts(normalize=True).to_dict()}")
    
    # 4. Features & Label Split
    # CRITICAL: We drop 'recency' and 'CustomerID' to prevent data leakage!
    X = customer_df[['frequency', 'total_spend', 'avg_order_value', 'total_items']]
    y = customer_df['churned']
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\n🏋️ Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("\n📈 Model Evaluation Report:")
    print(f"Accuracy Score: {accuracy_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC Score:  {roc_auc_score(y_test, y_prob):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # 6. Save the trained model binary
    os.makedirs(os.path.dirname(model_output_path), exist_ok=True)
    joblib.dump(model, model_output_path)
    print(f"\n💾 Model saved successfully to: {model_output_path}")

if __name__ == "__main__":
    CLEANED_DATA = os.path.join("data", "processed", "cleaned_retail.csv")
    MODEL_PATH = os.path.join("models", "churn_model.joblib")
    
    build_features_and_train(CLEANED_DATA, MODEL_PATH)
