import pickle
import numpy as np
import pandas as pd
from config import Config
import os

class CropPredictor:
    def __init__(self):
        self.config = Config()
        self.models = None
        self.historical_data = None
        self.load_models()
        self.load_historical_data()
        
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
    
    def load_historical_data(self):
        """Load historical data for trend analysis"""
        try:
            data_path = os.path.join(self.config.PROCESSED_DATA_DIR, self.config.MERGED_FILE)
            if os.path.exists(data_path):
                self.historical_data = pd.read_csv(data_path)
                print("✅ Historical data loaded successfully!")
            else:
                print("⚠️ No historical data found.")
                self.historical_data = None
        except Exception as e:
            print(f"❌ Error loading historical data: {e}")
            self.historical_data = None
    
    def calculate_year_trend(self, crop, season, target_year):
        """Calculate year-based trend adjustment"""
        if self.historical_data is None:
            return 1.0  # No adjustment if no historical data
        
        try:
            # Filter data for the specific crop and season
            crop_season_data = self.historical_data[
                (self.historical_data['Crop'] == crop) & 
                (self.historical_data['Season'] == season)
            ].copy()
            
            if len(crop_season_data) < 2:
                return 1.0  # Not enough data for trend
            
            # Calculate year-over-year growth rates
            crop_season_data = crop_season_data.sort_values('Year')
            
            # Calculate average yield and production trends
            years = crop_season_data['Year'].values
            yields = crop_season_data['Yield'].fillna(0).values
            productions = crop_season_data['Production'].fillna(0).values
            
            if len(years) < 3:
                return 1.0
            
            # Calculate linear trend (simple slope)
            yield_trend = np.polyfit(years, yields, 1)[0] if len(yields) > 1 else 0
            production_trend = np.polyfit(years, productions, 1)[0] if len(productions) > 1 else 0
            
            # Get the latest year in historical data
            latest_year = years.max()
            
            # Project trend to target year
            years_ahead = target_year - latest_year
            
            # Calculate growth factor (more conservative for future projections)
            if years_ahead > 0:
                # Future projection - be conservative
                yield_growth = 1 + (yield_trend * years_ahead * 0.5) / np.mean(yields) if np.mean(yields) > 0 else 1.0
                production_growth = 1 + (production_trend * years_ahead * 0.5) / np.mean(productions) if np.mean(productions) > 0 else 1.0
            else:
                # Historical interpolation - more accurate
                yield_growth = 1 + (yield_trend * years_ahead) / np.mean(yields) if np.mean(yields) > 0 else 1.0
                production_growth = 1 + (production_trend * years_ahead) / np.mean(productions) if np.mean(productions) > 0 else 1.0
            
            # Average the two growth factors and constrain to reasonable bounds
            growth_factor = (yield_growth + production_growth) / 2
            growth_factor = max(0.5, min(2.0, growth_factor))  # Between 50% and 200%
            
            return growth_factor
            
        except Exception as e:
            print(f"Error calculating year trend: {e}")
            return 1.0
    
    def apply_climate_factor(self, year, base_prediction):
        """Apply climate change and technological advancement factors"""
        base_year = 2020
        years_diff = year - base_year
        
        # Climate change impact (slight negative trend)
        climate_factor = 1 - (years_diff * 0.002)  # -0.2% per year
        
        # Technology improvement (positive trend)
        tech_factor = 1 + (years_diff * 0.008)  # +0.8% per year
        
        # Net effect (tech generally outweighs climate in near term)
        combined_factor = climate_factor * tech_factor
        
        # Constrain factor to reasonable bounds
        combined_factor = max(0.8, min(1.3, combined_factor))
        
        return base_prediction * combined_factor
    
    def predict(self, crop, season, area, year):
        """Make predictions for given inputs with year-based adjustments"""
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
            
            # Make base predictions
            base_yield = self.models['yield_model'].predict(features_yield_scaled)[0]
            base_production = self.models['production_model'].predict(features_production_scaled)[0]
            
            # Apply year-based trend adjustments
            trend_factor = self.calculate_year_trend(crop, season, year)
            
            # Apply climate and technology factors
            adjusted_yield = self.apply_climate_factor(year, base_yield * trend_factor)
            adjusted_production = self.apply_climate_factor(year, base_production * trend_factor)
            
            # Ensure positive predictions
            predicted_yield = max(0, adjusted_yield)
            predicted_production = max(0, adjusted_production)
            
            # Calculate confidence based on how far we're predicting into the future
            current_year = 2025
            years_ahead = abs(year - current_year)
            base_confidence = 0.85
            confidence = base_confidence * max(0.6, 1 - (years_ahead * 0.05))  # Decrease confidence for distant predictions
            
            return {
                'crop': crop,
                'season': season,
                'area': area,
                'year': year,
                'predicted_yield': round(predicted_yield, 2),
                'predicted_production': round(predicted_production, 2),
                'productivity': round(predicted_production / area, 2) if area > 0 else 0,
                'confidence': round(confidence, 3),
                'trend_factor': round(trend_factor, 3),
                'years_projected': years_ahead
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
    
    def get_prediction_summary(self, crop, season, area, years):
        """Get predictions for multiple years for comparison"""
        results = []
        for year in years:
            prediction = self.predict(crop, season, area, year)
            if 'error' not in prediction:
                results.append({
                    'year': year,
                    'yield': prediction['predicted_yield'],
                    'production': prediction['predicted_production'],
                    'productivity': prediction['productivity'],
                    'confidence': prediction['confidence']
                })
        return results