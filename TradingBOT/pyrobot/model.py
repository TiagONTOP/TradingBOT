import pandas as pd
import numpy as np
from .strategy import Strategy


class LGBMStrategy(Strategy):


    def __init__(self, model):
        
        self.model = model
        self.preds = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series):

        self.model.fit(X_train, y_train)

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        
        index = X.index
        # Assuming model.predict returns a numpy array or similar that needs to be framed
        raw_predictions = self.model.predict(X)
        if not isinstance(raw_predictions, pd.DataFrame) and not isinstance(raw_predictions, pd.Series):
            preds_df = pd.DataFrame(raw_predictions, index=index, columns=['preds'])
        elif isinstance(raw_predictions, pd.Series):
            preds_df = pd.DataFrame(raw_predictions, index=index, columns=['preds'])
        else: # it's already a DataFrame
            preds_df = raw_predictions
            if 'preds' not in preds_df.columns: # Ensure 'preds' column exists
                 # This case assumes the DataFrame might not have the column name 'preds'
                 # Or it might have multiple columns, here we'd need a rule
                 # For simplicity, if only one column, rename it to 'preds'
                 if len(preds_df.columns) == 1:
                     preds_df.columns = ['preds']
                 else:
                     # Or handle error/specific logic if multiple columns without 'preds'
                     raise ValueError("Prediction DataFrame must have a 'preds' column or be a single column DataFrame.")

        self.preds = preds_df # Storing the DataFrame
        return preds_df
    
    def generate_trades(self, predictions: pd.DataFrame, n_trades: int) -> dict:
         
        if n_trades <= 0:
            return {} # Return empty dict for no trades
        if predictions is None or predictions.empty:
            # raise ValueError("Predictions have not been made or are empty.")
            return {} # Or return empty if no predictions

        # Ensure predictions DataFrame has 'preds' column or is a single column that can be treated as such
        if 'preds' not in predictions.columns:
            if len(predictions.columns) == 1:
                # If single column, use it directly but rename for clarity within this method
                predictions_col = predictions.iloc[:, 0]
            else:
                raise ValueError("Predictions DataFrame must contain a 'preds' column or be a single column DataFrame.")
        else:
            predictions_col = predictions['preds']

        # Sort by the absolute value of predictions to find the strongest signals
        # Then take the top n_trades
        # Ensure we are working with a Series for sorting
        if not isinstance(predictions_col, pd.Series):
            predictions_col = pd.Series(predictions_col)

        sorted_preds = predictions_col.abs().sort_values(ascending=False)
        
        if sorted_preds.empty:
            return {}

        top_tickers_indices = sorted_preds.iloc[:n_trades].index
        
        # Get the signs of the original predictions for these top tickers
        # Accessing original predictions using .loc with the selected indices
        signs = np.sign(predictions_col.loc[top_tickers_indices]).astype(int).tolist()

        return dict(zip(top_tickers_indices, signs))
