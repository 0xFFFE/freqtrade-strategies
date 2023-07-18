from typing import Dict
from pandas import DataFrame
from freqtrade.strategy.interface import IStrategy
import talib.abstract as ta

from hyperopt import hp, fmin, tpe, Trials
from freqtrade.strategy import IStrategy


class RsiMacd(IStrategy):

    # Define buy and sell parameters here

    #buy_price_drop: float = -0.02  # Percentage drop from resistance to trigger buy
    #sell_price_gain: float = 0.02  # Percentage gain from buy price to trigger sell

    # Define the indicators and timeframe required for your strategy
    #3.6% for 3 months - 15m	
    #minimal_roi = {
    #    "2160":  0.02,
    #    "1440":  0.05,
    #    "600":  0.05,
    #    "300":  0.05,
    #    "60":  0.06,
    #    "0":  0.06
    #}

    minimal_roi = {}

    minimal_roi = {
        "1440":  0.01,
        "600":  0.03,
        "300":  0.03,
        "60":  0.03,
        "0":  0.03
    }

    stoploss: float = -0.06

    def populate_indicators(self, dataframe: DataFrame, metadata: Dict[str, any]) -> DataFrame:
        # Calculate additional indicators using the 'ta' library
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['macd'], dataframe['macd_signal'], _  = ta.MACD(dataframe['close'], )
        

        # You can add more indicators here as needed

        return dataframe
    
       

    def populate_entry_trend(self, dataframe: DataFrame, metadata: Dict[str, any]) -> DataFrame:
        # Implement your entry trend logic here
        # Example: Enter trades when the RSI crosses above 30 and MACD is positive
        dataframe.loc[
            (
                (dataframe['rsi'].shift(1) < 30) & (dataframe['rsi'] >= 30) &
                #(dataframe['macd'] > 0) & 
                (dataframe['macd_signal'] > 0)
            ),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: Dict[str, any]) -> DataFrame:
        # Implement your exit trend logic here
        # Example: Exit trades when the RSI crosses below 70 or MACD crosses below the signal line
        dataframe.loc[
            (
                (dataframe['rsi'].shift(1) > 70) & (dataframe['rsi'] <= 70) &
                (dataframe['macd'] <= 0)
            ),
            'exit_long'] = 1
        return dataframe

    def hyperopt_space(self):
        space = {
            'stoploss': hp.uniform('stoploss', -0.1, 0.0)
        }
        return space

    def optimize(self, parameters):
        self.stoploss = parameters['stoploss']

        return -self.backtest()

    def hyperopt_main(self):
        space = self.hyperopt_space()
        trials = Trials()

        best = fmin(fn=self.optimize,
                    space=space,
                    algo=tpe.suggest,
                    max_evals=100,
                    trials=trials)

        print("Best hyperparameters:", best)
