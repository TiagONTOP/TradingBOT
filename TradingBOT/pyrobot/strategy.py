"""
This module defines the interface for trading strategies.
To add a new strategy:
1. Create a new class that inherits from the `Strategy` abstract base class.
2. Implement the abstract methods: `train`, `predict`, and `generate_trades`.
3. See `LGBMStrategy` (in `model.py`) and `SimpleMomentumStrategy` (in this file)
   for examples.
4. Update `run_robot.py` to include your new strategy in the selection mechanism
   if you want to run it using the main script.
"""
import pandas as pd
import numpy as np # Ensure numpy is imported if SimpleMomentumStrategy uses it
from abc import ABC, abstractmethod

class Strategy(ABC):
    """
    Abstract base class for a trading strategy.

    A strategy encapsulates the logic for generating trading signals based on market data.
    It typically involves a model that can be trained (though not always required)
    and methods to produce predictions and convert them into actionable trades.
    """

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        Train the strategy's underlying model or prepare the strategy for prediction.

        Args:
            X_train: DataFrame containing features for training.
            y_train: Series containing the target variable for training.

        Not all strategies may require explicit training (e.g., rule-based strategies).
        If no training is needed, this method can simply pass or print a message.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions based on the input data.

        Args:
            X: DataFrame containing the features for which to make predictions.
               The structure of X might depend on the strategy's requirements.
               For example, it might expect certain columns or a specific index.

        Returns:
            A DataFrame indexed by ticker (or other relevant entity) with a 'preds'
            column containing the raw prediction signals (e.g., scores, +1/-1 signals).
        """
        pass

    @abstractmethod
    def generate_trades(self, predictions: pd.DataFrame, n_trades: int) -> dict:
        """
        Convert raw predictions into a dictionary of trades to be executed.

        Args:
            predictions: DataFrame of predictions, typically the output of the
                         `predict` method (should contain a 'preds' column).
            n_trades: The maximum number of trades to generate.

        Returns:
            A dictionary where keys are tickers (or other tradable instruments)
            and values are the trade signals (e.g., 1 for buy, -1 for sell, 0 for hold/no action).
            Example: {'EURUSD': 1, 'USDJPY': -1}
        """
        pass

# Existing SimpleMomentumStrategy class definition should be here...
class SimpleMomentumStrategy(Strategy):
    """
    A simple momentum strategy.
    It calculates momentum based on the last two 'close' prices for each ticker.
    """

    def __init__(self, momentum_window: int = 1):
        self.momentum_window = momentum_window
        # This strategy doesn't have a model to train in the traditional sense
        # but we could store parameters or state if needed.

    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """
        This strategy does not require training.
        """
        print("SimpleMomentumStrategy does not require training.")
        pass

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Generate predictions based on momentum.
        Expects X to be a DataFrame with a MultiIndex (level 0: ticker, level 1: timestamp)
        and a 'close' column.
        Momentum is calculated as the sign of the price change over the window.
        """
        if not isinstance(X.index, pd.MultiIndex):
            raise ValueError("Input DataFrame X must have a MultiIndex [ticker, timestamp].")
        if 'close' not in X.columns:
            raise ValueError("Input DataFrame X must contain a 'close' column.")

        # Calculate momentum: (price_now - price_n_periods_ago)
        # We need at least momentum_window + 1 data points per ticker to calculate momentum

        # Group by ticker and calculate the difference
        momentum = X.groupby(level=0)['close'].diff(self.momentum_window)

        # Take the sign of the momentum
        # Important: Ensure we are taking the latest momentum for each ticker
        # This predict function should return a DataFrame indexed by ticker, with a 'preds' column

        # Get the latest momentum for each ticker
        latest_momentum_signal = momentum.groupby(level=0).last()

        preds_df = pd.DataFrame(np.sign(latest_momentum_signal), columns=['preds'])
        preds_df.fillna(0, inplace=True) # Fill NaN signals with 0 (no trade)

        return preds_df

    def generate_trades(self, predictions: pd.DataFrame, n_trades: int) -> dict:
        """
        Convert momentum predictions into a dictionary of trades.
        Selects trades with the strongest (most non-zero) signals.
        """
        if n_trades <= 0:
            return {}
        if predictions is None or predictions.empty:
            return {}
        if 'preds' not in predictions.columns:
            print("Warning: 'preds' column not found in predictions. Returning no trades.")
            return {}

        # Ensure 'preds' is numeric
        predictions['preds'] = pd.to_numeric(predictions['preds'], errors='coerce').fillna(0)

        # Sort by the absolute value of 'preds' to pick strongest signals, excluding 0
        # We only want to consider trades where signal is non-zero
        valid_signals = predictions[predictions['preds'] != 0]

        if valid_signals.empty:
            return {}

        # Sort by absolute signal strength
        sorted_preds = valid_signals.abs().sort_values(by='preds', ascending=False)

        # Select top N trades
        tickers_to_trade_list = sorted_preds.iloc[:n_trades].index.to_list()

        if not tickers_to_trade_list:
            return {}

        # Get the original signs for these tickers
        signs = np.sign(predictions.loc[tickers_to_trade_list, 'preds']).astype(int).to_list()

        return dict(zip(tickers_to_trade_list, signs))
