"""ML-based difficulty prediction for assignment tasks using v2 model."""

import pickle
from pathlib import Path
from typing import Optional

from .config import MODELS_DIR


class DifficultyPredictor:
    """Predicts task difficulty using trained ML model (v2 - Sentence Transformers + XGBoost)."""

    def __init__(self):
        """Initialize the difficulty predictor by loading v2 ML model."""
        self.sbert_model = None
        self.xgboost_classifier = None
        self.difficulty_map = None
        self.model_info = {}
        self.loaded = False

        try:
            self._load_model()
            self.loaded = True
            print("="*80)
            print("[OK] ML difficulty model v2 loaded successfully.")
            print(f"    Model Version: {self.model_info.get('model_version', 'Unknown')}")
            print(f"    Test Accuracy: {self.model_info.get('test_accuracy', 0):.2%}")
            print(f"    Train Accuracy: {self.model_info.get('train_accuracy', 0):.2%}")
            print(f"    Trained on: {self.model_info.get('trained_on', 'N/A')} samples")
            print("="*80)
        except Exception as e:
            print(f"Warning: Could not load ML model v2: {e}")
            print("Will use default difficulty estimation.")

    def _load_model(self):
        """Load the trained v2 model from pickle file."""
        model_path = MODELS_DIR / "difficulty_predictor_v2.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        print(f"Loading v2 model from: {model_path}")
        with open(model_path, "rb") as f:
            model_dict = pickle.load(f)

        # Extract components from the model dictionary
        self.sbert_model = model_dict['sbert_model']
        self.xgboost_classifier = model_dict['xgboost_judge']

        # V2 model uses class mapping: 0=Easy, 1=Medium, 2=Hard
        self.difficulty_map = model_dict.get('difficulty_map', {0: 'Easy', 1: 'Medium', 2: 'Hard'})

        # Score mapping for 1-5 scale
        self.class_to_score = {
            0: 1,  # Easy = 1
            1: 3,  # Medium = 3
            2: 5   # Hard = 5
        }

        # Store metadata
        self.model_info = {
            'model_version': model_dict.get('model_version', 'v2'),
            'test_accuracy': model_dict.get('test_accuracy', 0.0),
            'train_accuracy': model_dict.get('train_accuracy', 0.0),
            'trained_on': model_dict.get('trained_on', 'N/A'),
            'dataset_info': model_dict.get('dataset_info', {})
        }

    def predict_difficulty(self, task_description: str, fallback: int = 3) -> int:
        """
        Predict difficulty rating from task description text using v2 model.

        Args:
            task_description: The text description of the task
            fallback: Default difficulty if model not loaded (1-5)

        Returns:
            Difficulty rating on 1-5 scale (1=Easy, 3=Medium, 5=Hard)
        """
        if not self.loaded or not task_description.strip():
            print(f"  > Using fallback difficulty: {fallback}")
            return fallback

        try:
            # Step 1: Encode text using Sentence Transformer
            embeddings = self.sbert_model.encode([task_description])

            # Step 2: Predict difficulty using XGBoost
            prediction_class = self.xgboost_classifier.predict(embeddings)[0]
            probabilities = self.xgboost_classifier.predict_proba(embeddings)[0]

            # Step 3: Map to difficulty score and label
            difficulty_label = self.difficulty_map.get(prediction_class, 'Medium')
            difficulty_score = self.class_to_score.get(prediction_class, fallback)
            confidence = max(probabilities) * 100

            # Display detailed output in terminal
            print("\n" + "="*80)
            print("DIFFICULTY PREDICTION RESULTS")
            print("="*80)
            print(f"Task: {task_description[:60]}...")
            print(f"\nDifficulty Rating: {difficulty_label} (Score: {difficulty_score}/5)")
            print(f"Prediction Class: {prediction_class}")
            print(f"Confidence: {confidence:.1f}%")

            print(f"\nProbabilities:")
            print(f"  Easy   (1/5): {probabilities[0]:.1%} (Class 0)")
            print(f"  Medium (3/5): {probabilities[1]:.1%} (Class 1)")
            print(f"  Hard   (5/5): {probabilities[2]:.1%} (Class 2)")
            print("="*80 + "\n")

            return difficulty_score

        except Exception as e:
            print(f"Error during prediction: {e}")
            import traceback
            traceback.print_exc()
            print(f"  > Using fallback difficulty: {fallback}")
            return fallback
