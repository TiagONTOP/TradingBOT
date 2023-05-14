import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, 'pyrobot'))
from broker import PyRobot
from manage_data import ManageDatas
from model import TradingModel
from lightgbm import LGBMRegressor

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