# From-scratch implementations of Multinomial Naive Bayes (add-k smoothing)
# and L2-Regularized Logistic Regression (as specified in the project proposal)

import math
from collections import Counter


# From-scratch Multinomial Naive Bayes classifier with add-k (Laplace) smoothing
class CustomNaiveBayes:

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.vocab = set()
        self.class_priors = {}
        self.word_Counts = {0: Counter(), 1: Counter()}
        self.total_counts = {0: 0.0, 1: 0.0}

    # Clean negative features and scale tiny densities (same as NaiveBayesModel)
    def _clean_row(self, row):
        signed = {
            "lex_polarity_sum", "shift_sum", "lex_polarity_density", "shift_density",
            "ana_salient_net_density", "rst_weighted_polarity_density"
        }
        cleaned = {}
        for k, v in row.items():
            if k in signed or v < 0:
                continue
            if k.startswith(("lex_", "shift_")):
                cleaned[k] = v * 100.0
            elif k.startswith(("ana_", "rst_")):
                cleaned[k] = v * 4.0
            else:
                cleaned[k] = v
        return cleaned

    # Train Naive Bayes by counting feature totals in class 0 and class 1
    def train(self, X_train, y_train):
        n_docs = len(y_train)
        pos_docs = sum(1 for y in y_train if y == 1)
        neg_docs = n_docs - pos_docs

        self.class_priors[1] = math.log(max(1, pos_docs) / n_docs)
        self.class_priors[0] = math.log(max(1, neg_docs) / n_docs)

        for row, label in zip(X_train, y_train):
            clean = self._clean_row(row)
            for feat, val in clean.items():
                self.vocab.add(feat)
                self.word_Counts[label][feat] += val
                self.total_counts[label] += val

    # Predict sentiment class (0 or 1) for a list of feature dictionaries
    def predict(self, X):
        preds = []
        vocab_size = max(1, len(self.vocab))

        denom_0 = self.total_counts[0] + self.alpha * vocab_size
        denom_1 = self.total_counts[1] + self.alpha * vocab_size

        for row in X:
            clean = self._clean_row(row)
            score_0 = self.class_priors[0]
            score_1 = self.class_priors[1]

            for feat, val in clean.items():
                if feat not in self.vocab:
                    continue
                prob_0 = (self.word_Counts[0][feat] + self.alpha) / denom_0
                prob_1 = (self.word_Counts[1][feat] + self.alpha) / denom_1
                score_0 += val * math.log(prob_0)
                score_1 += val * math.log(prob_1)

            if score_1 >= score_0:
                preds.append(1)
            else:
                preds.append(0)

        return preds


# From-scratch L2-Regularized Logistic Regression trained with Gradient Descent
class CustomLogisticRegression:

    def __init__(self, lr=0.05, l2_reg=0.01, epochs=15):
        self.lr = lr
        self.l2_reg = l2_reg
        self.epochs = epochs
        self.weights = {}
        self.bias = 0.0

    # Sigmoid activation function with clipping to prevent math overflow
    def _sigmoid(self, z):
        if z > 30.0:
            return 1.0
        if z < -30.0:
            return 0.0
        return 1.0 / (1.0 + math.exp(-z))

    # Train weights using stochastic gradient descent with L2 regularization
    def train(self, X_train, y_train):
        self.weights = {}
        self.bias = 0.0

        for _ in range(self.epochs):
            for row, y in zip(X_train, y_train):
                z = self.bias
                for feat, val in row.items():
                    z += self.weights.get(feat, 0.0) * val

                pred = self._sigmoid(z)
                err = pred - y

                # Update bias and weights
                self.bias -= self.lr * err
                for feat, val in row.items():
                    old_w = self.weights.get(feat, 0.0)
                    grad = err * val + self.l2_reg * old_w
                    self.weights[feat] = old_w - self.lr * grad

    # Predict binary class labels (0 or 1)
    def predict(self, X):
        preds = []
        for row in X:
            z = self.bias
            for feat, val in row.items():
                z += self.weights.get(feat, 0.0) * val
            preds.append(1 if self._sigmoid(z) >= 0.5 else 0)
        return preds
