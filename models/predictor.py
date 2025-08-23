import pickle
import numpy as np
import pandas as pd
from config import Config
import os

class CropPredictor:
    def __init__(self):
        self.config = Config()
        self.models = None
        self.load_models()
        
    def load_models(self):
        """Load saved models and preprocessors"""
        try:
            if os.path.exists(self.config.MODEL_FILE):
                with open(self.config.MODEL_FILE, 'rb') as f:
                    self.models = pickle.load(f)
                print("✅ Models loaded successfully!")
            else:
                print("⚠️ No saved models found. Models will be trained automatically.")
                self.models = None
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.models = None
    
    def predict(self, crop, season, area, year):
        """Make predictions for given inputs"""
        if not self.models:
            return {'error': 'Models not loaded. Please train models first.'}
        
        try:
            # Encode categorical variables
            if crop not in self.models['crop_encoder'].classes_:
                return {'error': f'Unknown crop: {crop}'}
            if season not in self.models['season_encoder'].classes_:
                return {'error': f'Unknown season: {season}'}
                
            crop_encoded = self.models['crop_encoder'].transform([crop])[0]
            season_encoded = self.models['season_encoder'].transform([season])[0]
            # Use the same baseline year as training (2015)
            baseline_year = self.models.get('baseline_year', 2015)
            year_normalized = year - baseline_year
            
            # Create feature vector
            features = np.array([[crop_encoded, season_encoded, area, year_normalized]])
            
            # Scale features
            features_yield_scaled = self.models['yield_scaler'].transform(features)
            features_production_scaled = self.models['production_scaler'].transform(features)
            
            # Make predictions
            predicted_yield = self.models['yield_model'].predict(features_yield_scaled)[0]
            predicted_production = self.models['production_model'].predict(features_production_scaled)[0]
            
            # Ensure positive predictions
            predicted_yield = max(0, predicted_yield)
            predicted_production = max(0, predicted_production)
            
            return {
                'crop': crop,
                'season': season,
                'area': area,
                'year': year,
                'predicted_yield': round(predicted_yield, 2),
                'predicted_production': round(predicted_production, 2),
                'productivity': round(predicted_production / area, 2) if area > 0 else 0
            }
        
        except Exception as e:
            return {'error': f'Prediction failed: {str(e)}'}
    
    def get_available_options(self):
        """Get available crops and seasons"""
        if not self.models:
            # Return default options if models aren't loaded
            return {
                'crops': ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize'],
                'seasons': ['Kharif', 'Rabi', 'Summer', 'Annual']
            }
        
        try:
            return {
                'crops': list(self.models['crop_encoder'].classes_),
                'seasons': list(self.models['season_encoder'].classes_)
            }
        except Exception as e:
            print(f"Error getting options: {e}")
            return {
                'crops': ['Rice', 'Wheat', 'Cotton', 'Sugarcane', 'Maize'],
                'seasons': ['Kharif', 'Rabi', 'Summer', 'Annual']
            }