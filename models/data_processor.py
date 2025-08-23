import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import os
from config import Config

class DataProcessor:
    def __init__(self):
        self.config = Config()
        self.le_crop = LabelEncoder()
        self.le_season = LabelEncoder()
        self.scaler_yield = StandardScaler()
        self.scaler_production = StandardScaler()
        
    def melt_dataframe(self, df, value_name):
        """Convert wide format to long format"""
        year_cols = [col for col in df.columns if col not in ['Crop', 'Season']]
        
        melted = pd.melt(df, 
                        id_vars=['Crop', 'Season'], 
                        value_vars=year_cols,
                        var_name='Year_Column', 
                        value_name=value_name)
        
        # Extract year from column name (e.g., 'Yield-2015-16' -> 2015)
        melted['Year'] = melted['Year_Column'].str.extract(r'(\d{4})-\d{2}').iloc[:, 0].astype(int)
        melted = melted.drop('Year_Column', axis=1)
        melted[value_name] = pd.to_numeric(melted[value_name], errors='coerce')
        
        return melted
    
    def load_and_process_data(self):
        """Load and process all datasets"""
        try:
            print("📊 Loading datasets...")
            # Load datasets
            yield_df = pd.read_csv(os.path.join(self.config.RAW_DATA_DIR, self.config.YIELD_FILE))
            production_df = pd.read_csv(os.path.join(self.config.RAW_DATA_DIR, self.config.PRODUCTION_FILE))
            area_df = pd.read_csv(os.path.join(self.config.RAW_DATA_DIR, self.config.AREA_FILE))
            
            print(f"  - Yield data: {yield_df.shape}")
            print(f"  - Production data: {production_df.shape}")
            print(f"  - Area data: {area_df.shape}")
            
            print("🔄 Transforming to long format...")
            # Transform to long format
            yield_long = self.melt_dataframe(yield_df, 'Yield')
            production_long = self.melt_dataframe(production_df, 'Production')
            area_long = self.melt_dataframe(area_df, 'Area')
            
            print("🔗 Merging datasets...")
            # Merge datasets
            merged_df = yield_long.merge(production_long, on=['Crop', 'Season', 'Year'], how='outer')
            merged_df = merged_df.merge(area_long, on=['Crop', 'Season', 'Year'], how='outer')
            
            print(f"  - Merged shape: {merged_df.shape}")
            
            # Remove rows where all target variables are missing
            merged_df = merged_df.dropna(subset=['Yield', 'Production', 'Area'], how='all')
            print(f"  - After removing empty rows: {merged_df.shape}")
            
            # Clean data - remove rows with missing critical values
            initial_size = len(merged_df)
            merged_df = merged_df.dropna(subset=['Crop', 'Season', 'Year'])
            print(f"  - After removing missing Crop/Season/Year: {len(merged_df)}")
            
            print("⚙️ Feature engineering...")
            # Feature engineering
            merged_df['Crop_encoded'] = self.le_crop.fit_transform(merged_df['Crop'])
            merged_df['Season_encoded'] = self.le_season.fit_transform(merged_df['Season'])
            
            # Handle division by zero in productivity calculation
            merged_df['Productivity'] = np.where(
                merged_df['Area'] > 0, 
                merged_df['Production'] / merged_df['Area'], 
                0
            )
            
            # Normalize years from 2015 (baseline year)
            merged_df['Year_normalized'] = merged_df['Year'] - 2015
            
            print(f"✅ Processing complete! Final shape: {merged_df.shape}")
            print(f"  - Unique crops: {merged_df['Crop'].nunique()}")
            print(f"  - Unique seasons: {merged_df['Season'].nunique()}")
            print(f"  - Year range: {merged_df['Year'].min()}-{merged_df['Year'].max()}")
            
            # Save processed data
            os.makedirs(self.config.PROCESSED_DATA_DIR, exist_ok=True)
            processed_path = os.path.join(self.config.PROCESSED_DATA_DIR, self.config.MERGED_FILE)
            merged_df.to_csv(processed_path, index=False)
            print(f"💾 Processed data saved to: {processed_path}")
            
            return merged_df
            
        except Exception as e:
            print(f"❌ Error in data processing: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def prepare_features(self, df):
        """Prepare features for modeling"""
        print("🎯 Preparing features for modeling...")
        
        feature_columns = ['Crop_encoded', 'Season_encoded', 'Area', 'Year_normalized']
        
        # Clean data - only keep rows with both yield and production data
        model_df = df.dropna(subset=['Yield', 'Production']).copy()
        print(f"  - Data with Yield & Production: {len(model_df)}")
        
        X = model_df[feature_columns].copy()
        y_yield = model_df['Yield'].copy()
        y_production = model_df['Production'].copy()
        
        # Remove rows with missing features
        mask_complete = ~X.isnull().any(axis=1)
        
        X_clean = X[mask_complete]
        y_yield_clean = y_yield[mask_complete]
        y_production_clean = y_production[mask_complete]
        
        print(f"  - Complete feature rows: {len(X_clean)}")
        print(f"  - Features: {feature_columns}")
        
        return X_clean, y_yield_clean, X_clean, y_production_clean