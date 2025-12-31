"""ML-based difficulty prediction for assignment tasks using v3 model."""

import pickle
from pathlib import Path
from typing import Optional

from .config import MODELS_DIR


class DifficultyPredictor:
    """Predicts task difficulty using trained ML model (v3 - Sentence Transformers + Neural Network)."""

    def __init__(self):
        """Initialize the difficulty predictor by loading v3 ML model."""
        self.sbert_model = None
        self.neural_network = None
        self.difficulty_map = None
        self.model_info = {}
        self.loaded = False

        try:
            self._load_model()
            self.loaded = True
            print("[OK] ML difficulty model v3 loaded successfully.")
            print(f"    Model Version: {self.model_info.get('model_version', 'Unknown')}")
            print(f"    Test Accuracy: {self.model_info.get('test_accuracy', 0):.2%}")
        except Exception as e:
            print(f"Warning: Could not load ML model v3: {e}")
            print("Will use default difficulty estimation.")

    def _load_model(self):
        """Load the trained v3 model from pickle file."""
        model_path = MODELS_DIR / "difficulty_predictor_v3.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        print(f"Loading v3 model from: {model_path}")
        with open(model_path, "rb") as f:
            model_dict = pickle.load(f)

        # Extract components from the model dictionary
        self.sbert_model = model_dict['sbert_model']
        self.neural_network = model_dict['neural_network']
        self.difficulty_map = model_dict['difficulty_map']

        # Store metadata
        self.model_info = {
            'model_version': model_dict.get('model_version', 'Unknown'),
            'test_accuracy': model_dict.get('test_accuracy', 0.0),
            'train_accuracy': model_dict.get('train_accuracy', 0.0),
            'dataset_info': model_dict.get('dataset_info', {})
        }

    def predict_difficulty(self, task_description: str, fallback: int = 3) -> int:
        """
        Predict difficulty rating from task description text using v3 model.

        Args:
            task_description: The text description of the task
            fallback: Default difficulty if model not loaded (1-5)

        Returns:
            Difficulty rating on 1-5 scale
        """
        if not self.loaded or not task_description.strip():
            print(f"  > Using fallback difficulty: {fallback}")
            return fallback

        try:
            # Step 1: Encode text using Sentence Transformer
            embeddings = self.sbert_model.encode([task_description])

            # Step 2: Predict difficulty using Neural Network
            predicted_label = self.neural_network.predict(embeddings)[0]

            print(f"  > Model v3 predicted label: {predicted_label}")

            # Step 3: Map predicted label to difficulty rating
            # difficulty_map format: {1: 'Easy', 3: 'Medium', 5: 'Hard'}
            # We need to find the key that matches the predicted value
            difficulty = fallback
            for rating, label in self.difficulty_map.items():
                if predicted_label == rating:
                    # Direct match (if model returns 1, 3, or 5)
                    difficulty = rating
                    print(f"  > Direct match to difficulty: {difficulty}/5 ({label})")
                    break
                elif str(predicted_label).lower() == label.lower():
                    # String match (if model returns 'Easy', 'Medium', 'Hard')
                    difficulty = rating
                    print(f"  > Label match to difficulty: {difficulty}/5 ({label})")
                    break
            else:
                # No match found, try to convert to number
                try:
                    difficulty = max(1, min(5, int(round(float(predicted_label)))))
                    print(f"  > Converted to difficulty: {difficulty}/5")
                except (ValueError, TypeError):
                    print(f"Warning: Could not map prediction '{predicted_label}'")
                    print(f"  > Using fallback difficulty: {fallback}")
                    difficulty = fallback

            return difficulty

        except Exception as e:
            print(f"Error during prediction: {e}")
            import traceback
            traceback.print_exc()
            print(f"  > Using fallback difficulty: {fallback}")
            return fallback
