import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime
import talib as ta



class ManageDatas:

    def __init__(self, tickers):

        self.tickers = tickers
        self.momentum_windows = [30, 60, 120, 240, 480, 1060, 2120, 3180]
        self.ema_window = 20
        self.ema_accel_windows = [1, 5, 10, 30]
        self.rsi_window = 14
        self.log_returns_lags = list(range(1, 10))
        self.rolling_std_window = 50
        self.parkinson_sma_H_window = 200
        self.parkinson_sma_L_window = 20



    def get_clean_prices(self, interval, lenght):

        datas = []
        for ticker in self.tickers:

            data = pd.DataFrame(mt5.copy_rates_from(ticker, interval, datetime.now(), lenght))
            data['time'] = pd.to_datetime(data['time'], unit='s')
            data['symbol'] = np.full(shape=len(data), fill_value=ticker)
            data = data.drop(['real_volume'], axis=1)
            datas.append(data)

        data = pd.concat(datas, axis=0)
        data = data.set_index(['symbol', 'time'])

        return data
    
    def get_features_data(self, data):
        
        for window in self.momentum_windows:

            data[f'momentum_{window}p'] = (data
                                           .groupby(level='symbol', group_keys=False)
                                           .apply(lambda x: x.close.pct_change(window)))
        
        ema = data.groupby(level='symbol', group_keys=False).apply(lambda x: ta.EMA(x.close, timeperiod=self.ema_window))
        data[f'ema_spread{self.ema_window}'] = data.close - ema
        for window in self.ema_accel_windows:

            data[f'ema_accel_{window}p'] = ema.groupby(level='symbol', group_keys=False).apply(lambda x: x.pct_change(window))
        
        data['rsi'] = data.groupby(level='symbol', group_keys=False).apply(lambda x: ta.RSI(x.close, timeperiod=self.rsi_window))
        data['log_returns_lag_0p'] = data.groupby(level='symbol', group_keys=False).apply(lambda x: np.log(x.close/x.close.shift(1)))
        for lag in self.log_returns_lags:
            data[f'log_returns_lag_{lag}p'] = data.groupby(level='symbol', group_keys=False).apply(lambda x: x.log_returns_lag_0p.shift(lag))
        data[f'rolling_std_{self.rolling_std_window}'] = (data
                                                          .groupby(level='symbol', group_keys=False, as_index=False)['log_returns_lag_0p']
                                                          .rolling(self.rolling_std_window)
                                                          .std()
                                                          .drop(['symbol'], axis=1))
        data['parkinson'] = (data.groupby(level='symbol', group_keys=False).apply(lambda x: np.sqrt((1/4 * np.log(2)) * np.log(x.high/x.low)**2)))

        # !!!!!!!!!!! Faites un test pour vérifier si les nombres attribués à chaque ticker sont les mêmes entre l'ensemble d'entraînement (train set) et l'ensemble de test (test set). !!!!!!!!!!
        data['ticker_token'] = pd.factorize(data.index.get_level_values(0))[0]
        data['parkinson_sma_H'] = data.groupby(level='symbol', as_index=False)['parkinson'].rolling(self.parkinson_sma_H_window).mean().drop(['symbol'], axis=1)
        data['parkinson_sma_L'] = data.groupby(level='symbol', as_index=False)['parkinson'].rolling(self.parkinson_sma_L_window).mean().drop(['symbol'], axis=1)
        data['parkinson_spread'] = (data.parkinson_sma_L - data.parkinson_sma_H) / data.parkinson_sma_H

        return data



    def get_train_datas(self, length):
        
        pass