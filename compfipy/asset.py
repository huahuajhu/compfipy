# pylint: disable=too-many-public-methods
"""
asset.py

Define the an asset class to contain price data and various calculations, measures, and processed versions of data.

"""

import datetime
import collections
import tabulate
import scipy.stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from compfipy.util import RISK_FREE_RATE, MONTHS_IN_YEAR, DAYS_IN_YEAR, DAYS_IN_TRADING_YEAR
from compfipy.util import FIBONACCI_SEQUENCE, FIBONACCI_DECIMAL, RANK_PERCENTS, RANK_DAYS_IN_TRADING_YEAR
from compfipy.util import calc_returns, calc_cagr, fmtp, fmtn, fmttn, sma, ema

# Helper Functions for Fibonacci Code
# ------------------------------------------------------------------------------------------------------------------------------
def fibonacci_retracement(price=0.0, lastprice=0.0):
    """
    Fibonacci_retracement
    """
    return price + FIBONACCI_DECIMAL * (lastprice - price)

def fibonacci_arc(price=0.0, lastprice=0.0, days_since_last_price=0, n_days=0):
    """
    Fibonacci_arc
    """
    fib_radius = FIBONACCI_DECIMAL * np.sqrt(np.power(lastprice - price, 2) + np.power(days_since_last_price, 2))
    return price - np.sqrt(np.power(fib_radius, 2) - np.power(n_days, 2))

def fibonacci_time(date=datetime.date.today()):
    """
    Fibonacci_time
    """
    return [date + datetime.timedelta(days=d) for d in FIBONACCI_SEQUENCE]

# General Utility Functions
# ------------------------------------------------------------------------------------------------------------------------------
def plot(x, figsize=(16, 4), title=None, logy=False, **kwargs):
    """
    Plot helper, assumes a pd.Series or pd.DataFrame.
    """
    title = title if title else 'Price Series'
    x.plot(figsize=figsize, title=title, logy=logy, **kwargs)

def scatter_matrix(x, figsize=(16, 4), title=None, logy=False, **kwargs):
    """
    Plot helper, assumes a pd.Series or pd.DataFrame.
    """
    title = title if title else 'Price Scatter Matrix'
    x.scatter_matrix(figsize=figsize, title=title, logy=logy, **kwargs)

def hist(x, figsize=(16, 4), title=None, logy=False, **kwargs):
    """
    Plot helper, assumes a pd.Series or pd.DataFrame.
    """
    title = title if title else 'Return Histogram'
    x.hist(figsize=figsize, title=title, logy=logy, **kwargs)

# General Asse Class
# ------------------------------------------------------------------------------------------------------------------------------
class Asset(object):
    # pylint: disable=line-too-long
    """
    Asset Class for storing OCHLV price data, and calculating overlays and indicators from price data.

    Overlays
    --------
    [x] Bollinger Bands                      - A chart overlay that shows the upper and lower limits of 'normal' price movements based on the Standard Deviation of prices.
    [x] Chandelier Exit                      - A indicator that can be used to set trailing stop-losses for both long and short position.
    [x] Ichimoku Clouds                      - A comprehensive indicator that defines support and resistance, identifies trend direction, gauges momentum and provides trading signals.
    [x] Keltner Channels                     - A chart overlay that shows upper and lower limits for price movements based on the Average True Range of prices.
    [x] Moving Averages                      - Simple and Exponential - Chart overlays that show the 'average' value over time. Both Simple Moving Averages (SMAs) and Exponential Moving Averages (EMAs) are explained.
    [x] Moving Average Envelopes             - A chart overlay consisting of a channel formed from simple moving averages.
    [x] Parabolic SAR                        - A chart overlay that shows reversal points below prices in an uptrend and above prices in a downtrend.
    [x] Pivot Points                         - A chart overlay that shows reversal points below prices in an uptrend and above prices in a downtrend.
    [x] Price Channels                       - A chart overlay that shows a channel made from the highest high and lowest low for a given period of time.
    [x] Volume by Price                      - A chart overlay with a horizontal histogram showing the amount of activity at various price levels.
    [x] Volume-weighted Average Price (VWAP) - An intraday indicator based on total dollar value of all trades for the current day divided by the total trading volume for the current day.
    [x] ZigZag                               - A chart overlay that shows filtered price movements that are greater than a given percentage.

    Indicators
    ----------
    [x] Accumulation Distribution Line       - Combines price and volume to show how money may be flowing into or out of a stock.
    [x] Aroon                                - Uses Aroon Up and Aroon Down to determine whether a stock is trending or not.
    [x] Aroon Oscillator                     - Measures the difference between Aroon Up and Aroon Down.
    [x] Average Directional Index (ADX)      - Shows whether a stock is trending or oscillating.
    [x] Average True Range (ATR)             - Measures a stock's volatility.
    [x] BandWidth                            - Shows the percentage difference between the upper and lower Bollinger Band.
    [x] %B Indicator                         - Shows the relationship between price and standard deviation bands.
    [x] Commodity Channel Index (CCI)        - Shows a stock's variation from its 'typical' price.
    [x] Coppock Curve                        - An oscillator that uses rate-of-change and a weighted moving average to measure momentum.
    [x] Chaikin Money Flow                   - Combines price and volume to show how money may be flowing into or out of a stock. Alternative to Accumulation/Distribution Line.
    [x] Chaikin Oscillator                   - Combines price and volume to show how money may be flowing into or out of a stock. Based on Accumulation/Distribution Line.
    [x] Price Momentum Oscillator            - An advanced momentum indicator that tracks a stock's rate of change.
    [x] Detrended Price Oscillator (DPO)     - A price oscillator that uses a displaced moving average to identify cycles.
    [x] Ease of Movement (EMV)               - An indicator that compares volume and price to identify significant moves.
    [x] Force Index                          - A simple price-and-volume oscillator.
    [x] Know Sure Thing (KST)                - An indicator that measures momentum in a smooth fashion.
    [x] Mass Index                           - An indicator that identifies reversals when the price range widens.
    [x] MACD                                 - A momentum oscillator based on the difference between two EMAs.
    [x] MACD-Histogram                       - A momentum oscillator that shows the difference between MACD and its signal line.
    [x] Money Flow Index (MFI)               - A volume-weighted version of RSI that shows shifts is buying and selling pressure.
    [x] Negative Volume Index (NVI)          - A cumulative volume-based indicator used to identify trend reversals.
    [x] On Balance Volume (OBV)              - Combines price and volume in a very simple way to show how money may be flowing into or out of a stock.
    [x] Percentage Price Oscillator (PPO)    - A percentage-based version of the MACD indicator.
    [x] Percentage Volume Oscillator         - The PPO indicator applied to volume instead of price.
    [x] Rate of Change (ROC)                 - Shows the speed at which a stock's price is changing.
    [x] Relative Strength Index (RSI)        - Shows how strongly a stock is moving in its current direction.
    [x] StockCharts Tech. Ranks (SCTRs)      - Our relative ranking system based on a stock's technical strength.
    [ ] Slope                                - Measures the rise-over-run for a linear regression
    [x] Standard Deviation (Volatility)      - A statistical measure of a stock's volatility.
    [x] Stochastic Oscillator                - Shows how a stock's price is doing relative to past movements. Fast, Slow and Full Stochastics are explained.
    [x] StochRSI                             - Combines Stochastics with the RSI indicator. Helps you see RSI changes more clearly.
    [x] TRIX                                 - A triple-smoothed moving average of price movements.
    [x] True Strength Index (TSI)            - An indicator that measures trend direction and identifies overbought/oversold levels.
    [x] Ulcer Index                          - An indicator designed to measure market risk or volatility.
    [x] Ultimate Oscillator                  - Combines long-term, mid-term and short-term moving averages into one number.
    [x] Vortex Indicator                     - An indicator designed to identify the start of a new trend and define the current trend.
    [x] William %R                           - Uses Stochastics to determine overbought and oversold levels.

    Charts
    ------
    [x] Gaps                                  - An area of price change in which there were no trades.
    [ ] Classify Gaps                         - decide if a gap is [ ] common, [ ] breakaway, [ ] runaway, or [ ] exhaustion
    [ ] Double Top Reversal
    [ ] Double Bottom Reversal
    [ ] Head and Shoulders Top (Reversal)
    [ ] Head and Shoulders Bottom (Reversal)
    [ ] Falling Wedge (Reversal)
    [ ] Rising Wedge (Reversal)
    [ ] Rounding Bottom (Reversal)
    [ ] Triple Top Reversal
    [ ] Triple Bottom Reversal
    [ ] Bump and Run Reversal (Reversal)
    [ ] Flag, Pennant (Continuation)
    [ ] Symmetrical Triangle (Continuation)
    [ ] Ascending Triangle (Continuation)
    [ ] Descending Triangle (Continuation)
    [ ] Rectangle (Continuation)
    [ ] Price Channel (Continuation)
    [ ] Measured Move - Bullish (Continuation)
    [ ] Measured Move - Bearish (Continuation)
    [ ] Cup with Handle (Continuation)

    [ ] Introduction to Candlesticks          - An overview of candlesticks, including history, formation, and key patterns.
    [ ] Candlesticks and Support              - How candlestick chart patterns can mark support levels.
    [ ] Candlesticks and Resistance           - How candlestick chart patterns can mark resistance levels.
    [ ] Candlestick Bullish Reversal Patterns - Detailed descriptions of bullish reversal candlestick patterns
    [ ] Candlestick Bearish Reversal Patterns - Detailed descriptions of common bearish reversal candlestick patterns.
    [ ] Candlestick Pattern Dictionary        - A comprehensive list of common candlestick patterns.

    [ ] Arms CandleVolume                     - A price chart that merges candlesticks with EquiVolume boxes.
    [ ] CandleVolume                          - A price chart that merges candlesticks with volume.
    [ ] Elder Impulse System                  - A trading system that color codes the price bars to show signals.
    [ ] EquiVolume                            - Price boxes that incorporate volume. How to use and interpret EquiVolume boxes.
    [ ] Heikin-Ashi                           - A candlestick method that uses price data from two periods instead one one.
    [ ] Kagi Charts                           - How to use and interpret Kagi charts.
    [ ] Point and Figure Charts               - How to use and interpret Point and Figure charts.
    [ ] Renko Charts                          - How to use and interpret Renko charts.
    [ ] Three Line Break Charts               - How to use and interpret Three Line Break charts.

    [ ] Andrews' Pitchfork                    - Drawing, adjusting and interpreting this trend channel tool.
    [ ] Cycles                                - Steps to finding cycles and using the Cycle Lines Tool.
    [o] Fibonacci Retracements                - Defines Fibonacci retracements and shows how to use them to identify reversal zones.
    [o] Fibonacci Arcs                        - Shows how Fibonacci Arcs can be used to find reversals.
    [ ] Fibonacci Fans                        - Explains what Fibonacci Fans are and how they can be used.
    [o] Fibonacci Time Zones                  - Describes Fibonacci Time Zones and how they can be used.
    [x] Quandrant Lines                       - Defines Quadrant Lines and shows how they can be used to find future support/resistance zones.
    [ ] Raff Regression Channel               - A channel tool based on two equidistant trendlines on either side of a linear regression.
    [ ] Speed Resistance Lines                - Shows how Speed Resistance Lines are used on charts.
    """
    # pylint: enable=line-too-long

    def __init__(self, data=None, market_cap=1.0):
        """
        Create an asset, with string symbol and pandas.Series of price data.
        """
        self.symbol = data.index.name
        self.data = data
        self.market_cap = market_cap
        self.stats = {}

    def __str__(self):
        """
        Return string representation.
        """
        return str(self.data)

    # Summary stats
    # --------------------------------------------------------------------------------------------------------------------------
    def calc_stats(self, yearly_risk_free_return=RISK_FREE_RATE):
        """
        Calculate common statistics for this asset.
        """
        # pylint: disable=too-many-statements

        monthly_risk_free_return = (np.power(1 + yearly_risk_free_return, 1.0 / MONTHS_IN_YEAR) - 1.0) * MONTHS_IN_YEAR
        daily_risk_free_return = (np.power(1 + yearly_risk_free_return, 1.0 / DAYS_IN_TRADING_YEAR) - 1.0) * DAYS_IN_TRADING_YEAR

        # Sample prices
        daily_price = self.close
        monthly_price = daily_price.resample('M').last()
        yearly_price = daily_price.resample('A').last()

        self.stats = {
            'name' : self.symbol,
            'start': daily_price.index[0],
            'end': daily_price.index[-1],
            'market_cap' : self.market_cap,
            'yearly_risk_free_return': yearly_risk_free_return,
            'daily_mean': np.nan,
            'daily_vol': np.nan,
            'daily_sharpe': np.nan,
            'best_day': np.nan,
            'worst_day': np.nan,
            'total_return': np.nan,
            'cagr': np.nan,
            'incep': np.nan,
            'max_drawdown': np.nan,
            'avg_drawdown': np.nan,
            'avg_drawdown_days': np.nan,
            'daily_skew': np.nan,
            'daily_kurt': np.nan,
            'monthly_mean': np.nan,
            'monthly_vol': np.nan,
            'monthly_sharpe': np.nan,
            'best_month': np.nan,
            'worst_month': np.nan,
            'mtd': np.nan,
            'pos_month_perc': np.nan,
            'avg_up_month': np.nan,
            'avg_down_month': np.nan,
            'three_month': np.nan,
            'monthly_skew': np.nan,
            'monthly_kurt': np.nan,
            'six_month': np.nan,
            'ytd': np.nan,
            'one_year': np.nan,
            'yearly_mean': np.nan,
            'yearly_vol': np.nan,
            'yearly_sharpe': np.nan,
            'best_year': np.nan,
            'worst_year': np.nan,
            'three_year': np.nan,
            'win_year_perc': np.nan,
            'twelve_month_win_perc': np.nan,
            'yearly_skew': np.nan,
            'yearly_kurt': np.nan,
            'five_year': np.nan,
            'ten_year':  np.nan,
            'return_table': {}
        }

        if len(daily_price) is 1:
            return self

        # Stats with daily prices
        r = calc_returns(daily_price)

        if len(r) < 4:
            return self

        self.stats['daily_mean'] = DAYS_IN_TRADING_YEAR * r.mean()
        self.stats['daily_vol'] = np.sqrt(DAYS_IN_TRADING_YEAR) * r.std()
        self.stats['daily_sharpe'] = (self.stats['daily_mean'] - daily_risk_free_return) / self.stats['daily_vol']
        self.stats['best_day'] = r.ix[r.idxmax():r.idxmax()]
        self.stats['worst_day'] = r.ix[r.idxmin():r.idxmin()]
        self.stats['total_return'] = (daily_price[-1] / daily_price[0]) - 1.0
        self.stats['ytd'] = self.stats['total_return']
        self.stats['cagr'] = calc_cagr(daily_price)
        self.stats['incep'] = self.stats['cagr']
        drawdown_info = self.drawdown_info()
        self.stats['max_drawdown'] = drawdown_info['drawdown'].min()
        self.stats['avg_drawdown'] = drawdown_info['drawdown'].mean()
        self.stats['avg_drawdown_days'] = drawdown_info['days'].mean()
        self.stats['daily_skew'] = r.skew()
        self.stats['daily_kurt'] = r.kurt() if len(r[(~np.isnan(r)) & (r != 0)]) > 0 else np.nan

        # Stats with monthly prices
        mr = calc_returns(monthly_price)

        if len(mr) < 2:
            return self

        self.stats['monthly_mean'] = MONTHS_IN_YEAR * mr.mean()
        self.stats['monthly_vol'] = np.sqrt(MONTHS_IN_YEAR) * mr.std()
        self.stats['monthly_sharpe'] = (self.stats['monthly_mean'] - monthly_risk_free_return) / self.stats['monthly_vol']
        self.stats['best_month'] = mr.ix[mr.idxmax():mr.idxmax()]
        self.stats['worst_month'] = mr.ix[mr.idxmin():mr.idxmin()]
        self.stats['mtd'] = (daily_price[-1] / monthly_price[-2]) - 1.0 # -2 because monthly[1] = daily[-1]
        self.stats['pos_month_perc'] = len(mr[mr > 0]) / float(len(mr) - 1.0) # -1 to ignore first NaN
        self.stats['avg_up_month'] = mr[mr > 0].mean()
        self.stats['avg_down_month'] = mr[mr <= 0].mean()

        # Table for lookback periods
        self.stats['return_table'] = collections.defaultdict(dict)
        for mi in mr.index:
            self.stats['return_table'][mi.year][mi.month] = mr[mi]
        fidx = mr.index[0]
        try:
            self.stats['return_table'][fidx.year][fidx.month] = (float(monthly_price[0]) / daily_price[0]) - 1
        except ZeroDivisionError:
            self.stats['return_table'][fidx.year][fidx.month] = 0.0
        # Calculate YTD
        for year, months in self.stats['return_table'].items():
            self.stats['return_table'][year][13] = np.prod(np.array(months.values()) + 1) - 1.0

        if len(mr) < 3:
            return self

        denominator = daily_price[:daily_price.index[-1] - pd.DateOffset(months=3)]
        self.stats['three_month'] = (daily_price[-1] / denominator[-1]) - 1 if len(denominator) > 0 else np.nan

        if len(mr) < 4:
            return self

        self.stats['monthly_skew'] = mr.skew()
        self.stats['monthly_kurt'] = mr.kurt() if len(mr[(~np.isnan(mr)) & (mr != 0)]) > 0 else np.nan

        denominator = daily_price[:daily_price.index[-1] - pd.DateOffset(months=6)]
        self.stats['six_month'] = (daily_price[-1] / denominator[-1]) - 1 if len(denominator) > 0 else np.nan

        # Stats with yearly prices
        yr = calc_returns(yearly_price)

        if len(yr) < 2:
            return self

        self.stats['ytd'] = (daily_price[-1] / yearly_price[-2]) - 1.0

        denominator = daily_price[:daily_price.index[-1] - pd.DateOffset(years=1)]
        self.stats['one_year'] = (daily_price[-1] / denominator[-1]) - 1 if len(denominator) > 0 else np.nan

        self.stats['yearly_mean'] = yr.mean()
        self.stats['yearly_vol'] = yr.std()
        self.stats['yearly_sharpe'] = (self.stats['yearly_mean'] - yearly_risk_free_return) / self.stats['yearly_vol']
        self.stats['best_year'] = yr.ix[yr.idxmax():yr.idxmax()]
        self.stats['worst_year'] = yr.ix[yr.idxmin():yr.idxmin()]

        # Annualize stat for over 1 year
        self.stats['three_year'] = calc_cagr(daily_price[daily_price.index[-1] - pd.DateOffset(years=3):])
        self.stats['win_year_perc'] = len(yr[yr > 0]) / float(len(yr) - 1.0)
        self.stats['twelve_month_win_perc'] = (monthly_price.pct_change(11) > 0).sum() / float(len(monthly_price) - (MONTHS_IN_YEAR - 1.0))

        if len(yr) < 4:
            return self

        self.stats['yearly_skew'] = yr.skew()
        self.stats['yearly_kurt'] = yr.kurt() if len(yr[(~np.isnan(yr)) & (yr != 0)]) > 0 else np.nan
        self.stats['five_year'] = calc_cagr(daily_price[daily_price.index[-1] - pd.DateOffset(years=5):])
        self.stats['ten_year'] = calc_cagr(daily_price[daily_price.index[-1] - pd.DateOffset(years=10):])

        return self
        # pylint: enable=too-many-statements

    def display_stats(self):
        """
        Display talbe of stats.
        """
        stats = [
            ('start', 'Start', 'dt'),
            ('end', 'End', 'dt'),
            ('yearly_risk_free_return', 'Risk-free rate', 'p'),
            (None, None, None),
            ('total_return', 'Total Return', 'p'),
            ('daily_sharpe', 'Daily Sharpe', 'n'),
            ('cagr', 'CAGR', 'p'),
            ('max_drawdown', 'Max Drawdown', 'p'),
            ('market_cap', 'Market Cap', 't'),
            (None, None, None),
            ('mtd', 'MTD', 'p'),
            ('three_month', '3m', 'p'),
            ('six_month', '6m', 'p'),
            ('ytd', 'YTD', 'p'),
            ('one_year', '1Y', 'p'),
            ('three_year', '3Y (ann.)', 'p'),
            ('five_year', '5Y (ann.)', 'p'),
            ('ten_year', '10Y (ann.)', 'p'),
            ('incep', 'Since Incep. (ann.)', 'p'),
            (None, None, None),
            ('daily_sharpe', 'Daily Sharpe', 'n'),
            ('daily_mean', 'Daily Mean (ann.)', 'p'),
            ('daily_vol', 'Daily Vol (ann.)', 'p'),
            ('daily_skew', 'Daily Skew', 'n'),
            ('daily_kurt', 'Daily Kurt', 'n'),
            ('best_day', 'Best Day', 'pp'),
            ('worst_day', 'Worst Day', 'pp'),
            (None, None, None),
            ('monthly_sharpe', 'Monthly Sharpe', 'n'),
            ('monthly_mean', 'Monthly Mean (ann.)', 'p'),
            ('monthly_vol', 'Monthly Vol (ann.)', 'p'),
            ('monthly_skew', 'Monthly Skew', 'n'),
            ('monthly_kurt', 'Monthly Kurt', 'n'),
            ('best_month', 'Best Month', 'pp'),
            ('worst_month', 'Worst Month', 'pp'),
            (None, None, None),
            ('yearly_sharpe', 'Yearly Sharpe', 'n'),
            ('yearly_mean', 'Yearly Mean', 'p'),
            ('yearly_vol', 'Yearly Vol', 'p'),
            ('yearly_skew', 'Yearly Skew', 'n'),
            ('yearly_kurt', 'Yearly Kurt', 'n'),
            ('best_year', 'Best Year', 'pp'),
            ('worst_year', 'Worst Year', 'pp'),
            (None, None, None),
            ('avg_drawdown', 'Avg. Drawdown', 'p'),
            ('avg_drawdown_days', 'Avg. Drawdown Days', 'n'),
            ('avg_up_month', 'Avg. Up Month', 'p'),
            ('avg_down_month', 'Avg. Down Month', 'p'),
            ('win_year_perc', 'Win Year %', 'p'),
            ('twelve_month_win_perc', 'Win 12m %', 'p')
        ]

        data = []
        first_row = ['Stat']
        first_row.extend([self.stats['name']])
        data.append(first_row)

        for k, n, f in stats:
            # Blank row
            if k is None:
                row = [''] * len(data[0])
                data.append(row)
                continue

            row = [n]
            raw = self.stats[k]
            if f is None:
                row.append(raw)
            elif f == 'p':
                row.append(fmtp(raw))
            elif f == 'n':
                row.append(fmtn(raw))
            elif f == 't':
                row.append(fmttn(raw))
            elif f == 'pp':
                row.append(fmtp(raw[0]))
            elif f == 'dt':
                row.append(raw.strftime('%Y-%m-%d'))
            else:
                print 'bad'
            data.append(row)

        print tabulate.tabulate(data, headers='firstrow')

        return self

    def summary(self):
        """
        Displays summary of Asset.
        """
        print 'Summary of %s from %s to %s' % (self.stats['name'], self.stats['start'], self.stats['end'])
        print 'Annual risk-free rate considered: %s' %(fmtp(self.stats['yearly_risk_free_return']))
        print '\nSummary:'
        data = [[fmtp(self.stats['total_return']), fmtn(self.stats['daily_sharpe']),
                 fmtp(self.stats['cagr']), fmtp(self.stats['max_drawdown']), fmttn(self.stats['market_cap'])]]
        print tabulate.tabulate(data, headers=['Total Return', 'Sharpe', 'CAGR', 'Max Drawdown', 'Market Cap'])

        print '\nAnnualized Returns:'
        data = [[fmtp(self.stats['mtd']), fmtp(self.stats['three_month']), fmtp(self.stats['six_month']),
                 fmtp(self.stats['ytd']), fmtp(self.stats['one_year']), fmtp(self.stats['three_year']),
                 fmtp(self.stats['five_year']), fmtp(self.stats['ten_year']),
                 fmtp(self.stats['incep'])]]
        print tabulate.tabulate(data, headers=['MTD', '3M', '6M', 'YTD', '1Y', '3Y', '5Y', '10Y', 'Incep.'])

        print '\nPeriodic Returns:'
        data = [
            ['sharpe', fmtn(self.stats['daily_sharpe']), fmtn(self.stats['monthly_sharpe']), fmtn(self.stats['yearly_sharpe'])],
            ['mean', fmtp(self.stats['daily_mean']), fmtp(self.stats['monthly_mean']), fmtp(self.stats['yearly_mean'])],
            ['vol', fmtp(self.stats['daily_vol']), fmtp(self.stats['monthly_vol']), fmtp(self.stats['yearly_vol'])],
            ['skew', fmtn(self.stats['daily_skew']), fmtn(self.stats['monthly_skew']), fmtn(self.stats['yearly_skew'])],
            ['kurt', fmtn(self.stats['daily_kurt']), fmtn(self.stats['monthly_kurt']), fmtn(self.stats['yearly_kurt'])],
            ['best price', fmtp(self.stats['best_day'][0]), fmtp(self.stats['best_month'][0]), fmtp(self.stats['best_year'][0])],
            ['best time', self.stats['best_day'].index[0].strftime('%Y-%m-%d'), self.stats['best_month'].index[0].strftime('%Y-%m-%d'), \
                self.stats['best_year'].index[0].strftime('%Y-%m-%d')],
            ['worst price', fmtp(self.stats['worst_day'][0]), fmtp(self.stats['worst_month'][0]), fmtp(self.stats['worst_year'][0])],
            ['worst time', self.stats['worst_day'].index[0].strftime('%Y-%m-%d'), self.stats['worst_month'].index[0].strftime('%Y-%m-%d'), \
                self.stats['worst_year'].index[0].strftime('%Y-%m-%d')]
            ]
        print tabulate.tabulate(data, headers=['daily', 'monthly', 'yearly'])

        print '\nDrawdowns:'
        data = [
            [fmtp(self.stats['max_drawdown']), fmtp(self.stats['avg_drawdown']),
             fmtn(self.stats['avg_drawdown_days'])]]
        print tabulate.tabulate(data, headers=['max', 'avg', '# days'])

        print '\nMisc:'
        data = [['avg. up month', fmtp(self.stats['avg_up_month'])],
                ['avg. down month', fmtp(self.stats['avg_down_month'])],
                ['up year %', fmtp(self.stats['win_year_perc'])],
                ['12m up %', fmtp(self.stats['twelve_month_win_perc'])]]
        print tabulate.tabulate(data)

        return self

    # Class Helper Functions
    # --------------------------------------------------------------------------------------------------------------------------
    def describe(self):
        """
        Wrapper for pandas describe().
        """
        self.data.describe()

    def time_range(self, start=None, end=datetime.date.today(), freq='B'):
        """
        Return a specific time range of the Asset.
        """
        if isinstance(start, datetime.date) and isinstance(end, datetime.date):
            date_range = pd.date_range(start, end, freq=freq)
        else:
            date_range = pd.date_range(end - datetime.timedelta(days=start), periods=start, freq=freq)
            return Asset(self.symbol, self.data.loc[date_range])

    def plot(self):
        """
        Wrapper for pandas plot().
        """
        plt.figure()
        self.data[['Open', 'Close', 'High', 'Low']].plot(figsize=(16, 4), title='{} OCHL Price'.format(self.symbol.upper()))

        plt.figure()
        self.data[['Volume']].plot(figsize=(16, 4), title='{} Volume'.format(self.symbol.upper()))

        plt.figure()
        ax3 = (100.0 * self.returns()).hist(figsize=(16, 4), bins=100, normed=1)
        (100.0 * self.returns()).plot(kind='kde', ax=ax3)
        ax3.set_title('{} Daily Return Distribution'.format(self.symbol.upper()))

        plt.figure()
        ax4 = (100.0 * self.returns(freq='M')).hist(figsize=(16, 4), bins=100, normed=1)
        (100.0 * self.returns(freq='M')).plot(kind='kde', ax=ax4)
        ax4.set_title('{} Monthly Return Distribution'.format(self.symbol.upper()))

    # Bring underlying data to class properties
    # --------------------------------------------------------------------------------------------------------------------------
    @property
    def number_of_days(self):
        """
        Return total number of days in price data.
        """
        return len(self.close)

    @property
    def close(self):
        """
        Return closing price of asset.
        """
        return self.data['Close']

    @property
    def c(self):
        """
        Return closing price of asset.
        """
        return self.close

    @property
    def adj_close(self):
        """
        Return adjusted closing price of asset.
        """
        return self.data['Adj_Close']

    @property
    def ac(self):
        """
        Return adjusted closing price of asset.
        """
        return self.adj_close

    @property
    def open(self):
        """
        Return opening price of asset.
        """
        return self.data['Open']

    @property
    def o(self):
        """
        Return opening price of asset.
        """
        return self.open

    @property
    def high(self):
        """
        Return high price of asset.
        """
        return self.data['High']

    @property
    def h(self):
        """
        Return high price of asset.
        """
        return self.high

    @property
    def low(self):
        """
        Return low price of asset.
        """
        return self.data['Low']

    @property
    def l(self):
        """
        Return low price of asset.
        """
        return self.low

    @property
    def volume(self):
        """
        Return volume of asset.
        """
        return self.data['Volume']

    @property
    def v(self):
        """
        Return volume of asset.
        """
        return self.volume

    # Common Price Transformations
    # --------------------------------------------------------------------------------------------------------------------------
    def money_flow(self):
        """
        Calculate money flow.
                     (close - low) - (high - close)
        money flow = ------------------------------
                             (high - low)
        """
        return ((self.close - self.low) - (self.high - self.close)) / (self.high - self.low)

    def money_flow_volume(self):
        """
        Calculate money flow volume.
        money flow volume = money flow * volume
        """
        return self.money_flow() * self.volume

    def typical_price(self):
        """
        Calculate typical price.
                        (high + low + close)
        typical price = --------------------
                                 3
        """
        return (self.high + self.low + self.close) / 3.0

    def close_to_open_range(self):
        """
        Calculate close to open range.
        close to open range = open - last close
        """
        return self.open - self.close.shift(1)

    def quadrant_range(self):
        """
        Calculate quandrant range.
        l_i = i * (high - low) / 4, for i = [1, 4]
        """
        size = self.high_low_spread() / 4.0
        l1 = self.low
        l2 = l1 + size
        l3 = l2 + size
        l4 = l3 + size
        l5 = l4 + size
        return pd.DataFrame({'1': l1, '2': l2, '3': l3, '4': l4, '5': l5})

    def true_range(self):
        """
        Calculate true range.
            true range = high - last low
        """
        return self.high - self.low.shift(1)

    def high_low_spread(self):
        """
        Calculate high low spread.
            high low spread = high - low
        """
        return self.high - self.low

    def rate_of_change(self, n=20):
        """
        Calculate rate of change.
                                   close - last close
            rate of change = 100 * ------------------
                                       last close
        """
        return 100.0 * (self.close - self.close.shift(n)) / self.close.shift(n)

    def roc(self, n=20):
        """
        Calculate rate of change.
                                   close - last close
            rate of change = 100 * ------------------
                                       last close
        """
        return self.rate_of_change(n)

    def drawdown(self):
        """
        Calucate the drawdown from the highest high.
        """
        # Don't change original data
        draw_down = self.close.copy()

        # Fill missing data
        draw_down = draw_down.ffill()

        # Ignore initial NaNs
        draw_down[np.isnan(draw_down)] = -np.Inf

        # Get highest high
        highest_high = draw_down.expanding().max()
        draw_down = (draw_down / highest_high) - 1.0
        return draw_down

    def drawdown_info(self):
        """
        Return table of drawdown data.
        """
        drawdown = self.drawdown()
        is_zero = drawdown == 0

        # Find start and end time
        start = ~is_zero & is_zero.shift(1)
        start = list(start[start].index)
        end = is_zero & (~is_zero).shift(1)
        end = list(end[end].index)

        # Handle no ending
        if len(end) is 0:
            end.append(drawdown.index[-1])

        # Handle startingin drawdown
        if start[0] > end[0]:
            start.insert(0, drawdown.index[0])

        # Handle finishing with drawdown
        if start[-1] > end[-1]:
            end.append(drawdown.index[-1])

        info = pd.DataFrame({
            'start': start,
            'end'  : end,
            'days' : [(e - s).days for s, e in zip(start, end)],
            'drawdown':[drawdown[s:e].min() for s, e in zip(start, end)]
        })

        return info

    # Overlays
    # --------------------------------------------------------------------------------------------------------------------------
    def bollinger_bands(self, n=20, k=2):
        """
        Calculate Bollinger Bands.
        """
        ma = pd.rolling_mean(self.close, n)
        ub = ma + k * pd.rolling_std(self.close, n)
        lb = ma - k * pd.rolling_std(self.close, n)
        return pd.DataFrame({'ub': ub, 'mb': ma, 'lb': lb})

    def chandelier_exit(self, n=22, k=3):
        """
        Calculate Chandelier Exit.
        """
        atr = self.atr(n)
        n_day_high = pd.rolling_max(self.high, n)
        n_day_low = pd.rolling_min(self.low, n)
        chdlr_exit_long = n_day_high - k * atr
        chdlr_exit_short = n_day_low  - k * atr
        return pd.DataFrame({'long': chdlr_exit_long, 'short': chdlr_exit_short})

    def ichimoku_clouds(self, n1=9, n2=26, n3=52):
        """
        Calculate Ichimoku Clouds.
        """
        high = self.high
        low = self.low
        conversion = (pd.rolling_max(high, n1) + pd.rolling_min(low, n1)) / 2.0
        base = (pd.rolling_max(high, n2) + pd.rolling_min(low, n2)) / 2.0
        leading_a = (conversion + base) / 2.0
        leading_b = (pd.rolling_max(high, n3) + pd.rolling_min(low, n3)) / 2.0
        lagging = self.close.shift(-n2)
        return pd.DataFrame({'conversion' : conversion, 'base': base, 'leadA': leading_a, 'leadB': leading_b, 'lag': lagging})

    def keltner_channels(self, n=20, natr=10):
        """
        Calculate Keltner Channels.
        """
        atr = self.atr(natr)
        ml = ema(self.close, n)
        ul = ml + 2.0 * atr
        ll = ml - 2.0 * atr
        return pd.DataFrame({'ul': ul, 'ml': ml, 'll': ll})

    def moving_average_envelopes(self, n=20, k=0.025):
        """
        Calculate Moving Average Envelopes.
        """
        close = self.close
        ma = sma(close, n)
        uma = ma + (k * ma)
        lma = ma - (k * ma)
        return pd.DataFrame({'uma': uma, 'ma': ma, 'lma': lma})

    def parabolic_sar(self, step_r=0.02, step_f=0.02, max_af_r=0.2, max_af_f=0.2):
        """
        Calculate Parabolic SAR.
        """
        high = self.high
        low = self.low
        r_sar = pd.TimeSeries(np.zeros(len(high)), index=high.index)
        f_sar = pd.TimeSeries(np.zeros(len(high)), index=high.index)
        ep = high[0]
        af = step_r
        sar = low[0]
        up = True

        for i in range(1, len(high)):
            if up:
                # Rising SAR
                ep = np.max([ep, high[i]])
                af = np.min([af + step_r if (ep == high[i]) else af, max_af_r])
                sar = sar + af * (ep - sar)
                r_sar[i] = sar
            else:
                # Falling SAR
                ep = np.min([ep, low[i]])
                af = np.min([af + step_f if (ep == low[i]) else af, max_af_f])
                sar = sar + af * (ep - sar)
                f_sar[i] = sar
            # Trend switch
            if up and (sar > low[i] or sar > high[i]):
                up = False
                sar = ep
                af = step_f
            elif not up and (sar < low[i] or sar < high[i]):
                up = True
                sar = ep
                af = step_r

        return pd.DataFrame({'rising' : r_sar, 'falling': f_sar})

    def pivot_point(self):
        """
        Calculate pivot point
        """
        p = self.typical_price()
        hl = self.high_low_spread()
        s1 = (2.0 * p) - self.high
        s2 = p - hl
        r1 = (2.0 * p) - self.low
        r2 = p + hl
        return pd.DataFrame({'p': p, 's1': s1, 's2': s2, 'r1': r1, 'r2': r2})

    def fibonacci_pivot_point(self):
        """
        Calculate Fibonacci Pivot Point.
        """
        p = self.typical_price()
        hl = self.high_low_spread()
        s1 = p - 0.382 * hl
        s2 = p - 0.618 * hl
        s3 = p - 1.0 * hl
        r1 = p + 0.382 * hl
        r2 = p + 0.618 * hl
        r3 = p + 1.0 * hl
        return pd.DataFrame({'p': p, 's1': s1, 's2': s2, 's3': s3, 'r1': r1, 'r2': r2, 'r3': r3})

    def demark_pivot_point(self):
        """
        Calculate Demark Pivot Point.
        """
        h_l_c = self.close < self.open
        h_lc = self.close > self.open
        hl_c = self.close == self.open
        p = np.zeros(len(self.close))
        p[h_l_c] = self.high[h_l_c] + 2.0 * self.low[h_l_c] + self.close[h_l_c]
        p[h_lc] = 2.0 * self.high[h_lc] + self.low[h_lc] + self.close[h_lc]
        p[hl_c] = self.high[hl_c] + self.low[hl_c] + 2.0 * self.close[hl_c]
        s1 = p / 2.0 - self.high
        r1 = p / 2.0 - self.low
        p = p / 4.0
        return pd.DataFrame({'p': p, 's1': s1, 'r1': r1})

    def price_channel(self, n=20):
        """
        Calculate Price Channel.
        """
        n_day_high = pd.rolling_max(self.high, n)
        n_day_low = pd.rolling_min(self.low, n)
        center = (n_day_high + n_day_low) / 2.0
        return pd.DataFrame({'high': n_day_high, 'low': n_day_low, 'center': center})

    def volume_by_price(self, n=14, block_num=12):
        """
        Calculate Volume by Price.
        """
        close = self.close
        volume = self.volume
        nday_closing_high = pd.rolling_max(close, n).bfill()
        nday_closing_low = pd.rolling_min(close, n).bfill()
        # Compute price blocks: rolling high low range in block number steps
        price_blocks = pd.SpareSeries()
        for low, high, in zip(nday_closing_low, nday_closing_high):
            price_blocks = price_blocks.append(pd.DataFrame(np.linspace(low, high, block_num)).T)
        price_blocks = price_blocks.set_index(close.index)
        # Find correct block for each price, then tally that days volume
        volume_by_price = pd.DataFrame(np.zeros((close.shape[0], block_num)))
        for j in range(n-1, close.shape[0]):
            for i, c in enumerate(close[j-(n-1):j+1]):
                block = (price_blocks.iloc[i, :] <= c).sum() - 1.0
                block = 0 if block < 0 else block
                volume_by_price.iloc[j, block] = volume[i] + volume_by_price.iloc[j, block]
        volume_by_price = volume_by_price.set_index(close.index)
        return volume_by_price

    def volume_weighted_average_price(self):
        """
        Calculate Volume Weighted Average Price (VWAP)."""
        tp = self.typical_price()
        return (tp * self.volume).cumsum() / self.volume.cumsum()
    def vwap(self):
        """Alias for volume_weighted_average_price()."""
        return self.volume_weighted_average_price()

    def zigzag(self, percent=7.0):
        """
        Calculate Zigzag.
        """
        x = self.close
        zigzag = pd.TimeSeries(np.zeros(self.number_of_days), index=x.index)
        lastzig = x[0]
        zigzag[0] = x[0]
        for i in range(1, self.number_of_days):
            if np.abs((lastzig - x[i]) / x[i]) > percent / 100.0:
                zigzag[i] = x[i]
                lastzig = x[i]
            else:
                zigzag[i] = None
        return pd.Series.interpolate(zigzag)

    # Indicators
    # --------------------------------------------------------------------------------------------------------------------------
    def accumulation_distribution_line(self):
        """
        Calculate Aaccumulation Distribution Line (ADL).
        """
        return self.money_flow_volume().cumsum()
    def adl(self):
        """
        Alias for accumulation_distribution_line().
        """
        return self.accumulation_distribution_line()

    def aroon(self, n=25):
        """
        Calculate aroon.
        """
        high = self.high
        n_day_high = pd.rolling_max(high, n, 0)
        highs = high[high == n_day_high]
        time_since_last_max = (highs.index.values[1:] - highs.index.values[0:-1]).astype('timedelta64[D]').astype(int)
        day_b4_high = (high == n_day_high).shift(-1).fillna(False)
        days_since_high = pd.TimeSeries(np.nan + np.ones(len(high)), index=high.index)
        days_since_high[day_b4_high] = time_since_last_max
        days_since_high[high == n_day_high] = 0.0
        days_since_high = days_since_high.interpolate('time').astype(int).clip_upper(n)
        low = self.low
        n_day_low = pd.rolling_min(low, n, 0)
        lows = low[low == n_day_low]
        time_since_last_min = (lows.index.values[1:] - lows.index.values[0:-1]).astype('timedelta64[D]').astype(int)
        day_b4_low = (low == n_day_low).shift(-1).fillna(False)
        days_since_low = pd.TimeSeries(np.nan + np.ones(len(low)), index=low.index)
        days_since_low[day_b4_low] = time_since_last_min
        days_since_low[low == n_day_low] = 0.0
        days_since_low = days_since_low.interpolate('time').astype(int).clip_upper(n)
        aroon_up = 100.0 * ((n - days_since_high) / n)
        aroon_dn = 100.0 * ((n - days_since_low) / n)
        aroon_osc = aroon_up - aroon_dn
        return pd.DataFrame({'up': aroon_up, 'down': aroon_dn, 'oscillator': aroon_osc})

    def average_directional_index(self, n=14):
        """
        Calculate Average Directional Index (ADX).
        """
        tr = self.true_range()
        pdm = pd.TimeSeries(np.zeros(len(tr)), index=tr.index)
        ndm = pd.TimeSeries(np.zeros(len(tr)), index=tr.index)
        pdm[(self.high - self.high.shift(1)) > (self.low.shift(1) - self.low)] = (self.high - self.high.shift(1))
        ndm[(self.low.shift(1) - self.low) > (self.high - self.high.shift(1))] = (self.low.shift(1) - self.low)
        trn = ema(tr, n)
        pdmn = ema(pdm, n)
        ndmn = ema(ndm, n)
        pdin = pdmn / trn
        ndin = ndmn / trn
        dx = ((pdin - ndin) / (pdin + ndin)).abs()
        adx = ((n-1) * dx.shift(1) + dx) / n
        return adx
    def adx(self, n=14):
        """
        Alias for average_directional_index().
        """
        return self.average_directional_index(n)

    def average_true_range(self, n=14):
        """
        Calculate Average True Range.
        !!!!!this is not a 100% correct - redo!!!!!
        """
        tr = self.true_range()
        return ((n-1) * tr.shift(1) + tr) / n
    def atr(self, n=14):
        """
        Alias foraverage_true_range().
        !!!!!this is not a 100% correct - redo!!!!!
        """
        return self.average_true_range(n)

    def bandwidth(self, n=20, k=2):
        """
        Calculate Bandwidth.
        """
        bb = self.bollinger_bands(n, k)
        return (bb['ub'] - bb['lb']) / bb['mb']

    def percent_b(self, n=20, k=2):
        """
        Calculate Percent B.
        """
        bb = self.bollinger_bands(n, k)
        return (self.close.shift(1) - bb['lb']) / (bb['ub'] - bb['lb'])

    def commodity_channel_index(self, n=20):
        """
        Calculate Commodity Channel Index (CCI).
        """
        tp = self.typical_price()
        return (tp - pd.rolling_mean(tp, n)) / (0.015 * pd.rolling_std(tp, n))
    def cci(self, n=20):
        """
        Alias for commodity_channel_index().
        """
        return self.commodity_channel_index(n)

    def coppock_curve(self, n1=10, n2=14, n3=11):
        """
        Calculate Coppock Curve.
        !!!!!fix!!!!!
        """
        window = range(n1)
        return pd.rolling_window(self.roc(n2), window) + self.roc(n3)

    def chaikin_money_flow(self, n=20):
        """
        Calculate Chaikin Money Flow.
        """
        return pd.rolling_sum((self.money_flow_volume()), n) / pd.rolling_sum(self.volume, n)
    def cmf(self, n=20):
        """Alias for chaikin_money_flow()."""
        return self.chaikin_money_flow(n)

    def chaikin_oscillator(self, n1=3, n2=10):
        """
        Calculate Chaikin Oscillator.
        """
        return ema(self.adl(), n1) - ema(self.adl(), n2)

    def price_momentum_oscillator(self, n1=20, n2=35, n3=10):
        """
        Calculate Price Momentum Oscillator (PMO).
        """
        pmo = ema(10 * ema((100 * (self.close / self.close.shift(1))) - 100.0, n2), n1)
        signal = ema(pmo, n3)
        return pd.DataFrame({'pmo': pmo, 'signal': signal})
    def pmo(self, n1=20, n2=35, n3=10):
        """
        Alias for price_momentum_oscillator().
        """
        return self.price_momentum_oscillator(n1, n2, n3)

    def detrended_price_oscillator(self, n=20):
        """
        Calculate Detrended Price Oscillator (DPO).
        """
        return self.close.shift(int(n / 2.0 + 1.0)) - sma(self.close, n)
    def dpo(self, n=20):
        """
        Alias for detrended_price_oscillator().
        """
        return self.detrended_price_oscillator(n)

    def ease_of_movement(self, n=14):
        """
        Calculate Ease Of Movement.
        """
        high_low_avg = (self.high + self.low) / 2.0
        distance_moved = high_low_avg - high_low_avg.shift(1)
        box_ratio = (self.volume / 100000000.0) / (self.high - self.low)
        emv = distance_moved / box_ratio
        return sma(emv, n)

    def force_index(self, n=13):
        """
        Calculate Force Index.
        """
        force_index = self.close - self.close.shift(1) * self.volume
        return ema(force_index, n)

    def know_sure_thing(self, n_sig=9):
        """
        Calculate Know Sure Thing.
        """
        rcma1 = sma(self.roc(10), 10)
        rcma2 = sma(self.roc(15), 10)
        rcma3 = sma(self.roc(20), 10)
        rcma4 = sma(self.roc(30), 15)
        kst = rcma1 + 2.0 * rcma2 + 3.0 * rcma3 + 4.0 * rcma4
        kst_signal = sma(kst, n_sig)
        return pd.DataFrame({'kst': kst, 'signal': kst_signal})
    def kst(self, n_sig=9):
        """
        Alias for know_sure_thing().
        """
        return self.know_sure_thing(n_sig)

    def mass_index(self, n1=9, n2=25):
        """
        Calculate Mass Index.
        """
        ema1 = ema(self.high_low_spread(), n1)
        ema2 = ema(ema1, n1)
        ema_ratio = ema1 / ema2
        return pd.rolling_sum(ema_ratio, n2)

    def moving_avg_converge_diverge(self, sn=26, fn=12, n_sig=9):
        """
        Calculate moving avgerage convergence divergence (MACD).
        """
        macd = ema(self.close, fn) - ema(self.close, sn)
        macd_signal = ema(macd, n_sig)
        macd_hist = macd - macd_signal
        return pd.DataFrame({'macd': macd, 'signal': macd_signal, 'hist': macd_hist})
    def macd(self, sn=26, fn=12, n_sig=9):
        """
        Alias for moving_avg_converge_diverge().
        """
        return self.moving_avg_converge_diverge(sn, fn, n_sig)

    def money_flow_index(self, n=14):
        """
        Calculate Money Flow Index.
        """
        tp = self.typical_price()
        rmf = tp * self.volume
        pmf = rmf.copy()
        nmf = rmf.copy()
        pmf[pmf < 0] = 0.0
        nmf[nmf > 0] = 0.0
        mfr = pd.rolling_sum(pmf, n) / pd.rolling_sum(nmf, n)
        return 100.0 - (100.0 / (1.0 + mfr))

    def negative_volume_index(self, n=255):
        """
        Calculate Negative Volume Index.
        """
        pct_change = self.returns().cumsum()
        # forward fill when volumes increase with last percent change of a volume decrease day
        pct_change[self.volume > self.volume.shift(1)] = None
        pct_change = pct_change.ffill()
        nvi = 1000.0 + pct_change
        nvi_signal = ema(nvi, n)
        return pd.DataFrame({'nvi': nvi, 'signal': nvi_signal})
    def nvi(self, n=255):
        """
        Alias for negative_volume_index().
        """
        return self.negative_volume_index(n)

    def on_balance_volume(self):
        """
        Calculate On Balance Volume.
        """
        p_obv = self.volume.astype(float)
        n_obv = (-1.0 * p_obv.copy())
        p_obv[self.close < self.close.shift(1)] = 0.0
        n_obv[self.close > self.close.shift(1)] = 0.0
        p_obv[self.close == self.close.shift(1)] = None
        n_obv[self.close == self.close.shift(1)] = None
        obv = p_obv + n_obv
        return obv.ffill().cumsum()
    def obv(self):
        """
        Alias for on_balance_volume().
        """
        return self.on_balance_volume

    def percentage_price_oscillator(self, n1=12, n2=26, n3=9):
        """
        Calculate Percentage Price Oscillator.
        """
        ppo = 100.0 * (ema(self.close, n1) - ema(self.close, n2)) / ema(self.close, n2)
        ppo_signal = ema(ppo, n3)
        ppo_hist = ppo - ppo_signal
        return pd.DataFrame({'ppo': ppo, 'signal': ppo_signal, 'hist': ppo_hist})
    def ppo(self, n1=12, n2=26, n3=9):
        """
        Alias for percentage_price_oscillator().
        """
        return self.percentage_price_oscillator(n1, n2, n3)

    def percentage_volume_oscillator(self, n1=12, n2=26, n3=9):
        """
        Calculate Percentage Volume Oscillator.
        """
        pvo = 100.0 * (ema(self.volume, n1) - ema(self.volume, n2)) / ema(self.volume, n2)
        pvo_signal = ema(pvo, n3)
        pvo_hist = pvo - pvo_signal
        return pd.DataFrame({'pvo': pvo, 'signal': pvo_signal, 'hist': pvo_hist})
    def pvo(self, n1=12, n2=26, n3=9):
        """
        Alias percentage_volume_oscillator().
        """
        return self.percentage_volume_oscillator(n1, n2, n3)

    def relative_strength_index(self, n=14):
        """
        Calculate Relative Strength Index.
        """
        change = self.close - self.close.shift(1)
        gain = change.copy()
        loss = change.copy()
        gain[gain < 0] = 0.0
        loss[loss > 0] = 0.0
        loss = -1.0 * loss
        avg_gain = pd.TimeSeries(np.zeros(len(gain)), index=change.index)
        avg_loss = pd.TimeSeries(np.zeros(len(loss)), index=change.index)
        avg_gain[n] = gain[0:n].sum() / n
        avg_loss[n] = loss[0:n].sum() / n
        for i in range(n+1, len(gain)):
            avg_gain[i] = (n-1) * (avg_gain[i-1] / n) + (gain[i] / n)
            avg_loss[i] = (n-1) * (avg_loss[i-1] / n) + (loss[i] / n)
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
    def rsi(self, n=14):
        """
        Alias for relative_strength_index().
        """
        return self.relative_strength_index(n)

    def stock_charts_tech_ranks(self, n=None, w=None):
        """
        Calculate Stock Charts Tech Ranks/
        """
        n = n if n else RANK_DAYS_IN_TRADING_YEAR
        w = w if w else RANK_PERCENTS
        close = self.close
        long_ma = 100.0 * (1 - close / ema(close, n[0]))
        long_roc = self.roc(n[1])
        medium_ma = 100.0 * (1.0 - close / ema(close, n[2]))
        medium_roc = self.roc(n[3])
        ppo = self.ppo()
        short_ppo_m = 100.0 * ((ppo['hist'] - ppo['hist'].shift(n[4])) / n[4]) / 2.0
        short_rsi = self.rsi(n[5])
        return w[0] * long_ma + w[1] * long_roc + w[2] * medium_ma + w[3] * medium_roc + w[4] * short_ppo_m + w[5] * short_rsi
    def sctr(self, n=None, w=None):
        """
        Alias for stock_charts_tech_ranks().
        """
        return self.stock_charts_tech_ranks(n, w)

    def slope(self):
        """
        Calculate slope.
        """
        close = self.close
        return pd.TimeSeries(np.zeros(len(close)), index=close.index)

    def volatility(self, n=20):
        """
        Calculate volatility.
        """
        return pd.rolling_std(self.close, n)

    def stochastic_oscillator(self, n=20, n1=3):
        """
        Calculate Stochastic Oscillator.
        """
        n_day_high = pd.rolling_max(self.high, n)
        n_day_low = pd.rolling_min(self.low, n)
        percent_k = 100.0 * (self.close - n_day_low) / (n_day_high - n_day_low)
        percent_d = sma(percent_k, n1)
        return pd.DataFrame({'k': percent_k, 'd': percent_d})

    def stochastic_rsi(self, n=20):
        """
        Calculate Stochastic RSI.
        """
        rsi = self.rsi(n)
        high_rsi = pd.rolling_max(rsi, n)
        low_rsi = pd.rolling_min(rsi, n)
        return (rsi - low_rsi) / (high_rsi - low_rsi)

    def trix(self, n=15):
        """
        Calculate TRIX.
        """
        ema1 = ema(self.close, n)
        ema2 = ema(ema1, n)
        ema3 = ema(ema2, n)
        return ema3.pct_change()

    def true_strength_index(self, n1=25, n2=13):
        """
        Calculate True Strength Index.
        """
        pc = self.close - self.close.shift(1)
        ema1 = ema(pc, n1)
        ema2 = ema(ema1, n2)
        abs_pc = (self.close - self.close.shift(1)).abs()
        abs_ema1 = ema(abs_pc, n1)
        abs_ema2 = ema(abs_ema1, n2)
        return 100.0 * ema2 / abs_ema2
    def tsi(self, n1=25, n2=13):
        """
        Alias for true_strength_index().
        """
        return self.true_strength_index(n1, n2)

    def ulcer_index(self, n=14):
        """
        Calculate Ulcer Index.
        """
        percent_draw_down = 100.0 * (self.close - pd.rolling_max(self.close, n)) / pd.rolling_max(self.close, n)
        return np.sqrt(pd.rolling_sum(percent_draw_down * percent_draw_down, n) / n)

    def ultimate_oscillator(self, n1=7, n2=14, n3=28):
        """
        Calculate Ultimate Oscillator.
        """
        bp = self.close - pd.DataFrame([self.low, self.close.shift(1)]).min()
        hc_max = pd.DataFrame({'a': self.high, 'b': self.close.shift(1)}, index=bp.index).max(1)
        lc_min = pd.DataFrame({'a': self.low, 'b': self.close.shift(1)}, index=bp.index).min(1)
        tr = hc_max - lc_min
        a1 = pd.rolling_sum(bp, n1) / pd.rolling_sum(tr, n1)
        a2 = pd.rolling_sum(bp, n2) / pd.rolling_sum(tr, n2)
        a3 = pd.rolling_sum(bp, n3) / pd.rolling_sum(tr, n3)
        return 100.0 * (4.0 * a1 + 2.0 * a2 + a3) / (4.0 + 2.0 + 1.0)

    def vortex(self, n=14):
        """
        Calculate Vortex.
        """
        pvm = self.high - self.low.shift(1)
        nvm = self.low - self.high.shift(1)
        pvm14 = pd.rolling_sum(pvm, n)
        nvm14 = pd.rolling_sum(nvm, n)
        hc_abs = (self.high - self.close.shift(1)).abs()
        lc_abs = (self.low - self.close.shift(1)).abs()
        tr = pd.DataFrame({'a': self.high_low_spread(), 'b': hc_abs, 'c': lc_abs}, index=pvm.index).max(1)
        tr14 = pd.rolling_sum(tr, n)
        pvi14 = pvm14 / tr14
        nvi14 = nvm14 / tr14
        return pd.DataFrame({'+': pvi14, '-': nvi14})

    def william_percent_r(self, n=14):
        """
        Calculate William Percent R.
        """
        high_max = pd.rolling_max(self.high, n)
        low_min = pd.rolling_min(self.low, n)
        return -100.0 * (high_max - self.close) / (high_max - low_min)

    # Charting
    # --------------------------------------------------------------------------------------------------------------------------
    def gaps(self):
        """
        Calculate gaps.
        """
        o = self.open
        c = self.close
        c2o = self.close_to_open_range()
        gap = pd.TimeSeries(np.zeros(len(c)), index=c.index)
        gap[o > c.shift()] = c2o
        gap[o < c.shift()] = c2o
        return gap

    def speedlines(self, n=20):
        """
        Calculate Speedlines.
        """

        high = self.high
        n_day_high = pd.rolling_max(high, n, 0)
        highs = high[high == n_day_high]
        time_since_last_max = (highs.index.values[1:] - highs.index.values[0:-1]).astype('timedelta64[D]').astype(int)
        day_b4_high = (high == n_day_high).shift(-1).fillna(False)
        days_since_high = pd.TimeSeries(np.nan + np.ones(len(high)), index=high.index)
        days_since_high[day_b4_high] = time_since_last_max
        days_since_high[high == n_day_high] = 0.0
        days_since_high = days_since_high.interpolate('time').astype(int).clip_upper(n)

        low = self.low
        n_day_low = pd.rolling_min(low, n, 0)
        lows = low[low == n_day_low]
        time_since_last_min = (lows.index.values[1:] - lows.index.values[0:-1]).astype('timedelta64[D]').astype(int)
        day_b4_low = (low == n_day_low).shift(-1).fillna(False)
        days_since_low = pd.TimeSeries(np.nan + np.ones(len(low)), index=low.index)
        days_since_low[day_b4_low] = time_since_last_min
        days_since_low[low == n_day_low] = 0.0
        days_since_low = days_since_low.interpolate('time').astype(int).clip_upper(n)

        trend_length = (days_since_high - days_since_low)
        trend = trend_length
        days_behind = pd.TimeSeries(np.zeros(len(low)), index=low.index)
        days_behind[trend > 0] = days_since_low
        days_behind[trend < 0] = days_since_high
        p = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)
        p2_3 = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)
        p1_3 = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)
        base = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)

        p[trend > 0] = n_day_low
        p[trend < 0] = n_day_high
        base[trend > 0] = n_day_high
        base[trend < 0] = n_day_low
        p2_3[trend > 0] = n_day_high - ((2.0 / 3.0) * (n_day_high - n_day_low))
        p2_3[trend < 0] = n_day_low  + ((2.0 / 3.0) * (n_day_high - n_day_low))
        p1_3[trend > 0] = n_day_high - ((1.0 / 3.0) * (n_day_high - n_day_low))
        p1_3[trend < 0] = n_day_low  + ((1.0 / 3.0) * (n_day_high - n_day_low))
        p = p.ffill()
        base = base.ffill()
        p2_3 = p2_3.ffill()
        p1_3 = p1_3.ffill()
        p_slope = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)
        p2_3_slope = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)
        p1_3_slope = pd.TimeSeries(np.nan + np.zeros(len(low)), index=low.index)
        p_slope[trend > 0] = ((base - p) / (n + trend_length))
        p_slope[trend < 0] = ((base - p) / (n - trend_length))
        p2_3_slope[trend > 0] = ((base - p2_3) / (n + trend_length))
        p2_3_slope[trend < 0] = ((base - p2_3) / (n - trend_length))
        p1_3_slope[trend > 0] = ((base - p1_3) / (n + trend_length))
        p1_3_slope[trend < 0] = ((base - p1_3) / (n - trend_length))
        p_slope = p_slope.ffill()
        p2_3_slope = p2_3_slope.ffill()
        p1_3_slope = p1_3_slope.ffill()
        p_now = p    + (p_slope    * days_behind)
        # p2_3_now = p2_3 + (p2_3_slope * days_behind)
        # p1_3_now = p1_3 + (p1_3_slope * days_behind)

        return pd.DataFrame({'p': p_now, 'p2/3': p2_3, 'p1/3': p1_3})

    # Return Asset Performance
    # --------------------------------------------------------------------------------------------------------------------------
    def returns(self, periods=1, freq=None):
        """
        Calculate returns of asset over interval period and frequency offset freq string:
        B   business day frequency
        C   custom business day frequency (experimental)
        D   calendar day frequency
        W   weekly frequency
        M   month end frequency
        BM  business month end frequency
        MS  month start frequency
        BMS business month start frequency
        Q   quarter end frequency
        BQ  business quarter endfrequency
        QS  quarter start frequency
        BQS business quarter start frequency
        A   year end frequency
        BA  business year end frequency
        AS  year start frequency
        BAS business year start frequency
        H   hourly frequency
        T   minutely frequency
        S   secondly frequency
        L   milliseonds
        U   microseconds
        """
        return self.close.pct_change(periods=periods, freq=freq)

    def price_returns(self, periods=1):
        """
        Calculate price change over period.
        """
        return (self.close - self.close.shift(periods)).fillna(0)

    def arithmetic_return(self, periods=1, freq=None):
        """
        Calculate arithmetic return.
        """
        returns = self.returns(periods=periods, freq=freq).fillna(0)
        return 100.0 * np.mean(returns)

    def geometric_return(self, periods=1, freq=None):
        """
        Calculate geometric return.
        """
        returns = self.returns(periods=periods, freq=freq).fillna(0)
        return 100.0 * (scipy.stats.gmean(1.0 + returns) - 1.0)

    def rate_of_return(self, periods=DAYS_IN_TRADING_YEAR, freq=None):
        """
        Calculate rate of return over time period freq, default to yearly (DAYS_IN_TRADING_YEAR days).
        """
        returns = self.returns(periods=periods, freq=freq).fillna(0)
        return returns / periods

    def price_delta(self, start=None, end=None):
        """
        Calculate returns between dates, defaults to total return.
        """
        end = end if end else -1
        start = start if start else 0
        return self.close[end] - self.close[start]

    def total_return(self, start=None, end=None):
        """
        Calculate returns between dates, defaults to total return.
        """
        start = start if start else 0
        return 100.0 * self.price_delta(start=start, end=end) / self.close[start]

    def return_on_investment(self, periods=DAYS_IN_TRADING_YEAR, freq=None):
        """
        Calculate Return on Investment (ROI).
        """
        pass
    def roi(self, periods=DAYS_IN_TRADING_YEAR, freq=None):
        """
        Alias for return_on_investment().
        """
        return self.return_on_investment(periods=periods, freq=freq)

    def compound_annual_growth_rate(self, start=None, end=None):
        """
        Calculate Compound Annual Growth Rate (CAGR).
        """
        end = end if end else -1
        start = start if start else 0
        enddate = self.close.index[end]
        startdate = self.close.index[start]
        years = (enddate - startdate).days / DAYS_IN_YEAR
        return np.power((self.close[end] / self.close[start]), (1.0 / years)) - 1.0

    def cagr(self, start=None, end=None):
        """
        Alias for compound_annual_growth_rate().
        """
        return self.compound_annual_growth_rate(start=start, end=end)

    # Risk Performance
    # --------------------------------------------------------------------------------------------------------------------------
    def deviation_risk(self):
        """
        Calculate Deviation Risk.
        """
        return self.returns().std()

    # Risk Adjusted Performance
    # --------------------------------------------------------------------------------------------------------------------------
    def risk_return_ratio(self):
        """
        Calculate Sharpe Ratio w/o Risk-Free Rate.
        """
        daily_ret = self.returns()
        return np.sqrt(DAYS_IN_TRADING_YEAR) * daily_ret.mean() / daily_ret.std()

    def information_ratio(self, benchmark):
        """
        Caluculate the information ratio relative to a benchmark.
        """
        return_delta = self.returns() - benchmark.returns()
        return return_delta.mean() / return_delta.std()

    # Market Comparisons
    # --------------------------------------------------------------------------------------------------------------------------
    def sharpe_ratio(self, market):
        """
        Calcualte Sharpe Ratio against benchmark.
        """
        return_delta = self.returns() - market.returns()
        return return_delta.mean() / return_delta.std()

    def annualized_sharpe_ratio(self, market, N=DAYS_IN_TRADING_YEAR):
        """
        Calculate Annualized Sharpe Ratio against benchmark.
        """
        return np.sqrt(N) * self.sharpe_ratio(market)

    def equity_sharpe(self, market, risk_free_rate=RISK_FREE_RATE, N=DAYS_IN_TRADING_YEAR):
        """
        Calculate the Equity sharpe against a benchmark and Risk-Free Rate.
        """
        excess_returns = self.returns() - risk_free_rate / N
        return_delta = excess_returns - market.returns()
        return np.sqrt(N) * return_delta.mean() / return_delta.std()

    def beta(self, market):
        """
        Calcualte the Beta to a benchmark.
        """
        cov = np.cov(self.close.returns(), market.close.returns())
        return cov[0, 1] / cov[1, 1]

    def alpha(self, market, risk_free_rate=RISK_FREE_RATE):
        """
        Calculate the Alpha to a benchmark.
        """
        return self.close.returns().mean() - risk_free_rate - self.beta(market) * (market.close.returns().mean() - risk_free_rate)

    def r_squared(self, market, risk_free_rate=RISK_FREE_RATE):
        """
        Calculate R-squared.
        """
        eps_i = 0.0
        r_i = self.alpha(market) + self.beta(market) * (market.close.returns() - risk_free_rate) + eps_i + risk_free_rate
        cov = np.cov(self.close.returns(), market.close.returns())
        ss_res = np.power(r_i - self.close.returns(), 2.0)
        ss_tot = cov[0, 0] * (len(self.close.returns()) - 1.0)
        return 1.0 - (ss_res / ss_tot)

    # Package it all up...idk, used mostly to test there are no errors
    # --------------------------------------------------------------------------------------------------------------------------
    def all_indicators(self):
        """
        Calculate all indicators for the asset.
        """
        # Indicators that return multiple variables, seperated later
        quadrant_range = self.quadrant_range()
        bollinger_bands = self.bollinger_bands()
        chandelier_exit = self.chandelier_exit()
        ichimoku_clouds = self.ichimoku_clouds()
        keltner_channels = self.keltner_channels()
        moving_average_envelopes = self.moving_average_envelopes()
        parabolic_sar = self.parabolic_sar()
        pivot_point = self.pivot_point()
        fibonacci_pivot_point = self.fibonacci_pivot_point()
        demark_pivot_point = self.demark_pivot_point()
        price_channel = self.price_channel()
        aroon = self.aroon()
        price_momentum_oscillator = self.price_momentum_oscillator()
        know_sure_thing = self.know_sure_thing()
        macd = self.macd()
        negative_volume_index = self.negative_volume_index()
        percentage_price_oscillator = self.percentage_price_oscillator()
        percentage_volume_oscillator = self.percentage_volume_oscillator()
        stochastic_oscillator = self.stochastic_oscillator()
        vortex = self.vortex()
        # Return all indicators
        return pd.DataFrame({
            'return'                   : self.returns(),
            'money_flow'               : self.money_flow(),
            'money_flow_volume'        : self.money_flow_volume(),
            'typical_price'            : self.typical_price(),
            'close_to_open_range'      : self.close_to_open_range(),
            'l1_quadrant_range'        : quadrant_range['1'],
            'l2_quadrant_range'        : quadrant_range['2'],
            'l3_quadrant_range'        : quadrant_range['3'],
            'l4_quadrant_range'        : quadrant_range['4'],
            'l5_quadrant_range'        : quadrant_range['5'],
            'true_range'               : self.true_range(),
            'high_low_spread'          : self.high_low_spread(),
            'roc'                      : self.rate_of_change(),
            'upper_bollinger_band'     : bollinger_bands['ub'],
            'center_bollinger_band'    : bollinger_bands['mb'],
            'lower_bollinger_band'     : bollinger_bands['lb'],
            'long_chandelier_exit'     : chandelier_exit['long'],
            'short_chandelier_exit'    : chandelier_exit['short'],
            'conversion_ichimoku_cloud': ichimoku_clouds['conversion'],
            'base_line_ichimoku_cloud' : ichimoku_clouds['base'],
            'leadingA_ichimoku_cloud'  : ichimoku_clouds['leadA'],
            'leadingB_ichimoku_cloud'  : ichimoku_clouds['leadB'],
            'lagging_ichimoku_cloud'   : ichimoku_clouds['lag'],
            'upper_keltner_channel'    : keltner_channels['ul'],
            'center_keltner_channel'   : keltner_channels['ml'],
            'lower_keltner_channel'    : keltner_channels['ll'],
            'upper_ma_envelope'        : moving_average_envelopes['uma'],
            'center_ma_envelope'       : moving_average_envelopes['ma'],
            'lower_ma_envelope'        : moving_average_envelopes['lma'],
            'rising_parabolic_sar'     : parabolic_sar['rising'],
            'falling_parabolic_sar'    : parabolic_sar['falling'],
            'p_pivot_point'            : pivot_point['p'],
            's1_pivot_point'           : pivot_point['s1'],
            's2_pivot_point'           : pivot_point['s2'],
            'r1_pivot_point'           : pivot_point['r1'],
            'r2_pivot_point'           : pivot_point['r2'],
            'p_fibonacci_pivot_point'  : fibonacci_pivot_point['p'],
            's1_fibonacci_pivot_point' : fibonacci_pivot_point['s1'],
            's2_fibonacci_pivot_point' : fibonacci_pivot_point['s2'],
            's3_fibonacci_pivot_point' : fibonacci_pivot_point['s3'],
            'r1_fibonacci_pivot_point' : fibonacci_pivot_point['r1'],
            'r2_fibonacci_pivot_point' : fibonacci_pivot_point['r2'],
            'r3_fibonacci_pivot_point' : fibonacci_pivot_point['r3'],
            'p_demark_pivot_point'     : demark_pivot_point['p'],
            's1_demark_pivot_point'    : demark_pivot_point['s1'],
            'r1_demark_pivot_point'    : demark_pivot_point['r1'],
            'high_price_channel'       : price_channel['high'],
            'low_price_channel'        : price_channel['low'],
            'center_price_channel'     : price_channel['center'],
            'volume_by_price'          : self.volume_by_price(),
            'vwap'                     : self.volume_weighted_average_price(),
            'zigzag'                   : self.zigzag(),
            'adl'                      : self.accumulation_distribution_line(),
            'aroon_up'                 : aroon['up'],
            'aroon_down'               : aroon['down'],
            'aroon_oscillator'         : aroon['oscillator'],
            'adx'                      : self.average_directional_index(),
            'atr'                      : self.average_true_range(),
            'bandwidth'                : self.bandwidth(),
            '%b'                       : self.percent_b(),
            'cci'                      : self.commodity_channel_index(),
            'coppock_curve'            : self.coppock_curve(),
            'chaikin_money_flow'       : self.chaikin_money_flow,
            'chaikin_oscillator'       : self.chaikin_oscillator(),
            'pmo'                      : price_momentum_oscillator['pmo'],
            'pmo_signal'               : price_momentum_oscillator['signal'],
            'dpo'                      : self.detrended_price_oscillator(),
            'ease_of_movement'         : self.ease_of_movement(),
            'force_index'              : self.force_index(),
            'kst'                      : know_sure_thing['kst'],
            'kst_signal'               : know_sure_thing['signal'],
            'mass_index'               : self.mass_index(),
            'macd'                     : macd['macd'],
            'macd_signal'              : macd['signal'],
            'macd_hist'                : macd['hist'],
            'money_flow_index'         : self.money_flow_index(),
            'nvi'                      : negative_volume_index['nvi'],
            'nvi_signal'               : negative_volume_index['signal'],
            'obv'                      : self.on_balance_volume,
            'ppo'                      : percentage_price_oscillator['ppo'],
            'ppo_signal'               : percentage_price_oscillator['signal'],
            'ppo_hist'                 : percentage_price_oscillator['hist'],
            'pvo'                      : percentage_volume_oscillator['pvo'],
            'pvo_signal'               : percentage_volume_oscillator['signal'],
            'pvo_hist'                 : percentage_volume_oscillator['hist'],
            'rsi'                      : self.relative_strength_index(),
            'sctr'                     : self.stock_charts_tech_ranks(),
            's'                        : self.slope(),
            'volatility'               : self.volatility(),
            '%k_stochastic_oscillator' : stochastic_oscillator['k'],
            '%d_stochastic_oscillator' : stochastic_oscillator['d'],
            'stochastic_rsi'           : self.stochastic_rsi(),
            'trix'                     : self.trix(),
            'tsi'                      : self.true_strength_index(),
            'ulcer_index'              : self.ulcer_index(),
            'ultimate_oscillator'      : self.ultimate_oscillator(),
            '+vortex'                  : vortex['+'],
            '-vortex'                  : vortex['-'],
            'william_percent_r'        : self.william_percent_r()
        })
