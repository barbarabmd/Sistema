import joblib
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin

class ControllableDummyModel(BaseEstimator, ClassifierMixin):
 
    def fit(self, X, y=None):
    
        return self

    def predict(self, X_features):
 
        predictions = []

        for features in X_features:
            balance = features[0]
            purchases = features[1]

            if balance > 4000 and purchases > 500:
                predictions.append(4)
            elif balance < 500 and purchases < 100:
                predictions.append(3)
            else:
                predictions.append(np.random.choice([0, 1, 2]))
        return np.array(predictions)

if __name__ == '__main__':
    model = ControllableDummyModel()
    model_filename = 'modelo_cluster_cartao_credito.pkl'
    joblib.dump(model, model_filename)
