import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, time, timezone, date
import numpy as np
import math
from forex_python.converter import CurrencyRates
import holidays
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
        self.cr = CurrencyRates()

    def _create_session(self):

        mt5.initialize()
        mt5.login(self.client_id, self.client_mdp, self.trading_serveur)

    @property
    def market_open(self) -> bool:
        current_time = datetime.utcnow()
        us_holidays = holidays.US()
        if date.today() not in us_holidays:

            if current_time.weekday() < 4:
                return True
            elif current_time.weekday() == 4 and current_time.hour < 22:
                return True
            elif current_time.weekday() == 6 and current_time.hour > 22:
                return True
            else:
                return False

        else:
            return False

    @property
    def liquidity_hours(self) -> bool:

        lower_bound = datetime.now().replace(hour=3, minute=0, second=0, tzinfo=timezone.utc).timestamp()
        higher_bound = datetime.now().replace(hour=22, minute=0, second=0, tzinfo=timezone.utc).timestamp()
        right_now = datetime.now().astimezone(timezone.utc).timestamp()

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
                "volume" : self.leverage_to_volume(ticker),
                "type" : mt5.ORDER_TYPE_BUY_LIMIT if dict_pos[ticker] == 1 else mt5.ORDER_TYPE_SELL_LIMIT,
                "price" : mt5.symbol_info_tick(ticker).bid if dict_pos[ticker] == 1 else mt5.symbol_info_tick(ticker).ask
            }

            print(mt5.order_send(order))

    def create_close_trades(self, all_preds, time_limit):
        volumes = {}
        positions = mt5.positions_get()
        for position in positions:
            volumes[position.symbol] = position.volume
        pos_time = self.get_portfolio_pos_time()
        for ticker in pos_time.keys():
            if (pos_time[ticker]['Time'] > time_limit) and (pos_time[ticker]['PosType'] != sign(all_preds)):
                
                order = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": ticker,
                    "volume": volumes[ticker],
                    "type": mt5.ORDER_TYPE_SELL_LIMIT if pos_time[ticker]['PosType'] == 1 else mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": mt5.symbol_info_tick(ticker).ask if pos_time[ticker]['PosType'] == 1 else mt5.symbol_info_tick(ticker).bid    
                }
                
                mt5.order_send(order)
                
    def cancel_order(self):

        orders = mt5.orders_get()
        if orders is None:
            return
        for order in orders:
            result = mt5.order_send({
                "action": mt5.TRADE_ACTION_REMOVE,
                "ticket": order.ticket})
    
    def leverage_to_volume(self, ticker):

        account_currency = mt5.account_info().currency
        account = mt5.account_info().equity
        currency_base = mt5.symbol_info(ticker).currency_base
        lot_value = self.cr.convert(currency_base, account_currency, account)
        volume = self.leverage * account / lot_value
        volume = round(volume, ndigits=2)
        return volume 
        

        