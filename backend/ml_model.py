"""
ML model for feedback classification.
TF-IDF + Logistic Regression trained on large_feedback_dataset.csv.
Includes sentiment-aware feature engineering to handle noisy dataset.
"""

import os
import re
import pickle
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

BASE_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(BASE_DIR, "large_feedback_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

_pipeline = None

# Strong sentiment keyword lists for feature engineering
_COMPLAINT_WORDS = {
    "terrible", "horrible", "awful", "hate", "worst", "broken", "crash",
    "crashes", "crashing", "bug", "error", "fail", "failed", "failing",
    "slow", "freeze", "freezes", "freezing", "not working", "doesn't work",
    "cant", "cannot", "unable", "problem", "issue", "bad", "poor",
    "disappointed", "frustrating", "useless", "annoying", "fix", "wrong",
    "never works", "keeps crashing", "always fails", "nothing works",
    "waste", "garbage", "pathetic", "ridiculous", "unacceptable",
}

_COMPLIMENT_WORDS = {
    "love", "great", "excellent", "amazing", "fantastic", "awesome",
    "wonderful", "perfect", "best", "good", "nice", "happy", "thank",
    "brilliant", "superb", "outstanding", "impressive", "smooth",
    "helpful", "easy", "intuitive", "beautiful", "clean", "fast",
    "responsive", "reliable", "enjoy", "pleased", "satisfied",
}

_FEATURE_WORDS = {
    "add", "feature", "request", "suggestion", "would be nice", "please add",
    "could you", "wish", "want", "need", "should have", "missing",
    "support for", "allow", "enable", "option", "ability", "integrate",
    "implement", "include", "provide", "consider", "enhancement",
}


class SentimentFeatures(BaseEstimator, TransformerMixin):
    """Extracts hand-crafted sentiment keyword counts as extra features."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            t = text.lower()
            complaint_score = sum(1 for w in _COMPLAINT_WORDS if w in t)
            compliment_score = sum(1 for w in _COMPLIMENT_WORDS if w in t)
            feature_score = sum(1 for w in _FEATURE_WORDS if w in t)
            # Ratio features to capture dominance
            total = complaint_score + compliment_score + feature_score + 1
            features.append([
                complaint_score,
                compliment_score,
                feature_score,
                complaint_score / total,
                compliment_score / total,
                feature_score / total,
            ])
        return np.array(features)


def _clean(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _train_and_save() -> Pipeline:
    print("[ml_model] Training model from dataset...")
    df = pd.read_csv(DATASET_PATH)
    df.dropna(subset=["feedback", "category"], inplace=True)
    df["feedback"] = df["feedback"].apply(_clean)

    X_train, X_test, y_train, y_test = train_test_split(
        df["feedback"], df["category"], test_size=0.2, random_state=42, stratify=df["category"]
    )

    # Combine TF-IDF with hand-crafted sentiment features
    combined_features = FeatureUnion([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=15000,
            sublinear_tf=True,
            min_df=2,
        )),
        ("sentiment", SentimentFeatures()),
    ])

    pipeline = Pipeline([
        ("features", combined_features),
        ("clf", LogisticRegression(
            max_iter=2000,
            C=3.0,
            class_weight="balanced",
            solver="lbfgs",
            multi_class="multinomial",
        )),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("[ml_model] Training complete.\n", classification_report(y_test, y_pred))

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    print(f"[ml_model] Model saved to {MODEL_PATH}")
    return pipeline


def _load_model():
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    if os.path.exists(MODEL_PATH):
        print("[ml_model] Loading model from pkl...")
        with open(MODEL_PATH, "rb") as f:
            _pipeline = pickle.load(f)
    else:
        _pipeline = _train_and_save()

    return _pipeline


def predict_category(message: str) -> str:
    """
    Predicts feedback category from message text.
    Returns one of: 'Complaint', 'Compliment', 'Feature Request'
    """
    model = _load_model()
    cleaned = _clean(message)
    result = model.predict([cleaned])[0]
    return str(result)
