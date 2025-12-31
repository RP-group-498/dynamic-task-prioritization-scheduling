# Adaptive Time Estimation Model

## Model Information
- Version: 1.0
- Created: 2025-12-28 09:16:15
- SBERT Model: all-MiniLM-L6-v2
- Vector Dimensions: 384

## Performance Metrics
- Mean Absolute Error: 0.67 minutes
- Accuracy (±5 min): 100.0%
- Training Size: 26 tasks
- Test Size: 6 tasks

## Files in This Package
- `sbert_model/` - Pre-trained SBERT model
- `model_config.json` - Configuration settings
- `accuracy_metrics.json` - Performance metrics

## How to Use
1. Load SBERT model from `sbert_model/`
2. Read configuration from `model_config.json`
3. Connect to MongoDB using settings in .env
4. Use predict_time() function to make predictions

## Requirements
- Python 3.8+
- sentence-transformers
- pymongo
- numpy
- scikit-learn
