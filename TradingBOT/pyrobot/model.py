import pandas as pd
import numpy as np


class TradingModel:


    def __init__(self, model):
        
        self.model = model

    def train_model(self, X, y):

        self.model.fit(X, y)

    def predict(self, X):
        
        index = X.index
        preds = pd.DataFrame(self.model.predict(X), index=index, columns=['preds'])
        self.preds = preds
        return preds
    
    def tickers_to_trades(self, n_trades, preds=None):

        if preds is None:
            tickers = self.preds.abs().sort_values(by='preds', ascending=False).iloc[:n_trades].to_list()
            signs = list(np.sign(self.preds.loc[tickers]))
        else:
            tickers = preds.abs().sort_values(by='preds', ascending=False).iloc[:n_trades].to_list()
            signs = list(np.sign(preds.loc[tickers]))

        return dict(zip(tickers, signs))


        
    



        
