# region IMPORT LIBRARIES

import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
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

# endregion

# region VARIABLES
# 1$ = 0.1 lot x 1 pips
# lot = 0.1* money / pips
# Ex: 0.1* 100$ / 10 = 1 lot

fund = 10000
percent = 0.01

stop_margin = 1.5

frtl_m15 = 5 # 5 6 7 8
frtl_h1 = 5 # 5 6 7 8
frtl_h4 = 5
frtl_day = 5

upper_band = 0.8 # 0.7 0.75 0.8 0.85 0.9
lower_band = 0.2 # 0.1 0.15 0.2 0.25 0.3

frtl_2 = 2

frtl_flag_m15 = 0
frtl_flag_h1 = 0
frtl_flag_h4 = 0
frtl_flag_day = 0

frtl_flag_m15_2 = 0

swing_m15 = 0
swing_h1 = 0
swing_h4 = 0

trace_m15 = 0
trace_h1 = 0
trace_h4 = 0

trace_atr = 0

trace_sell_cond = 1

plot_pre_sh_h1_1 = 0
plot_pre_sh_h1_2 = 0
plot_pre_sh_h1_3 = 0

plot_entry = 0
plot_stop_loss = 0
plot_take_profit = 0
plot_closed = 0

# endregion

# region VARIABLES FRACTALS
plot_L0 = 0
plot_L1 = 1
plot_L2 = 0
plot_L3 = 0
plot_L0_line = 0
plot_L0_pre_line = 0

plot_L1_line = 0
plot_L1_pre_line = 0

plot_L2_line = 1
plot_L2_pre_line = 0

plot_L3_line = 0
plot_L3_pre_line = 0

plot_L0_zigzag = 0
plot_L1_zigzag = 0
plot_L2_zigzag = 0
plot_L3_zigzag = 0

trace_L1 = 0
trace_L2 = 1
trace_L3 = 1

upper_band_L3 = 0.75
lower_band_L3 = 0.25

upper_band_L2 = 0.75
lower_band_L2 = 0.25

upper_band_L1 = 0.75
lower_band_L1 = 0.25

# endregion

# region VARIABLES PLOT ALL, INPUT DATA, color variables

# Plot cummulative returns in %
plot_cumret = 0
# Plot to html file
plot_all = 1

# save all positions to a csv file
generate_result = 0
# calculate positions entry, SL, TP
find_position = 1

format_day = "%d/%m/%Y"
format_hour = "%d/%m/%Y %H:%M"
from_day = "2022-01-01"
to_day = '2022-02-01'

data_m15 = "data/AUDUSD_M15.csv"
data_h1 = "data/AUDUSD_H1.csv"
data_h4 = "data/AUDUSD_H4.csv"
data_d1 = "data/AUDUSD_D.csv"

csv_name = "result/AU_2024_Jan_September.csv"

# data_d1 = "data/AU_D_2024.csv"
# data_h4 = "data/AU_H4_2024.csv"
# data_h1 = "data/AU_H1_2024.csv"
# data_m15 = "data/AU_M15_2024.csv"

violet = 'rgba(255, 87 , 51, 0.2)'
gray = 'rgba(213, 216, 220, 0.2)'
green = 'rgba(0, 255, 0, 0.2)'
red = 'rgba(255, 0, 0, 0.2)'
blue = 'rgba(0, 0, 255, 0.2)'
yellow = 'rgba(255, 255, 0, 0.2)'
pink = 'rgba(255, 0, 255, 0.2)'
orange = 'rgba(255, 138, 101, 0.2)'
ocean = 'rgba(41, 182, 246, 0.2)'

# endregion

# region IMPORT DATA

data_day = pd.read_csv(data_d1, parse_dates=True)
data_day['Time'] = pd.to_datetime(data_day['Time'], format = "%d/%m/%Y")
data_day.set_index('Time', inplace=True)

data_h1 = pd.read_csv(data_h1, parse_dates=True)
data_h1['Time'] = pd.to_datetime(data_h1['Time'], format = format_hour)
data_h1.set_index('Time', inplace=True)

data_h4 = pd.read_csv(data_h4, parse_dates=True)
data_h4['Time'] = pd.to_datetime(data_h4['Time'], format = format_hour)
data_h4.set_index('Time', inplace=True)

data_m15 = pd.read_csv(data_m15, parse_dates=True)
data_m15['Time'] = pd.to_datetime(data_m15['Time'], format = format_hour)
data_m15.set_index('Time', inplace=True)

m15 = data_m15.loc[from_day : to_day]
h1 = data_h1.loc[from_day : to_day]
h4 = data_h4.loc[from_day : to_day]
day = data_day.loc[from_day : to_day]

# endregion

# region FIND SWING POINT

m15 = calc_swing_highs(m15.copy(),frtl_m15, 'SwingHigh')
h1 = calc_swing_highs(h1.copy(),frtl_h1, 'SwingHigh')
h4 = calc_swing_highs(h4.copy(),frtl_h4, 'SwingHigh')
day = calc_swing_highs(day.copy(),frtl_day, 'SwingHigh')

m15 = calc_swing_lows(m15.copy(),frtl_m15, 'SwingLow')
h1 = calc_swing_lows(h1.copy(),frtl_h1, 'SwingLow')
h4 = calc_swing_lows(h4.copy(),frtl_h4, 'SwingLow')
day = calc_swing_lows(day.copy(),frtl_day, 'SwingLow')

# Additional fractal for entry
m15 = calc_swing_highs(m15.copy(),frtl_2, 'frtl_2_high')
m15 = calc_swing_lows(m15.copy(),frtl_2, 'frtl_2_low')

# endregion

# region CALCULATE ATR

m15 = atr(m15, length=14, smoothing='RMA')
m15['atr_up'] = m15['High'] + m15['ATR']*stop_margin
m15['atr_down'] = m15['Low'] - m15['ATR']*stop_margin

# endregion

# region CALCULATE SWING

day = process_swing(day,"SwingHigh","sh_day", "High")
day = process_swing(day,"SwingLow","sl_day", "Low")
day['sh_day'] = day['sh_day'].shift(frtl_day+1)
day['sl_day'] = day['sl_day'].shift(frtl_day+1)

h4 = process_swing(h4,"SwingHigh","sh_h4", "High")
h4 = process_swing(h4,"SwingLow","sl_h4", "Low")
h4['sh_h4'] = h4['sh_h4'].shift(frtl_h4+1)
h4['sl_h4'] = h4['sl_h4'].shift(frtl_h4+1)

h1 = process_swing(h1,"SwingHigh","sh_h1", "High")
h1 = process_swing(h1,"SwingLow","sl_h1", "Low")
h1['sh_h1'] = h1['sh_h1'].shift(frtl_h1+1)
h1['sl_h1'] = h1['sl_h1'].shift(frtl_h1+1)

m15 = process_swing(m15,"SwingHigh","sh_m15", "High")
m15 = process_swing(m15,"SwingLow","sl_m15", "Low")
m15['sh_m15'] = m15['sh_m15'].shift(frtl_m15+1)
m15['sl_m15'] = m15['sl_m15'].shift(frtl_m15+1)

# Additional fractal for entry
m15 = process_swing(m15,"frtl_2_high","sh_m15_2", "High")
m15 = process_swing(m15,"frtl_2_low","sl_m15_2", "Low")
m15['sh_m15_2'] = m15['sh_m15_2'].shift(frtl_2 + 1)
m15['sl_m15_2'] = m15['sl_m15_2'].shift(frtl_2 + 1)

# endregion

# region CALCULATE OFFSET

swh_m15 = m15[m15['SwingHigh']]
swl_m15 = m15[m15['SwingLow']]
offset_m15 = 0.02 * (swh_m15['High'].max() - swh_m15['Low'].min())

swh_line_h1 = h1[h1['sh_h1'].notna()]
swl_line_h1 = h1[h1['sl_h1'].notna()]
swh_h1 = h1[h1['SwingHigh']]
swl_h1 = h1[h1['SwingLow']]
offset_h1 = 0.02 * (swh_h1['High'].max() - swh_h1['Low'].min())

swh_line_h4 = h4[h4['sh_h4'].notna()]
swl_line_h4 = h4[h4['sl_h4'].notna()]
swh_h4 = h4[h4['SwingHigh']]
swl_h4 = h4[h4['SwingLow']]
offset_h4 = 0.02 * (swh_h4['High'].max() - swh_h4['Low'].min())

swh_line_day = day[day['sh_day'].notna()]
swl_line_day = day[day['sl_day'].notna()]
swh_day = day[day['SwingHigh']]
swl_day = day[day['SwingLow']]
offset_day = 0.02 * (swh_day['High'].max() - swh_day['Low'].min())

# Additional fractal for entry
swh_m15_2 = m15[m15['frtl_2_high']]
swl_m15_2 = m15[m15['frtl_2_low']]

# endregion

# region MAP DATA TO 15MIN
# Create continuous points of swing high low

m15['sh_h1'] = swh_line_h1['sh_h1'].reindex(m15.index, method='ffill')
m15['sl_h1'] = swl_line_h1['sl_h1'].reindex(m15.index, method='ffill')

m15['sh_h4'] = swh_line_h4['sh_h4'].reindex(m15.index, method='ffill')
m15['sl_h4'] = swl_line_h4['sl_h4'].reindex(m15.index, method='ffill')

m15['sh_day'] = swh_line_day['sh_day'].reindex(m15.index, method='ffill')
m15['sl_day'] = swl_line_day['sl_day'].reindex(m15.index, method='ffill')

# endregion

# region CALCULATE M15, H1 BAND

m15['m15_band'] = m15['sh_m15'] - m15['sl_m15']
m15['h1_band'] = m15['sh_h1'] - m15['sl_h1']

m15['h1_big'] = m15[['sh_h1', 'sl_h1']].max(axis=1)
m15['h1_small'] = m15[['sh_h1', 'sl_h1']].min(axis=1)
m15['h1_up'] = m15['h1_small'] + (m15['h1_big'] - m15['h1_small']) * upper_band
m15['h1_down'] = m15['h1_small'] + (m15['h1_big'] - m15['h1_small'])* lower_band

m15['m15_big'] = m15[['sh_m15', 'sl_m15']].max(axis=1)
m15['m15_small'] = m15[['sh_m15', 'sl_m15']].min(axis=1)
m15['m15_up'] = m15['m15_small'] + (m15['m15_big'] - m15['m15_small']) * upper_band
m15['m15_down'] = m15['m15_small'] + (m15['m15_big'] - m15['m15_small'])* lower_band

pd.set_option('future.no_silent_downcasting', True)
m15['h1_up_cal'] = m15['h1_up'].fillna(1.0)
m15['h1_big_cal'] = m15['h1_big'].fillna(1.0)
m15['h1_down_cal'] = m15['h1_down'].fillna(1.0)
m15['h1_small_cal'] = m15['h1_small'].fillna(1.0)

# endregion

# region FIND PREVIOUS MAJOR SWING

swh_h1_list = copy.deepcopy(swh_h1['High'])
swh_h1_list.index = swh_h1_list.index.shift(frtl_h1+1, freq='h')

swl_h1_list = copy.deepcopy(swl_h1['Low'])
swl_h1_list.index = swl_h1_list.index.shift(frtl_h1+1, freq='h')

m15['sh_h1_pre1'] = m15.apply(find_previous_swing, list = swh_h1_list.copy(), order = 1, value = 'sh_h1', axis=1)
m15['sh_h1_pre2'] = m15.apply(find_previous_swing, list = swh_h1_list.copy(), order = 2, value = 'sh_h1', axis=1)
m15['sh_h1_pre3'] = m15.apply(find_previous_swing, list = swh_h1_list.copy(), order = 3, value = 'sh_h1', axis=1)

m15['sl_h1_pre1'] = m15.apply(find_previous_swing, list = swl_h1_list.copy(), order = 1, value = 'sl_h1', axis=1)
m15['sl_h1_pre2'] = m15.apply(find_previous_swing, list = swl_h1_list.copy(), order = 2, value = 'sl_h1', axis=1)
m15['sl_h1_pre3'] = m15.apply(find_previous_swing, list = swl_h1_list.copy(), order = 3, value = 'sl_h1', axis=1)

# endregion

# region CREATE L0
m15['down_bar'] = m15['Close'] <= m15['Close'].shift(1)
m15['up_bar'] = m15['Close'] > m15['Close'].shift(1)
m15['L0_down'] = (m15['down_bar'].shift(1) & m15['up_bar']).fillna(False)
m15['L0_up'] = (m15['up_bar'].shift(1) & m15['down_bar']).fillna(False)
m15['High_shifted'] = m15['High'].shift(1)
m15['Low_shifted'] = m15['Low'].shift(1)
m15['L0_up_val'] = m15.apply(lambda row: max(row['High'], row['High_shifted']) if row['L0_up'] else None, axis=1)
m15['L0_down_val'] = m15.apply(lambda row: min(row['Low'], row['Low_shifted']) if row['L0_down'] else None, axis=1)
m15.drop(columns=['High_shifted'], inplace=True)
m15.drop(columns=['Low_shifted'], inplace=True)
m15 = process_swing(m15, 'L0_down', 'L0_down_valine', 'L0_down_val')
m15 = process_swing(m15, 'L0_up', 'L0_up_valine', 'L0_up_val')
L0_up = m15[m15['L0_up']]
L0_down = m15[m15['L0_down']]
L0_up_list = copy.deepcopy(L0_up['L0_up_val'])
L0_down_list = copy.deepcopy(L0_down['L0_down_val'])

# endregion

# region CREATE L1
h1['down_bar'] = h1['Close'] <= h1['Close'].shift(1)
h1['up_bar'] = h1['Close'] > h1['Close'].shift(1)
h1['L1_down'] = (h1['down_bar'].shift(1) & h1['up_bar']).fillna(False)
h1['L1_up'] = (h1['up_bar'].shift(1) & h1['down_bar']).fillna(False)
h1['High_shifted'] = h1['High'].shift(1)
h1['Low_shifted'] = h1['Low'].shift(1)
h1['L1_up_val'] = h1.apply(lambda row: max(row['High'], row['High_shifted']) if row['L1_up'] else None, axis=1)
h1['L1_down_val'] = h1.apply(lambda row: min(row['Low'], row['Low_shifted']) if row['L1_down'] else None, axis=1)
h1.drop(columns=['High_shifted'], inplace=True)
h1.drop(columns=['Low_shifted'], inplace=True)

h1 = process_swing(h1, 'L1_down', 'L1_down_valine', 'L1_down_val')
h1 = process_swing(h1, 'L1_up', 'L1_up_valine', 'L1_up_val')

L1_up_val = h1[h1['L1_up_val'].notna()]
L1_up_val_list = copy.deepcopy(L1_up_val['L1_up_val'])
L1_up_val_list.index = L1_up_val_list.index.shift(1, freq = 'h')

L1_down_val = h1[h1['L1_down_val'].notna()]
L1_down_val_list = copy.deepcopy(L1_down_val['L1_down_val'])
L1_down_val_list.index = L1_down_val_list.index.shift(1, freq = 'h')

m15['L1_up_val'] = L1_up_val_list.reindex(m15.index)
m15['L1_down_val'] = L1_down_val_list.reindex(m15.index)
m15['L1_up'] = h1['L1_up'].reindex(m15.index)
m15['L1_down'] = h1['L1_down'].reindex(m15.index)
m15['L1_down_valine'] = L1_down_val_list.reindex(m15.index, method='ffill')
m15['L1_up_valine'] = L1_up_val_list.reindex(m15.index, method='ffill')

# endregion

# region CREATE L2
h4['down_bar'] = h4['Close'] <= h4['Close'].shift(1)
h4['up_bar'] = h4['Close'] > h4['Close'].shift(1)
h4['L2_down'] = (h4['down_bar'].shift(1) & h4['up_bar']).fillna(False)
h4['L2_up'] = (h4['up_bar'].shift(1) & h4['down_bar']).fillna(False)
h4['High_shifted'] = h4['High'].shift(1)
h4['Low_shifted'] = h4['Low'].shift(1)
h4['L2_up_val'] = h4.apply(lambda row: max(row['High'], row['High_shifted']) if row['L2_up'] else None, axis=1)
h4['L2_down_val'] = h4.apply(lambda row: min(row['Low'], row['Low_shifted']) if row['L2_down'] else None, axis=1)
h4.drop(columns=['High_shifted'], inplace=True)
h4.drop(columns=['Low_shifted'], inplace=True)

h4 = process_swing(h4, 'L2_down', 'L2_down_valine', 'L2_down_val')
h4 = process_swing(h4, 'L2_up', 'L2_up_valine', 'L2_up_val')

L2_up_val = h4[h4['L2_up_val'].notna()]
L2_up_val_list = copy.deepcopy(L2_up_val['L2_up_val'])
L2_up_val_list.index = L2_up_val_list.index.shift(4, freq = 'h')

L2_down_val = h4[h4['L2_down_val'].notna()]
L2_down_val_list = copy.deepcopy(L2_down_val['L2_down_val'])
L2_down_val_list.index = L2_down_val_list.index.shift(4, freq = 'h')

m15['L2_up_val'] = L2_up_val_list.reindex(m15.index)
m15['L2_down_val'] = L2_down_val_list.reindex(m15.index)
m15['L2_up'] = h4['L2_up'].reindex(m15.index)
m15['L2_down'] = h4['L2_down'].reindex(m15.index)
m15['L2_down_valine'] = L2_down_val_list.reindex(m15.index, method='ffill')
m15['L2_up_valine'] = L2_up_val_list.reindex(m15.index, method='ffill')

# endregion

# region CREATE L3
day['down_bar'] = day['Close'] <= day['Close'].shift(1)
day['up_bar'] = day['Close'] > day['Close'].shift(1)
day['L3_down'] = (day['down_bar'].shift(1) & day['up_bar']).fillna(False)
day['L3_up'] = (day['up_bar'].shift(1) & day['down_bar']).fillna(False)
day['High_shifted'] = day['High'].shift(1)
day['Low_shifted'] = day['Low'].shift(1)
day['L3_up_val'] = day.apply(lambda row: max(row['High'], row['High_shifted']) if row['L3_up'] else None, axis=1)
day['L3_down_val'] = day.apply(lambda row: min(row['Low'], row['Low_shifted']) if row['L3_down'] else None, axis=1)
day.drop(columns=['High_shifted'], inplace=True)
day.drop(columns=['Low_shifted'], inplace=True)

day = process_swing(day, 'L3_down', 'L3_down_valine', 'L3_down_val')
day = process_swing(day, 'L3_up', 'L3_up_valine', 'L3_up_val')

L3_up_val = day[day['L3_up_val'].notna()]
L3_up_val_list = copy.deepcopy(L3_up_val['L3_up_val'])
L3_up_val_list.index = L3_up_val_list.index.shift(24, freq = 'h')

L3_down_val = day[day['L3_down_val'].notna()]
L3_down_val_list = copy.deepcopy(L3_down_val['L3_down_val'])
L3_down_val_list.index = L3_down_val_list.index.shift(24, freq = 'h')

m15['L3_up_val'] = L3_up_val_list.reindex(m15.index)
m15['L3_down_val'] = L3_down_val_list.reindex(m15.index)
m15['L3_up'] = day['L3_up'].reindex(m15.index)
m15['L3_down'] = day['L3_down'].reindex(m15.index)
m15['L3_down_valine'] = L3_down_val_list.reindex(m15.index, method='ffill')
m15['L3_up_valine'] = L3_up_val_list.reindex(m15.index, method='ffill')

# endregion

# region CREATE L1 TRACE ZONE
m15['L1_big'] = m15[['L1_down_valine', 'L1_up_valine']].max(axis=1)
m15['L1_small'] = m15[['L1_down_valine', 'L1_up_valine']].min(axis=1)
m15['L1_up'] = m15['L1_small'] + (m15['L1_big'] - m15['L1_small']) * upper_band_L3
m15['L1_down'] = m15['L1_small'] + (m15['L1_big'] - m15['L1_small'])* lower_band_L3
m15['L1_up_cal'] = m15['L1_up'].fillna(1.0)
m15['L1_down_cal'] = m15['L1_down'].fillna(1.0)
# endregion

# region CREATE L2 TRACE ZONE
m15['L2_big'] = m15[['L2_down_valine', 'L2_up_valine']].max(axis=1)
m15['L2_small'] = m15[['L2_down_valine', 'L2_up_valine']].min(axis=1)
m15['L2_up'] = m15['L2_small'] + (m15['L2_big'] - m15['L2_small']) * upper_band_L2
m15['L2_down'] = m15['L2_small'] + (m15['L2_big'] - m15['L2_small'])* lower_band_L2
m15['L2_up_cal'] = m15['L2_up'].fillna(1.0)
m15['L2_down_cal'] = m15['L2_down'].fillna(1.0)
# endregion

# region CREATE L3 TRACE ZONE
m15['L3_big'] = m15[['L3_down_valine', 'L3_up_valine']].max(axis=1)
m15['L3_small'] = m15[['L3_down_valine', 'L3_up_valine']].min(axis=1)
m15['L3_up'] = m15['L3_small'] + (m15['L3_big'] - m15['L3_small']) * upper_band_L3
m15['L3_down'] = m15['L3_small'] + (m15['L3_big'] - m15['L3_small'])* lower_band_L3
m15['L3_up_cal'] = m15['L3_up'].fillna(1.0)
m15['L3_down_cal'] = m15['L3_down'].fillna(1.0)
# endregion

# region CREATE ZIGZAG
m15['L0_zigzag'] = m15['L0_up_val'].combine_first(m15['L0_down_val'])
m15['L0_zigzag'] = m15['L0_zigzag'].interpolate()

m15['L1_zigzag'] = m15['L1_up_val'].combine_first(m15['L1_down_val'])
m15['L1_zigzag'] = m15['L1_zigzag'].interpolate()

m15['L2_zigzag'] = m15['L2_up_val'].combine_first(m15['L2_down_val'])
m15['L2_zigzag'] = m15['L2_zigzag'].interpolate()

m15['L3_zigzag'] = m15['L3_up_val'].combine_first(m15['L3_down_val'])
m15['L3_zigzag'] = m15['L3_zigzag'].interpolate()

#endregion

# region SELL CONDITION EX1

# the previous candle's high is in the upper h1 band
sell_cond_1 = m15['High'].between(m15['h1_up_cal'], m15['h1_big_cal'], inclusive='both')
# the previous candle is the highest
sell_cond_2 = m15['High'] >= m15['High'].rolling(window=5).max().shift(1)
signal_sell = sell_cond_1 & sell_cond_2
# the current candle close is lower than the previous candle
confirm_sell_1 = (m15['Close'] <= m15['High'].shift(1))
# combine the previous candle signal
confirm_sell_2 = signal_sell.shift(1).fillna(False)
# the current candle is bearish
confirm_sell_3 = m15['Close'] <= m15['Open']
# the current candle is still lower than h1 upper band
confirm_sell_4 = m15['High'] <= m15['h1_big_cal']
# the current h1 upper band is lower than the previous, indicate a down trend
confirm_sell_5 = m15['sh_h1'] <= m15['sh_h1_pre1']


# confirm_sell = confirm_sell_1 & confirm_sell_2 & confirm_sell_3 & confirm_sell_4 & confirm_sell_5           
# m15['show_sell_cond'] = m15['High'].where(confirm_sell == True, None)

# endregion

# region SELL CONDITION EX2

# candle formation
bull_bar = m15['Open'] < m15['Close']
bear_bar = m15['Open'] > m15['Close']
doji_bar = m15['Open'] == m15['Open']
length_bar = abs(m15['Open'] - m15['Close'])

# bear_bull_bull
candle_bounce_up = bear_bar.shift(2) & bull_bar.shift(1) & bull_bar

# bull_bear_bear
candle_bounce_down = bull_bar.shift(2) & bear_bar.shift(1) & bear_bar

# bar test the low L2 trace zone, not exceeding that
test_L2_low = (m15['Low'] > m15['L2_small']) & (m15['Low'] < m15['L2_down']) & (m15['Open'] < (m15['L2_up_cal'] + m15['L2_down_cal'])/2)

confirm_sell = (m15['L2_down'] > 0) & test_L2_low
m15['show_sell_cond'] = m15['Low'].where(confirm_sell == True, None)
# endregion

# region POSITIONS series
# with entry, stop loss, take profit, closed, pnl
if find_position == 1:
    m15['confirm_sell'] = np.where(confirm_sell == True, True, False)
    m15['stop_loss'] = m15.apply(lambda row: row['atr_up'] if row['confirm_sell'] else None, axis=1)
    m15['entry'] = m15.apply(lambda row: row['Close'] if row['confirm_sell'] else None, axis=1)
    m15['take_profit'] = m15.apply(lambda row: (row['h1_small_cal'] + row['h1_down_cal'])/2 if row['confirm_sell'] else None, axis=1)

    positions = m15.dropna(subset=['entry', 'stop_loss', 'take_profit'])
    positions = positions[['entry', 'stop_loss', 'take_profit']]
    positions = check_positions(m15, positions, 'entry', 'stop_loss', 'take_profit', 'closed')

    positions['tp_pip'] = positions['entry'] - positions['take_profit']
    positions['sl_pip'] = positions['stop_loss'] - positions['entry']
    positions['pnl'] = (positions['entry'] - positions['closed'])
    positions['R'] = positions['pnl']/positions['sl_pip']
    positions['pnl_half'] = positions.apply(lambda row: 0.5*(row['entry']-row['close_half']) +
                                        max(0, 0.5*(row['entry'] - row['closed']))
                                        if row['half'] else row['pnl'], axis=1)
    # Close half position when price goes half way to take profit, move stop loss to break even for another half
    positions['R_half'] = positions.apply(lambda row: row['pnl_half']/row['sl_pip'] if row['half'] else row['R'], axis=1)
    positions['lot'] = 0.1*fund*percent/(positions['sl_pip']*10000)
    # open new position only after the old one closes
    sele_rows = []
    pre_closed_time = None

    for index, row in positions.iterrows():
        if pre_closed_time is None or index >= pre_closed_time:
            sele_rows.append(row)
            pre_closed_time = row['closed_time']

    select_positions = pd.DataFrame(sele_rows)

# endregion

# region CALCULATE SHARPE, DRAWDOWN
if find_position == 1:
    sharpe = cal_sharpe(select_positions['R_half'])
    cumret, maxDD, maxDDD, startDD = cal_drawdown(np,select_positions['R_half'])

# endregion

# region PLOT FLAG

fig = go.Figure(data=[go.Candlestick(x = m15.index,
                                    open = m15['Open'],
                                    high = m15['High'],
                                    low = m15['Low'],
                                    close = m15['Close'],
                                    increasing_line_color='white',  
                                    decreasing_line_color='white',
                                    increasing_fillcolor='white',
                                    decreasing_fillcolor='black')])

if frtl_flag_m15 == 1:
    # Fractal high m15
    plot_marker(fig, go, swh_m15.index, swh_m15['High'] + offset_m15, 'markers', 'triangle-up', 'red', 5, 'Fractal Highs m15')
    # Fractal low m15
    plot_marker(fig, go, swl_m15.index, swl_m15['Low'] - offset_m15, 'markers', 'triangle-down', 'green', 5, 'Fractal Lows m15')

if frtl_flag_h1 == 1:
    # Fractal high h1
    plot_marker(fig, go, swh_h1.index, swh_h1['High'] + offset_h1, 'markers', 'triangle-up', 'cyan', 5, 'Swing Highs h1')
    # Fractal low h1
    plot_marker(fig, go, swl_h1.index, swl_h1['Low'] - offset_h1, 'markers', 'triangle-down', 'cyan', 5, 'Swing Lows h1')

if frtl_flag_h4 == 1:
    # Fractal high h4
    plot_marker(fig, go, swh_h4.index, swh_h4['High'], 'markers', 'triangle-up', 'cyan', 5, 'Swing Highs H4')
    # Fractal low h4
    plot_marker(fig, go, swl_h4.index, swl_h4['Low'], 'markers', 'triangle-down', 'purple', 5, 'Swing Low H4')

if frtl_flag_day == 1:    
    # Fractal high day
    plot_marker(fig, go, swh_day.index, swh_day['High'], 'markers', 'triangle-up', 'yellow', 5, 'Swing Highs day')
    # Fractal low h4
    plot_marker(fig, go, swl_day.index, swh_day['Low'], 'markers', 'triangle-down', 'yellow', 5, 'Swing Low day')

if frtl_flag_m15_2 == 1:
    # Fractal high m15 period 2
    plot_marker(fig, go, swh_m15_2.index, swh_m15_2['High'] + offset_m15, 'markers', 'triangle-up', 'red', 5, 'Fractal Highs m15')
    # Fractal low m15 period 2
    plot_marker(fig, go, swl_m15_2.index, swl_m15_2['Low'] - offset_m15, 'markers', 'triangle-down', 'green', 5, 'Fractal Lows m15')

# endregion

# region PLOT SWING, TRACE, ENTRY, PRE-SWING
if swing_m15 == 1:
    # Swing high m15
    plot_marker(fig, go, m15.index, m15['sh_m15'], 'markers', 'circle', 'red', 2, 'Swing High m15')
    # Swing low m15
    plot_marker(fig, go, m15.index, m15['sl_m15'], 'markers', 'circle', 'green', 2, 'Swing Low m15')

if swing_h1 == 1:
    # Swing high h1
    plot_marker(fig, go, m15.index, m15['sh_h1'], 'markers', 'triangle-up', 'cyan', 5, 'Swing High H1')
    # Swing low h1
    plot_marker(fig, go, m15.index, m15['sl_h1'], 'markers', 'triangle-down', 'purple', 5, 'Swing Low H1')

if swing_h4 == 1:
    # Swing high h4
    plot_marker(fig, go, m15.index, m15['sh_h4'], 'markers', 'triangle-up', 'yellow', 5, 'Swing High H4')
    # Swing low h4
    plot_marker(fig, go, m15.index, m15['sl_h4'], 'markers', 'triangle-down', 'orange', 5, 'Swing Low H4')

if trace_m15 == 1:
    # upper band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['m15_big'].tolist() + m15['m15_up'].tolist()[::-1],
                'toself',
                'rgba(220,100,80,0.2)',
                dict(color='rgba(0,0,0,0)'))
    # lower_band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['m15_down'].tolist() + m15['m15_small'].tolist()[::-1],
                'toself',
                'rgba(0,255,0,0.2)',
                dict(color='rgba(0,0,0,0)'))

if trace_h1 == 1:
    # upper band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['h1_big'].tolist() + m15['h1_up'].tolist()[::-1],
                'toself',
                'rgba(0,255,255,0.2)',
                dict(color='rgba(0,0,0,0)'))
    # lower_band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['h1_down'].tolist() + m15['h1_small'].tolist()[::-1],
                'toself',
                'rgba(0,255,0,0.2)',
                dict(color='rgba(0,0,0,0)'))

if trace_atr == 1:
    # ATR up
    plot_line(fig, go, m15.index, m15['atr_up'], 'lines', 1, 'rgba(0,255,0,0.3)', 'atr up')
    # ATR down
    plot_line(fig, go, m15.index, m15['atr_down'], 'lines', 1, 'rgba(0,255,0,0.3)', 'atr down')

if trace_sell_cond == 1:
    # sell condition
    plot_marker(fig, go, m15.index, m15['show_sell_cond'], 'markers', 'circle', 'rgba(0, 255, 0, 1)', 10, 'show sell condition')

if plot_entry == 1:
    # sell condition
    plot_marker(fig, go, select_positions.index, select_positions['entry'], 'markers', 'circle', 'green', 10, 'entry')

if plot_stop_loss == 1:
    # sell condition
    plot_marker(fig, go, select_positions.index, select_positions['stop_loss'], 'markers', 'circle', 'yellow', 10, 'stop loss')

if plot_take_profit == 1:
    # sell condition
    plot_marker(fig, go, select_positions.index, select_positions['take_profit'], 'markers', 'circle', 'green', 10, 'take profit')

if plot_closed == 1:
    # position vector:
    for index, row in select_positions.iterrows():
        plot_line(fig, go, [index, row['closed_time']], [row['entry'], row['closed']], 'lines', 3, 'red', 'position')

if plot_pre_sh_h1_1 == 1:
    plot_marker(fig, go, m15.index, m15['sh_h1_pre1'], 'markers', 'triangle-up', 'yellow', 5, 'Swing High H1 pre1')

if plot_pre_sh_h1_2 == 1:
    plot_marker(fig, go, m15.index, m15['sh_h1_pre2'], 'markers', 'triangle-up', 'red', 5, 'Swing High H1 pre2')

if plot_pre_sh_h1_3 == 1:
    plot_marker(fig, go, m15.index, m15['sh_h1_pre3'], 'markers', 'triangle-up', 'green', 5, 'Swing High H1 pre3')

# endregion

# region PLOT FRACTAL

if plot_L0 == 1:
    plot_marker(fig, go, m15.index, m15['L0_up_val'], 'markers', 'circle', 'purple', 6, name = 'L0_up')
    plot_marker(fig, go, m15.index, m15['L0_down_val'], 'markers', 'circle', 'purple', 6, name = 'L0_down')

if plot_L1 == 1:
    plot_marker(fig, go, m15.index, m15['L1_up_val'], 'markers', 'circle', 'gray', 6, 'L1_up')
    plot_marker(fig, go, m15.index, m15['L1_down_val'], 'markers', 'circle', 'gray', 6, 'L1_down')

if plot_L2 == 1:
    plot_marker(fig, go, m15.index, m15['L2_up_val'], 'markers', 'circle', 'blue', 6, 'L2_up')
    plot_marker(fig, go, m15.index, m15['L2_down_val'], 'markers', 'circle', 'blue', 6, 'L2_down')

if plot_L3 == 1:
    plot_marker(fig, go, m15.index, m15['L3_up_val'], 'markers', 'circle', 'orange', 6, 'L3_up')
    plot_marker(fig, go, m15.index, m15['L3_down_val'], 'markers', 'circle', 'oranges', 6, 'L3_down')

if plot_L0_line == 1:
    plot_line(fig, go, m15.index, m15['L0_down_valine'], 'lines', 2, 'cyan', 'L0 down line')
    plot_line(fig, go, m15.index, m15['L0_up_valine'], 'lines', 2, 'blue', 'L0 up line')

if plot_L0_pre_line == 1:
    plot_line(fig, go, m15.index, m15['L0_up_pre_1'], 'lines', 2, 'red', 'L0 up previous')
    plot_line(fig, go, m15.index, m15['L0_down_pre_1'], 'lines', 2, 'green', 'L0 down previous')    

if plot_L1_line == 1:
    plot_line(fig, go, m15.index, m15['L1_down_valine'], 'lines', 2, 'gray', 'L1 down line')
    plot_line(fig, go, m15.index, m15['L1_up_valine'], 'lines', 2, 'gray', 'L1 up line')    
    # plot_marker(fig, go, m15.index, m15['L1_down_valine'], 'markers', 'circle-dot', 'gray', 5, 'L1 down line')
    # plot_marker(fig, go, m15.index, m15['L1_up_valine'], 'markers', 'circle-dot', 'gray', 5, 'L1 up line')

if plot_L2_line == 1:
    plot_line(fig, go, m15.index, m15['L2_down_valine'], 'lines', 2, 'blue', 'L2 down line')
    plot_line(fig, go, m15.index, m15['L2_up_valine'], 'lines', 2, 'blue', 'L2 up line')
    # plot_marker(fig, go, m15.index, m15['L2_down_valine'], 'markers', 'circle-dot', 'blue', 5, 'L2 down line')
    # plot_marker(fig, go, m15.index, m15['L2_up_valine'], 'markers', 'circle-dot', 'blue', 5, 'L2 up line')

if plot_L3_line == 1:
    plot_line(fig, go, m15.index, m15['L3_down_valine'], 'lines', 2, 'orange', 'L3 down line')
    plot_line(fig, go, m15.index, m15['L3_up_valine'], 'lines', 2, 'orange', 'L3 up line')
    # plot_marker(fig, go, m15.index, m15['L3_down_valine'], 'markers', 'circle-dot', 'orange', 5, 'L3 down line')
    # plot_marker(fig, go, m15.index, m15['L3_up_valine'], 'markers', 'circle-dot', 'orange', 5, 'L3 up line')    

if plot_L0_zigzag == 1:
    plot_line(fig, go, m15.index, m15['L0_zigzag'], 'lines', 1, 'cyan', 'L0_zigzag')

if plot_L1_zigzag == 1:
    plot_line(fig, go, m15.index, m15['L1_zigzag'], 'lines', 2, 'gray', 'L1_zigzag')

if plot_L2_zigzag == 1:
    plot_line(fig, go, m15.index, m15['L2_zigzag'], 'lines', 2, 'blue', 'L2_zigzag')       

if plot_L3_zigzag == 1:
    plot_line(fig, go, m15.index, m15['L3_zigzag'], 'lines', 2, 'orange', 'L3_zigzag')       

if trace_L1 == 1:
    # upper band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['L1_big'].tolist() + m15['L1_up'].tolist()[::-1],
                'toself',
                gray,
                dict(color='rgba(0,0,0,0)'))
    # lower_band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['L1_down'].tolist() + m15['L1_small'].tolist()[::-1],
                'toself',
                gray,
                dict(color='rgba(0,0,0,0)'))

if trace_L2 == 1:
    # upper band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['L2_big'].tolist() + m15['L2_up'].tolist()[::-1],
                'toself',
                ocean,
                dict(color='rgba(0,0,0,0)'))
    # lower_band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['L2_down'].tolist() + m15['L2_small'].tolist()[::-1],
                'toself',
                ocean,
                dict(color='rgba(0,0,0,0)'))

if trace_L3 == 1:
    # upper band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['L3_big'].tolist() + m15['L3_up'].tolist()[::-1],
                'toself',
                orange,
                dict(color='rgba(0,0,0,0)'))
    # lower_band
    plot_trace( fig, go, 
                m15.index.tolist() + m15.index.tolist()[::-1],
                m15['L3_down'].tolist() + m15['L3_small'].tolist()[::-1],
                'toself',
                orange,
                dict(color='rgba(0,0,0,0)'))

# endregion

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
result = select_positions[['entry', 'stop_loss', 'take_profit', 'lot']]
if generate_result == 1:
    result.to_csv(csv_name, header=False)
    print(len(select_positions))
# endregion

# region PRINT

# print(select_positions[['R', 'R_half']])
print("sum R: ", sum(select_positions['R']))
# print("sum R_half: ", sum(select_positions['R_half']))

# print(sharpe)
# print("maxDD: ", maxDD)
# print("maxDDD: ", maxDDD)
# print("startDD: ", startDD)
if plot_cumret == 1:
    import matplotlib.pyplot as plt
    plt.plot(cumret)
    plt.show()

# print(m15.loc['2024-01-02 08:00','L0_up_pre_1_indx'])
# print(m15.loc['2024-01-02 08:00','L0_down_pre_1_indx'])

# endregion
