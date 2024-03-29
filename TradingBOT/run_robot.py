import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, 'pyrobot'))
from broker import PyRobot
from manage_data import ManageDatas
from model import TradingModel
from datetime import datetime
from lightgbm import LGBMRegressor
import MetaTrader5 as mt5
import time


rf_model = LGBMRegressor(boosting_type='rf', 
                         objective='regression',
                         device='cpu',
                         n_jobs=-1,
                         n_estimators=500,
                         max_bin=100, 
                         max_depth=10,
                         num_leaves=20,
                         random_state=42,
                         feature_fraction=0.1,
                         bagging_fraction=0.3,
                         bagging_freq=1)

train_period_length = 2000
login_mt5 = 1051651055
mdp_mt5 = 'WTZRFSRT6J'
server = 'FTMO-Demo'
leverage = 4.4211
tickers = ['AUDCAD', 'AUDJPY', 'AUDNZD', 'AUDCHF', 'AUDUSD', 'GBPAUD', 
           'GBPCAD', 'GBPJPY', 'GBPNZD', 'GBPCHF', 'GBPUSD', 'CADJPY',
           'CADCHF', 'EURAUD', 'EURGBP', 'EURCAD', 'EURJPY', 'EURCHF', 
           'EURUSD', 'EURNZD', 'NZDCAD', 'NZDCHF', 'NZDUSD', 'NZDJPY',
           'CHFJPY', 'USDCAD', 'USDCHF', 'USDJPY']

brk = PyRobot(client_id=login_mt5, client_mdp=mdp_mt5, trading_serveur=server, leverage=leverage)
md = ManageDatas(tickers)
tm = TradingModel(model=rf_model)
last_time = None
time_retrain = 30
train_time = time_retrain + 1
max_pos = 1
min_time_pf = 10
interval = mt5.TIMEFRAME_M1

brk._create_session()

if __name__ == '__main__':

    while True:
        #initialize trade conditions
        actual_time = datetime.now().minute
        logic_cond = [actual_time != last_time, brk.market_open, brk.liquidity_hours]
        if all(logic_cond):
            start = time.time()
            # Cancel non executed orders
            brk.cancel_order()
            # Check if we must retrain our model
            train_time += 1
            if time_retrain <= train_time:
                #get train datas
                train_data = md.get_train_datas(interval=interval, length=train_period_length)
                target_column = [c for c in train_data.columns if 'target' in c][0]
                X_train = train_data.drop([target_column], axis=1)
                y_train = train_data[target_column]
                #Train model
                tm.train_model(X=X_train, y=y_train)
                train_time = 0
            
            # Get datas for predictions
            X = md.get_predict_datas(interval=interval)

            # Get predictions
            preds = tm.predict(X=X)
            # Close all positions that need to be closed
            brk.create_close_trades(all_preds=preds, time_limit=min_time_pf)

            # Verify if the portfolio is full
            n_trades = max(max_pos - mt5.positions_total(), 0)
            if n_trades == 0:
                last_time = datetime.now().minute
                continue

            # Get the best ticker(s) to trade
            tickers_to_trade = tm.tickers_to_trades(n_trades=n_trades)

            # send orders
            brk.create_entry_trades(dict_pos=tickers_to_trade)
            last_time = datetime.now().minute

            end = time.time()
            print(end - start)







