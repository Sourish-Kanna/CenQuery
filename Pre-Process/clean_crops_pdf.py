import pdfplumber
import pandas as pd
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_PDF = "input/Crops.pdf"
OUTPUT_DIR = "output_normalized_crops"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "crops.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_crops_data(pdf_path):
    print(f"📖 Opening PDF: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        table = page.extract_table()
        
    if not table:
        print("❌ No table found.")
        return None

    df = pd.DataFrame(table)
    
    # Select specific columns based on your PDF structure
    target_indices = [0, 2, 5, 8, 11, 14]
    
    if df.shape[1] <= max(target_indices):
        print(f"⚠️ Table width ({df.shape[1]}) is smaller than expected.")
        return None

    df_clean = df.iloc[:, target_indices].copy()

    clean_headers = [
        "crop",
        "normal_area_dafw",
        "area_sown_2025_26",
        "area_sown_2024_25",
        "difference_area",
        "pct_increase_decrease"
    ]
    df_clean.columns = clean_headers

    # Clean Data Rows
    df_clean = df_clean.iloc[9:].reset_index(drop=True)
    df_clean = df_clean.replace(r'\n', ' ', regex=True)
    df_clean = df_clean[df_clean['crop'].notna() & (df_clean['crop'] != "")]
    
    # --- FIX: Force Numeric Conversion ---
    print("🔢 Converting metrics to Numeric (Float)...")
    numeric_cols = ["normal_area_dafw", "area_sown_2025_26", "area_sown_2024_25", "difference_area", "pct_increase_decrease"]
    
    for col in numeric_cols:
        # Clean up potential commas or spaces in numbers
        if df_clean[col].dtype == object:
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '', regex=False)
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0.0)

    return df_clean

if __name__ == "__main__":
    df_result = extract_crops_data(INPUT_PDF)
    
    if df_result is not None:
        df_result.to_csv(OUTPUT_CSV, index=False)
        print(f"\n💾 Saved Clean CSV to: {OUTPUT_CSV}")