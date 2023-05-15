import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, time, timezone
import numpy as np
import math

from typing import List, Dict, Union

def sign(x):
    return int(math.copysign(1, x))


class PyRobot:


    def __init__(self, client_id: int, client_mdp: str, trading_serveur: str, leverage: float):

        self.client_id = client_id
        self.client_mdp = client_mdp
        self.trading_serveur = trading_serveur
        self.trades: dict = {}
        self.leverage = leverage

    def _create_session(self):

        mt5.initialize()
        mt5.login(self.client_id, self.client_mdp, self.trading_serveur)

    @property
    def market_open(self) -> bool:
        symbol = 'EURUSD'
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info.session_deals == 0:
            return False
        else:
            return True

    @property
    def liquidity_hours(self) -> bool:

        lower_bound = datetime.now().replace(hour=3, minute=0, second=0, tzinfo=timezone.utc).timestamp()
        higher_bound = datetime.now().replace(hour=22, minute=0, second=0, tzinfo=timezone.utc).timestamp()
        right_now = datetime.now().replace(tzinfo=timezone.utc()).timestamp()

        if higher_bound >= right_now >= lower_bound: 
            return True
        else:
            return False

    def get_portfolio_pos_time(self):

        portfolio = {}
        positions = mt5.positions_get()
        if positions is None:
            return None
        else:
            for position in positions:
                portfolio[position.symbol] = {'PosType' : 1 if position.type == mt5.POSITION_TYPE_BUY else -1,
                                              'Time': datetime.now() - datetime.fromtimestamp(position.time)}
        return portfolio

    def create_entry_trades(self, dict_pos: dict):

        for ticker in dict_pos.keys():

            order = {
                "action" : mt5.TRADE_ACTION_DEAL,
                "symbol" : ticker,
                "volume" : 1.0, # à modifier avec un volume qui dépend du levier qui est lui même variable
                "type" : None
            }

    def create_close_trades(self, all_preds, time_limit):

        pos_time = self.get_portfolio_pos_time()
        for ticker in pos_time.keys():
            if (pos_time[ticker]['Time'] > time_limit) and (pos_time[ticker]['PosType'] != sign(all_preds)):
                
                order = {"action": mt5.TRADE_ACTION_DEAL,
                         "symbol": ticker,
                         "volume": 1.0, # à modifier avec un volume qui dépend du levier qui est lui même variable
                         "type": mt5.ORDER_TYPE_SELL_LIMIT if pos_time[ticker]['PosType'] == 1 else mt5.ORDER_TYPE_BUY_LIMIT,
                         "price": mt5.symbol_info_tick(ticker).ask if pos_time[ticker]['PosType'] == 1 else mt5.symbol_info_tick(ticker).bid,
                         }

    def create_exits_trades(self, preds):
        pass

        
    def grab_current_quotes(self):
        pass

    def grab_historical_prices(self):
        pass