#!/usr/bin/env python3
"""
Debug script to check data and models
"""
import pandas as pd
import os
from config import Config

def debug_data():
    """Debug data loading and processing"""
    config = Config()
    
    print("🔍 DEBUGGING CROP DASHBOARD")
    print("=" * 50)
    
    # Check if data files exist
    print("\n1. Checking Data Files:")
    print("-" * 30)
    
    data_files = [
        config.YIELD_FILE,
        config.PRODUCTION_FILE,
        config.AREA_FILE
    ]
    
    for file in data_files:
        file_path = os.path.join(config.RAW_DATA_DIR, file)
        exists = os.path.exists(file_path)
        print(f"   {file}: {'✅ EXISTS' if exists else '❌ MISSING'}")
        
        if exists:
            try:
                df = pd.read_csv(file_path)
                print(f"      Shape: {df.shape}")
                print(f"      Columns: {list(df.columns)[:5]}...")  # First 5 columns
                if 'Crop' in df.columns:
                    print(f"      Crops: {df['Crop'].unique()[:3]}...")  # First 3 crops
                if 'Season' in df.columns:
                    print(f"      Seasons: {df['Season'].unique()}")
            except Exception as e:
                print(f"      ❌ Error reading: {e}")
    
    # Check processed data
    print("\n2. Checking Processed Data:")
    print("-" * 30)
    processed_file = os.path.join(config.PROCESSED_DATA_DIR, config.MERGED_FILE)
    if os.path.exists(processed_file):
        try:
            df = pd.read_csv(processed_file)
            print(f"   ✅ Processed data exists: {df.shape}")
            print(f"   Unique crops: {df['Crop'].nunique()}")
            print(f"   Crops: {list(df['Crop'].unique())}")
            print(f"   Unique seasons: {df['Season'].nunique()}")
            print(f"   Seasons: {list(df['Season'].unique())}")
        except Exception as e:
            print(f"   ❌ Error reading processed data: {e}")
    else:
        print("   ❌ No processed data found")
    
    # Check models
    print("\n3. Checking Models:")
    print("-" * 30)
    model_file = config.MODEL_FILE
    if os.path.exists(model_file):
        try:
            import pickle
            with open(model_file, 'rb') as f:
                models = pickle.load(f)
            print("   ✅ Models loaded successfully")
            print(f"   Available keys: {list(models.keys())}")
            
            if 'crop_encoder' in models:
                crops = list(models['crop_encoder'].classes_)
                print(f"   Encoded crops: {crops}")
            
            if 'season_encoder' in models:
                seasons = list(models['season_encoder'].classes_)
                print(f"   Encoded seasons: {seasons}")
                
        except Exception as e:
            print(f"   ❌ Error loading models: {e}")
    else:
        print("   ❌ No models found")
    
    # Test model training
    print("\n4. Testing Data Processing:")
    print("-" * 30)
    try:
        from models.data_processor import DataProcessor
        processor = DataProcessor()
        merged_df = processor.load_and_process_data()
        
        if merged_df is not None:
            print(f"   ✅ Data processing successful: {merged_df.shape}")
            print(f"   Available crops: {merged_df['Crop'].unique()}")
            print(f"   Available seasons: {merged_df['Season'].unique()}")
        else:
            print("   ❌ Data processing failed")
            
    except Exception as e:
        print(f"   ❌ Error in data processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_data()