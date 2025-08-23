#!/usr/bin/env python3
"""
Main script to run the crop prediction dashboard
"""
import os
import sys
from models.data_processor import DataProcessor
from models.model_trainer import ModelTrainer
from models.predictor import CropPredictor
from config import Config

def setup_project():
    """Setup the project by training models if needed"""
    config = Config()
    
    # Create necessary directories
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    
    # Check if models exist
    if not os.path.exists(config.MODEL_FILE):
        print("Models not found. Training new models...")
        
        # Process data
        processor = DataProcessor()
        merged_df = processor.load_and_process_data()
        
        if merged_df is not None:
            # Prepare features
            X_yield, y_yield, X_production, y_production = processor.prepare_features(merged_df)
            
            # Train models
            trainer = ModelTrainer(processor)
            yield_results, production_results = trainer.train_models(
                X_yield, y_yield, X_production, y_production
            )
            
            # Save models
            trainer.save_models()
            print("Models trained and saved successfully!")
        else:
            print("Error: Could not process data. Please check your data files.")
            return False
    else:
        print("✅ Models found and loaded!")
    
    return True

# -----------------------------
# ✅ Expose app + server for Gunicorn
# -----------------------------
from dashboard.app import app
server = app.server   # This is what Gunicorn will run

def main():
    """Main function to run the dashboard"""
    print("🌾 Starting Crop Prediction Dashboard...")
    
    # Setup project
    if not setup_project():
        print("❌ Setup failed. Exiting.")
        sys.exit(1)
    
    config = Config()
    print(f"🚀 Dashboard starting at http://{config.HOST}:{config.PORT}")
    
    # Local run
    try:
        app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
    except AttributeError:
        app.run_server(debug=config.DEBUG, host=config.HOST, port=config.PORT)

if __name__ == "__main__":
    main()
