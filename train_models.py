#!/usr/bin/env python3
"""
Script to manually train and save models
"""
from models.data_processor import DataProcessor
from models.model_trainer import ModelTrainer

def train_models():
    """Train and save models"""
    print("🚀 Starting Model Training...")
    print("=" * 50)
    
    # Process data
    processor = DataProcessor()
    merged_df = processor.load_and_process_data()
    
    if merged_df is not None:
        print("\n" + "="*50)
        print("🔧 PREPARING FEATURES")
        print("="*50)
        
        # Prepare features
        X_yield, y_yield, X_production, y_production = processor.prepare_features(merged_df)
        
        print("\n" + "="*50)
        print("🤖 TRAINING MODELS")
        print("="*50)
        
        # Train models
        trainer = ModelTrainer(processor)
        yield_results, production_results = trainer.train_models(
            X_yield, y_yield, X_production, y_production
        )
        
        print("\n" + "="*50)
        print("💾 SAVING MODELS")
        print("="*50)
        
        # Save models
        trainer.save_models()
        
        print("\n" + "="*50)
        print("✅ TRAINING COMPLETE!")
        print("="*50)
        print("Models are ready for the dashboard!")
        
    else:
        print("❌ Data processing failed. Cannot train models.")

if __name__ == "__main__":
    train_models()