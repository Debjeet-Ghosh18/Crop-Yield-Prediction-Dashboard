import os

class Config:
    # Data paths
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
    PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
    
    # Model paths
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'saved_models')
    MODEL_FILE = os.path.join(MODEL_DIR, 'crop_prediction_models.pkl')
    
    # Dashboard settings
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 8050
    
    # Data file names
    YIELD_FILE = 'All-India-Yield.csv'
    PRODUCTION_FILE = 'All-India-Production.csv'
    AREA_FILE = 'All-India-Area.csv'
    MERGED_FILE = 'merged_data.csv'