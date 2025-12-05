import os
import shutil
import pandas as pd

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "unified_outputs")

SOURCES = {
    "output_normalized_healthcare": [
        "regions.csv",          
        "healthcare_stats.csv",
        "tru.csv"               
    ],
    "output_normalized_population": [
        "population_stats.csv",
    ],
    "output_normalized_education": [
        "education_stats.csv"   # FIX: Updated filename
    ],
    "output_normalized_religion": [
        "religion_stats.csv",
        "religions.csv"
    ],
    "output_normalized_occupation": [
        "occupation_stats.csv",
        "age_groups.csv"
    ],
    "output_normalized_language": [
        "language_stats.csv",
        "languages.csv"
    ],
    "output_normalized_crops": [
        "crops.csv"
    ]
}

def consolidate():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created directory: {OUTPUT_DIR}")

    print("-" * 40)

    copied_count = 0
    for folder, files in SOURCES.items():
        src_folder_path = os.path.join(BASE_DIR, folder)
        
        if not os.path.exists(src_folder_path):
            alt_folder = folder.replace("_", " ")
            alt_path = os.path.join(BASE_DIR, alt_folder)
            if os.path.exists(alt_path):
                src_folder_path = alt_path
            else:
                print(f"⚠️  Warning: Source folder not found: {folder}")
                continue

        for filename in files:
            src_file = os.path.join(src_folder_path, filename)
            dst_file = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"✅ Copied: {filename:<25} (from {os.path.basename(src_folder_path)})")
                copied_count += 1
            else:
                print(f"❌ Missing: {filename:<25} (in {os.path.basename(src_folder_path)})")

    readme_path = os.path.join(OUTPUT_DIR, "README.txt")
    with open(readme_path, "w") as f:
        f.write("UNIFIED CENSUS DATA STAGING AREA\n")
    
    print("-" * 40)
    print(f"🎉 Success! {copied_count} files consolidated into 'unified_outputs/'.")

if __name__ == "__main__":
    consolidate()