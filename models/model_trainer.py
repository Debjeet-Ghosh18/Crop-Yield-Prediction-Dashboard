from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import numpy as np
import pickle
import os
from config import Config

class ModelTrainer:
    def __init__(self, data_processor):
        self.data_processor = data_processor
        self.config = Config()
        self.models = {}
        self.scalers = {}
        
    def train_models(self, X_yield, y_yield, X_production, y_production):
        """Train models for both yield and production prediction"""
        
        print(f"Training with {len(X_yield)} yield samples and {len(X_production)} production samples...")
        
        # Scale features
        self.scalers['yield'] = StandardScaler()
        self.scalers['production'] = StandardScaler()
        
        X_yield_scaled = self.scalers['yield'].fit_transform(X_yield)
        X_production_scaled = self.scalers['production'].fit_transform(X_production)
        
        # Split data
        X_train_y, X_test_y, y_train_y, y_test_y = train_test_split(
            X_yield_scaled, y_yield, test_size=0.2, random_state=42
        )
        
        X_train_p, X_test_p, y_train_p, y_test_p = train_test_split(
            X_production_scaled, y_production, test_size=0.2, random_state=42
        )
        
        # Initialize models
        model_types = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        # Train yield models
        print("Training Yield Models...")
        yield_results = {}
        for name, model in model_types.items():
            print(f"  - Training {name}...")
            model.fit(X_train_y, y_train_y)
            y_pred_test = model.predict(X_test_y)
            
            r2_score_val = r2_score(y_test_y, y_pred_test)
            yield_results[name] = {
                'model': model,
                'test_r2': r2_score_val,
                'test_rmse': np.sqrt(mean_squared_error(y_test_y, y_pred_test)),
                'test_mae': mean_absolute_error(y_test_y, y_pred_test)
            }
            print(f"    R² Score: {r2_score_val:.4f}")
        
        # Train production models
        print("Training Production Models...")
        production_results = {}
        for name, model in model_types.items():
            print(f"  - Training {name}...")
            # Create fresh model instance
            if name == 'Linear Regression':
                model_copy = LinearRegression()
            elif name == 'Random Forest':
                model_copy = RandomForestRegressor(n_estimators=100, random_state=42)
            else:
                model_copy = GradientBoostingRegressor(n_estimators=100, random_state=42)
                
            model_copy.fit(X_train_p, y_train_p)
            y_pred_test = model_copy.predict(X_test_p)
            
            r2_score_val = r2_score(y_test_p, y_pred_test)
            production_results[name] = {
                'model': model_copy,
                'test_r2': r2_score_val,
                'test_rmse': np.sqrt(mean_squared_error(y_test_p, y_pred_test)),
                'test_mae': mean_absolute_error(y_test_p, y_pred_test)
            }
            print(f"    R² Score: {r2_score_val:.4f}")
        
        # Select best models
        best_yield_model = max(yield_results.keys(), key=lambda x: yield_results[x]['test_r2'])
        best_production_model = max(production_results.keys(), key=lambda x: production_results[x]['test_r2'])
        
        print(f"\nBest Models Selected:")
        print(f"  Yield: {best_yield_model} (R² = {yield_results[best_yield_model]['test_r2']:.4f})")
        print(f"  Production: {best_production_model} (R² = {production_results[best_production_model]['test_r2']:.4f})")
        
        self.models['yield'] = yield_results[best_yield_model]['model']
        self.models['production'] = production_results[best_production_model]['model']
        
        return yield_results, production_results
    
    def save_models(self):
        """Save trained models and preprocessors"""
        try:
            # Ensure directory exists
            os.makedirs(self.config.MODEL_DIR, exist_ok=True)
            
            # Get baseline year for normalization
            baseline_year = 2015  # Based on your data starting from 2015
            
            models_to_save = {
                'yield_model': self.models['yield'],
                'production_model': self.models['production'],
                'yield_scaler': self.scalers['yield'],
                'production_scaler': self.scalers['production'],
                'crop_encoder': self.data_processor.le_crop,
                'season_encoder': self.data_processor.le_season,
                'feature_names': ['Crop_encoded', 'Season_encoded', 'Area', 'Year_normalized'],
                'baseline_year': baseline_year
            }
            
            # Save to pickle file
            with open(self.config.MODEL_FILE, 'wb') as f:
                pickle.dump(models_to_save, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            print(f"✅ Models saved successfully to {self.config.MODEL_FILE}")
            
            # Verify the save worked
            with open(self.config.MODEL_FILE, 'rb') as f:
                test_load = pickle.load(f)
            print("✅ Model save verification successful!")
            
        except Exception as e:
            print(f"❌ Error saving models: {e}")
            import traceback
            traceback.print_exc()