# region IMPORT LIBRARIES
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import datetime
import copy
import math

from helpers import calc_swing_highs
from helpers import calc_swing_lows
from helpers import process_swing
from helpers import atr
from helpers import find_previous_swing
from helpers import check_positions
from helpers import plot_line
from helpers import plot_marker
from helpers import plot_trace
from helpers import cal_sharpe
from helpers import cal_drawdown
from helpers import finding_fractal
from helpers import find_previous_swing_index
from helpers import collection_from_mongodb
from helpers import count_check
from helpers import two_check
from helpers import three_check
from helpers import plot_line_no_name

from fractal_01 import find_swing_point
from fractal_01 import figure_fractal
# endregion

# region VARIABLES
# 1$ = 0.1 lot x 1 pips
# lot = 0.1* money / pips
# Ex: 0.1* 100$ / 10 = 1 lot
fund = 1000
percent = 0.01
stop_margin = 1.5

# Plot cummulative returns in %
plot_cumret = 0
# Plot to html file
plot_all = 1

# save all positions to a csv file
generate_result = 0
# calculate positions entry, SL, TP
find_position = 1

# ----------------------------------------------------------------- #
# train from 2012 to 2020
# test from 2020 to 2024

format_day = '%Y-%m-%d %H:%M'
format_hour = '%Y-%m-%d %H:%M'
from_day = '2022-12-01' # days imported from MongoDb
to_day = '2024-01-15'
from_day_cal = '2023-03-01' # days for calculating
to_day_cal = '2023-06-30'

year = datetime.datetime.strptime(to_day_cal, '%Y-%m-%d').year
csv_name = f"result/AU_{year}.csv"
# csv_name = "result/AU_2015-2023.csv"
# endregion

# region IMPORT DATA
m15 = collection_from_mongodb('AUDUSD_M15')
m15 = m15[(m15['text_id'] >= from_day_cal) & (m15['text_id'] <= to_day_cal)]
m15['time'] = pd.to_datetime(m15['time'], format = format_hour)
m15.set_index('time', inplace=True)

# m15=m15.drop_duplicates(subset=['text_id'], keep='first')
h1 = m15.resample('1h').asfreq() # Resample to 1 hour frequency
h4 = m15.resample('4h').asfreq() # Resample to 4 hour frequency 
day = m15.resample('1d').asfreq() # Resample to 1 day frequency
# endregion

# calculate m15, swing
m15, swing = find_swing_point(m15, h1, h4, day)

# region CALCULATE ATR
m15 = atr(m15, length=14, smoothing='RMA')

# define atr's stop
m15['atr_up'] = m15['high'] + m15['ATR']*stop_margin
m15['atr_down'] = m15['low'] - m15['ATR']*stop_margin
# endregion

# -------------------------------------------------------#
# from this point on, select only the part I want to test
m15 = m15[(m15['text_id'] >= from_day) & (m15['text_id'] <= to_day)]

# region SIGNAL NO.1
# the previous candle's high is in the upper h1 band
sell_cond_1 = m15['high'].between(m15['h1_up_cal'], m15['h1_big_cal'], inclusive='both')
# the previous candle is the highest
sell_cond_2 = m15['high'] >= m15['high'].rolling(window=5).max().shift(1)
signal_sell = sell_cond_1 & sell_cond_2
# the current candle close is lower than the previous candle
confirm_sell_1 = (m15['close'] <= m15['high'].shift(1))
# combine the previous candle signal
confirm_sell_2 = signal_sell.shift(1).fillna(False)
# the current candle is bearish
confirm_sell_3 = m15['close'] <= m15['open']
# the current candle is still lower than h1 upper band
confirm_sell_4 = m15['high'] <= m15['h1_big_cal']
# the current h1 upper band is lower than the previous, indicate a down trend
confirm_sell_5 = m15['sh_h1'] <= m15['sh_h1_pre1']

# confirm_sell = confirm_sell_1 & confirm_sell_2 & confirm_sell_3 & confirm_sell_4 & confirm_sell_5           
# m15['show_sell_cond'] = m15['high'].where(confirm_sell == True, None)
# endregion

# region SIGNAL NO.2
# candle formation
bull_bar = m15['open'] < m15['close']
bear_bar = m15['open'] > m15['close']
doji_bar = m15['open'] == m15['open']
length_bar = abs(m15['open'] - m15['close'])


# bear_bull_bull
candle_bounce_up = bear_bar.shift(2) & \
                   bull_bar.shift(1) & \
                   bull_bar

# bull_bear_bear
candle_bounce_down = bull_bar.shift(2) & \
                     bear_bar.shift(1) & \
                     bear_bar

# bar test the low L2 trace zone, not exceeding that
test_L2_low = (m15['low'] > m15['L2_small']) & \
              (m15['low'] < m15['L2_down']) &  \
              (m15['open'] < m15['L2_down']) & \
              (m15['close'] < (m15['L2_down']+m15['L2_up'])/2)

test_L2_high = (m15['high'] < m15['L2_big']) & \
              (m15['high'] > m15['L2_up']) &  \
              (m15['open'] > m15['L2_up']) & \
              (m15['close'] > (m15['L2_down']+m15['L2_up'])/2)              

confirm_buy = (m15['L2_down'] > 0) & \
                test_L2_low  & \
                bull_bar

confirm_sell = (m15['L2_up'] >0) & \
                test_L2_high & \
                bear_bar

# m15['show_sell_cond'] = m15['close'].where(confirm_sell == True, None)
# m15['show_buy_cond'] = m15['close'].where(confirm_buy == True, None)
# endregion

# region SIGNAL NO.3
doji_buy = (m15['open'] <= m15['close']) & \
    (2*(m15['close'] - m15['open']) <= (m15['open'] - m15['low'])) & \
    (2*(m15['close'] - m15['open']) <= (m15['high'] - m15['close']))
doji_sell = (m15['open'] >= m15['close']) & \
    (2*(m15['open'] - m15['close']) <= (m15['high'] - m15['open'])) & \
    (2*(m15['open'] - m15['close']) <= (m15['close'] - m15['low']))
confirm_buy = doji_buy.shift(1) & (m15['close'] > m15['open'])
confirm_sell = doji_sell.shift(1) & (m15['open'] > m15['close'])
# end region

# region POSITIONS series
# with entry, stop loss, take profit, closed, pnl
if find_position == 1:
    m15['confirm_sell'] = np.where(confirm_sell == True, True, False) # --------------------------------
    m15['confirm_buy'] = np.where(confirm_buy == True, True, False)

    m15['stop_loss'] = np.where(
        m15['confirm_buy']==True,
        m15['atr_down'],
        np.where(
            m15['confirm_sell']==True,
            m15['atr_up'],
            None)
    )

    m15['entry'] = np.where(
        (m15['confirm_buy']==True) | (m15['confirm_sell']==True),
        m15['close'],
        None
    )

    # m15['take_profit'] = np.where(
    #     m15['confirm_buy']==True,
    #     (m15['L2_big'] + m15['L2_up'])/2,
    #     np.where(
    #         m15['confirm_sell']==True,
    #         m15['L2_small'],
    #         None
    #     )
    # )

    m15['take_profit'] = np.where(
        m15['confirm_buy']==True,
        (m15['atr_up']),
        np.where(
            m15['confirm_sell']==True,
            m15['atr_down'],
            None
        )
    )

    positions = m15.dropna(subset=['entry', 'stop_loss', 'take_profit'])
    positions = positions[['entry', 'stop_loss', 'take_profit', 'confirm_buy', 'confirm_sell']]
    positions = check_positions(m15, positions, 'entry', 'stop_loss', 'take_profit', 'closed')
    positions['tp_pip'] = abs(positions['take_profit'] - positions['entry'])
    positions['sl_pip'] = abs(positions['entry'] - positions['stop_loss'])

    positions['pnl'] = np.where(
        positions['confirm_buy'], 
        positions['closed'] - positions['entry'], 
        np.where(
            positions['confirm_sell'], 
            positions['entry'] - positions['closed'], 
            None
        )
    )

    positions['R_theory'] = positions['tp_pip']/positions['sl_pip']
    positions['R'] = positions['pnl']/positions['sl_pip']

    positions['pnl_half'] = np.where(
        (positions['half'] & positions['confirm_buy']), 
        0.5*(positions['close_half']-positions['entry'])+ \
            np.maximum(0, 0.5*(positions['closed'] - positions['entry'])), 
        np.where(
            (positions['half'] & positions['confirm_sell']), 
            0.5*(positions['entry']-positions['close_half'])+ \
                np.maximum(0, 0.5*(positions['entry'] - positions['closed'])), 
            positions['pnl']
        )
    )

    # Close half position when price goes half way to take profit, move stop loss to break even for another half
    positions['R_half'] = positions.apply(lambda row: row['pnl_half']/row['sl_pip']
                                          if row['half']
                                          else row['R'], axis=1)
    positions['lot'] = 0.1*fund*percent/(positions['sl_pip']*10000)
    # open new position only after the old one closes
    sele_rows = []
    pre_closed_time = None

    # select only positions with R > 2
    # positions = positions[positions['R_theory'] >=2]

    # select a postion only the last one had closed or no positions before
    for index, row in positions.iterrows():
        if pre_closed_time is None or index >= pre_closed_time:
            sele_rows.append(row)
            pre_closed_time = row['closed_time']

    select_positions = pd.DataFrame(sele_rows)
# endregion

# region CALCULATE SHARPE, DRAWDOWN
if find_position == 1:
    cumret, maxDD, maxDDD, startDD = cal_drawdown(select_positions['R'])
    sharpe = cal_sharpe(select_positions['R'])
# endregion

fig = figure_fractal(m15,swing, select_positions)

# region FIG UPDATE LAYOUT-AXES, PLOT ALL
fig.update_layout(title='Candlestick Chart',
                  yaxis_title='Price',
                  xaxis=dict(rangeslider=dict(visible=False),
                             gridcolor='rgba(255, 255, 255, 0.2)'),
                  plot_bgcolor='rgb(17, 17, 17)',
                  paper_bgcolor='rgb(17, 17, 17)',
                  font=dict(color='white'),
                  yaxis=dict(
                    gridcolor='rgba(255, 255, 255, 0.2)'))

fig.update_xaxes(
    rangebreaks=[
        { 'pattern': 'day of week', 'bounds': [6, 1]}
    ]
)

if plot_all ==1 :
    fig.show()
# endregion

# region GENERATE CSV FILE
if generate_result == 1:
    result = select_positions[['entry', 'stop_loss', 'take_profit', 'lot']]
    result.to_csv(csv_name, header=False)
    print(len(select_positions))
# endregion

# region PRINT
# print(select_positions[['R', 'R_half']])
print("all of position: ", positions.shape)
print("selected positions: ", select_positions.shape)
print("sum R: ", sum(select_positions['R']))
print("sum R_half: ", sum(select_positions['R_half']))

# print("sharpe: ", sharpe)
# print("maxDD: ", maxDD)
if plot_cumret == 1:
    import matplotlib.pyplot as plt
    plt.plot(cumret)
    plt.show()
# endregion