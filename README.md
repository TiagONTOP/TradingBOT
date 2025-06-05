# TradingBOT
FTMO Bot de trading

## Adding New Trading Strategies

This trading bot uses a strategy pattern to allow for flexible implementation and selection of different trading algorithms.

### Core Concept

The core of this pattern is the `Strategy` abstract base class defined in `TradingBOT/pyrobot/strategy.py`. Any new strategy you create must inherit from this class and implement its three key methods:

1.  `train(self, X_train, y_train)`: This method is for training your strategy's model. If your strategy doesn't require training (e.g., it's purely rule-based), this method can simply `pass` or log a message.
2.  `predict(self, X)`: This method takes input data `X` (e.g., market features) and should return a pandas DataFrame containing your strategy's predictions. This DataFrame should typically have a 'preds' column with your predictive signals (e.g., scores, +1 for buy, -1 for sell).
3.  `generate_trades(self, predictions, n_trades)`: This method takes the DataFrame of predictions from `predict()` and an integer `n_trades` (maximum number of trades). It should return a dictionary where keys are asset tickers and values are trade signals (e.g., `1` for buy, `-1` for sell).

### Steps to Add a New Strategy

1.  **Create Your Strategy Class**:
    *   In `TradingBOT/pyrobot/strategy.py` (or a new file you import from), define your new class.
    *   Make it inherit from `Strategy` (e.g., `class MyNewStrategy(Strategy):`).
    *   Implement the `train`, `predict`, and `generate_trades` methods according to your strategy's logic.
    *   You can look at `LGBMStrategy` (in `TradingBOT/pyrobot/model.py`) and `SimpleMomentumStrategy` (in `TradingBOT/pyrobot/strategy.py`) for examples.

2.  **Integrate into the Robot (Optional)**:
    *   If you want to run your strategy using the main `TradingBOT/run_robot.py` script:
        *   Import your new strategy class in `run_robot.py`.
        *   Add a new option for your strategy to the `STRATEGY_NAME` variable.
        *   Update the conditional logic that instantiates the `strategy` object to include your new strategy.

3.  **Data Handling**:
    *   Be mindful of the data format your strategy's `predict` method expects. The `ManageDatas` class is responsible for fetching and preparing data. You might need to adjust `ManageDatas` or ensure your strategy can work with its current output format. The `SimpleMomentumStrategy`, for instance, expects a MultiIndex DataFrame with 'close' prices, which might differ from the data format used by `LGBMStrategy`.

By following these steps, you can extend the bot with various custom trading strategies.
