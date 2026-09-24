# src/clean_data.py
import pandas as pd
import os

def clean_ecommerce_data(input_path, output_path):
    print("🧹 Starting Data Cleaning Pipeline...")
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Raw file not found: {input_path}")
    
    print("📖 Reading Excel file with calamine...")
    df = pd.read_excel(input_path, engine='calamine')
    initial_rows = len(df)
    print(f"📊 Loaded {initial_rows:,} raw transactions.")
    
    # Clean rows missing CustomerID
    df_clean = df.dropna(subset=['CustomerID']).copy()
    df_clean['CustomerID'] = df_clean['CustomerID'].astype(int)
    
    # Filter for valid positive transactions
    df_clean = df_clean[(df_clean['Quantity'] > 0) & (df_clean['UnitPrice'] > 0)]
    
    # Clean descriptions and compute Total Spend
    df_clean['Description'] = df_clean['Description'].astype(str).str.strip()
    df_clean['TotalSpend'] = df_clean['Quantity'] * df_clean['UnitPrice']
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_clean.to_csv(output_path, index=False)
    
    final_rows = len(df_clean)
    print(f"✅ Clean CSV generated successfully with {final_rows:,} rows!")

if __name__ == "__main__":
    RAW_PATH = os.path.join("data", "raw", "Online Retail.xlsx")
    PROCESSED_PATH = os.path.join("data", "processed", "cleaned_retail.csv")
    clean_ecommerce_data(RAW_PATH, PROCESSED_PATH)
