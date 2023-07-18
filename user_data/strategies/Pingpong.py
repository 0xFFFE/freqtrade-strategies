#from typing import Dict, List
#from freqtrade.strategy.interface import IStrategy
#from pandas import DataFrame
from freqtrade.strategy import IStrategy
from typing import Dict, List
from functools import reduce
from pandas import DataFrame

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib  

class Pingpong(IStrategy):
    """
    Ping Pong Strategy
    """
    INTERFACE_VERSION: int = 3
    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    minimal_roi = {
        "60":  0.01,
        "30":  0.03,
        "20":  0.04,
        "0":  0.05
    }

    # Define the indicators and timeframe required for your strategy
    #minimal_roi = {
    #    "0": 0.01  # Set your minimum ROI here
    #}

    # Define your buy and sell parameters here
    buy_price_drop: float = -0.02  # Percentage drop from resistance to trigger buy
    sell_price_gain: float = 0.02  # Percentage gain from buy price to trigger sell


    # Optimal stoploss designed for the strategy
    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.10

    # Optimal timeframe for the strategy
    timeframe = '5m'

    # trailing stoploss
    trailing_stop = False
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02

    # run "populate_indicators" only for new candle
    process_only_new_candles = False

    # Experimental settings (configuration will overide these if set)
    use_exit_signal = True
    exit_profit_only = True
    ignore_roi_if_entry_signal = False

    # Optional order type mapping
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []
    
    #def populate_indicators(self, dataframe: Dict[str, float]) -> Dict[str, float]:
    def populate_indicators (self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['resistance'] = dataframe['close'].rolling(window=self.buy_signal_length).max()
        dataframe['support'] = dataframe['close'].rolling(window=self.sell_signal_length).min()


    def populate_entry_trend (self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Implement your entry trend logic here
        # This method is optional and can be used to add additional entry conditions

        dataframe.loc[
            (
                #dataframe['volume'] > 1000 & # Adjust the volume threshold as per your preference
                #(dataframe['close'].shift(1) / dataframe['close']) - 1 > self.buy_price_drop
                
                (dataframe['close'].shift(1) > dataframe['resistance']) &  # Check if previous close is above resistance
                (dataframe['close'] <= dataframe['resistance']) &  # Check if current close is at or below resistance
                (dataframe['close'] > dataframe['support']) &  # Check if current close is above support
                (dataframe['close'].shift(1) <= dataframe['support'])  # Check if previous close is at or below support
    

 
            ),
            'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend (self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Implement your exit trend logic here
        # This method is optional and can be used to add additional exit conditions
        
        '''dataframe.loc[
            (
                (dataframe['close'] / dataframe['buy_price']) - 1 > self.sell_price_gain
            ),
            'exit_long'] = 1
        '''
        return dataframe