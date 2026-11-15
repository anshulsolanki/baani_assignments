
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


class LogisticRegressionModel:

    def __init__(self, max_iter=1000):
        self.model = Pipeline([
            ("vectorizer", DictVectorizer()),
            ("classifier", LogisticRegression(
                max_iter=max_iter,
                random_state=42
            ))
        ])

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
