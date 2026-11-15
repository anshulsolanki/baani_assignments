
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class NaiveBayesModel:

    def __init__(self, alpha=1.0):
        self.model = Pipeline([
            ("vectorizer", DictVectorizer()),
            ("classifier", MultinomialNB(alpha=alpha))
        ])

    # CORRECTION 4c: Filter negative features and scale tiny densities (x100) so MultinomialNB uses M1-M4 features
    def _prepare_nb_features(self, X):
        signed_features = {
            "lex_polarity_sum", "shift_sum", "lex_polarity_density", "shift_density",
            "ana_salient_net_density", "rst_weighted_polarity_density"
        }
        return [
            {
                k: (
                    v * 100.0 if k.startswith(("lex_", "shift_"))
                    else (v * 4.0 if k.startswith(("ana_", "rst_")) else v)
                )
                for k, v in row.items()
                if k not in signed_features and v >= 0
            }
            for row in X
        ]

    def train(self, X_train, y_train):
        self.model.fit(self._prepare_nb_features(X_train), y_train)

    def predict(self, X):
        return self.model.predict(self._prepare_nb_features(X))

    def predict_proba(self, X):
        return self.model.predict_proba(self._prepare_nb_features(X))
