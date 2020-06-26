from sklearn.base import BaseEstimator, TransformerMixin


class VectorsFlattener(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass


    def transform(self, X, y=None):
        return X
        