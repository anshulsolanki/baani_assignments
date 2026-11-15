
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack, csr_matrix


class FeatureExtractor:

    def __init__(self, max_features=5000):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features
        )

    def fit_transform(self, reviews):
        return self.vectorizer.fit_transform(reviews)

    def transform(self, reviews):
        return self.vectorizer.transform(reviews)

    def combine_features(self, tfidf_features, rst_features):
        rst_features = csr_matrix(rst_features)

        return hstack(
            [tfidf_features, rst_features],
            format="csr"
        )
