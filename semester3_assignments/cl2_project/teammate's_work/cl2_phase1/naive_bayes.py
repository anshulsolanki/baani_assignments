
from sklearn.naive_bayes import MultinomialNB


class NaiveBayesClassifier:

    def __init__(self, alpha=1.0):
        self.model = MultinomialNB(alpha=alpha)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)

    def predict_proba(self, X):
        return self.model.predict_proba(X)
