# File: src/utils.py
"""
Utility functions for configuration and logging
"""
import json
import logging
import os
from datetime import datetime

def load_config():
    """Load configuration from config.json with defaults"""
    default_config = {
        "subject_url": "https://www.gutenberg.org/ebooks/subject/2716",
        "port": 5000,
        "font": "Helvetica",
        "font_color": "#800000"
    }
    
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Merge with defaults
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
        
        return config
        
    except Exception as e:
        print(f"Warning: Could not load config.json, using defaults: {str(e)}")
        return default_config

def setup_logging():
    """Setup logging configuration"""
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'error.log')
    
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()  # Also log to console
        ]
    )