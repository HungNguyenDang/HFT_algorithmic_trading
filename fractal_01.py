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
# endregion

# region VARIABLES FRACTALS
plot_L0 = 0
plot_L1 = 0
plot_L2 = 1
plot_L3 = 0
plot_L0_line = 0
plot_L0_pre_line = 0

plot_L1_line = 0
plot_L1_pre_line = 0

plot_L2_line = 0
plot_L2_pre_line = 0

plot_L3_line = 0
plot_L3_pre_line = 0

plot_L0_zigzag = 0
plot_L1_zigzag = 0
plot_L2_zigzag = 0
plot_L3_zigzag = 0

trace_L1 = 0
trace_L2 = 1
trace_L3 = 0

upper_band_L3 = 0.75
lower_band_L3 = 0.25

upper_band_L2 = 0.75
lower_band_L2 = 0.25

upper_band_L1 = 0.75
lower_band_L1 = 0.25
# endregion

# region VARIABLES PLOT
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

trace_sell_cond = 0

plot_pre_sh_h1_1 = 0
plot_pre_sh_h1_2 = 0
plot_pre_sh_h1_3 = 0

plot_entry = 1
plot_stop_loss = 1
plot_take_profit = 1
plot_closed = 1
plot_half_closed = 1

violet = 'rgba(255, 87 , 51, 0.2)'
gray = 'rgba(213, 216, 220, 0.2)'
green = 'rgba(0, 255, 0, 0.2)'
red = 'rgba(255, 0, 0, 0.2)'
blue = 'rgba(0, 0, 255, 0.2)'
yellow = 'rgba(255, 255, 0, 0.2)'
pink = 'rgba(255, 0, 255, 0.25)'
orange = 'rgba(255, 137, 101, 0.25)'
ocean = 'rgba(41, 181, 246, 0.25)'
# endregion

def find_swing_point(df, h1, h4, day):
    # Process everything in 1 dataframe
    # anything else, package it to 

    class create_swing:
        def __init__(self, swh_m15, swl_m15, offset_m15,
                     swh_h1, swl_h1, offset_h1,
                     swh_h4, swl_h4, offset_h4,
                     swh_day, swl_day, offset_day,
                     swh_m15_2, swl_m15_2):
            self.swh_m15 = swh_m15
            self.swl_m15 = swl_m15
            self.offset_m15 = offset_m15
            self.swh_h1 = swh_h1
            self.swl_h1 = swl_h1
            self.offset_h1 = offset_h1
            self.swh_h4 = swh_h4
            self.swl_h4 = swl_h4
            self.offset_h4 = offset_h4
            self.swh_day = swh_day
            self.swl_day = swl_day
            self.offset_day = offset_day
            self.swh_m15_2 = swh_m15_2
            self.swl_m15_2 = swl_m15_2

    # region FIND SWING POINT
    m15 = calc_swing_highs(df.copy(),frtl_m15, 'SwingHigh')
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

    # region CALCULATE SWING
    day = process_swing(day,"SwingHigh","sh_day", "high")
    day = process_swing(day,"SwingLow","sl_day", "low")
    day['sh_day'] = day['sh_day'].shift(frtl_day+1)
    day['sl_day'] = day['sl_day'].shift(frtl_day+1)

    h4 = process_swing(h4,"SwingHigh","sh_h4", "high")
    h4 = process_swing(h4,"SwingLow","sl_h4", "low")
    h4['sh_h4'] = h4['sh_h4'].shift(frtl_h4+1)
    h4['sl_h4'] = h4['sl_h4'].shift(frtl_h4+1)

    h1 = process_swing(h1,"SwingHigh","sh_h1", "high")
    h1 = process_swing(h1,"SwingLow","sl_h1", "low")
    h1['sh_h1'] = h1['sh_h1'].shift(frtl_h1+1)
    h1['sl_h1'] = h1['sl_h1'].shift(frtl_h1+1)

    m15 = process_swing(m15,"SwingHigh","sh_m15", "high")
    m15 = process_swing(m15,"SwingLow","sl_m15", "low")
    m15['sh_m15'] = m15['sh_m15'].shift(frtl_m15+1)
    m15['sl_m15'] = m15['sl_m15'].shift(frtl_m15+1)

    # Additional fractal for entry
    m15 = process_swing(m15,"frtl_2_high","sh_m15_2", "high")
    m15 = process_swing(m15,"frtl_2_low","sl_m15_2", "low")
    m15['sh_m15_2'] = m15['sh_m15_2'].shift(frtl_2 + 1)
    m15['sl_m15_2'] = m15['sl_m15_2'].shift(frtl_2 + 1)
    # endregion

    # region CALCULATE OFFSET
    swh_m15 = m15[m15['SwingHigh']]
    swl_m15 = m15[m15['SwingLow']]
    offset_m15 = 0.02 * (swh_m15['high'].max() - swh_m15['low'].min())

    swh_line_h1 = h1[h1['sh_h1'].notna()]
    swl_line_h1 = h1[h1['sl_h1'].notna()]
    swh_h1 = h1[h1['SwingHigh']]
    swl_h1 = h1[h1['SwingLow']]
    offset_h1 = 0.02 * (swh_h1['high'].max() - swh_h1['low'].min())

    swh_line_h4 = h4[h4['sh_h4'].notna()]
    swl_line_h4 = h4[h4['sl_h4'].notna()]
    swh_h4 = h4[h4['SwingHigh']]
    swl_h4 = h4[h4['SwingLow']]
    offset_h4 = 0.02 * (swh_h4['high'].max() - swh_h4['low'].min())

    swh_line_day = day[day['sh_day'].notna()]
    swl_line_day = day[day['sl_day'].notna()]
    swh_day = day[day['SwingHigh']]
    swl_day = day[day['SwingLow']]
    offset_day = 0.02 * (swh_day['high'].max() - swh_day['low'].min())

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
    swh_h1_list = copy.deepcopy(swh_h1['high'])
    swh_h1_list.index = swh_h1_list.index.shift(frtl_h1+1, freq='h')

    swl_h1_list = copy.deepcopy(swl_h1['low'])
    swl_h1_list.index = swl_h1_list.index.shift(frtl_h1+1, freq='h')

    m15['sh_h1_pre1'] = m15.apply(find_previous_swing, list = swh_h1_list.copy(), order = 1, value = 'sh_h1', axis=1)
    m15['sh_h1_pre2'] = m15.apply(find_previous_swing, list = swh_h1_list.copy(), order = 2, value = 'sh_h1', axis=1)
    m15['sh_h1_pre3'] = m15.apply(find_previous_swing, list = swh_h1_list.copy(), order = 3, value = 'sh_h1', axis=1)

    m15['sl_h1_pre1'] = m15.apply(find_previous_swing, list = swl_h1_list.copy(), order = 1, value = 'sl_h1', axis=1)
    m15['sl_h1_pre2'] = m15.apply(find_previous_swing, list = swl_h1_list.copy(), order = 2, value = 'sl_h1', axis=1)
    m15['sl_h1_pre3'] = m15.apply(find_previous_swing, list = swl_h1_list.copy(), order = 3, value = 'sl_h1', axis=1)
    # endregion

    # region CREATE L0
    m15['down_bar'] = m15['close'] <= m15['close'].shift(1)
    m15['up_bar'] = m15['close'] > m15['close'].shift(1)
    m15['L0_down'] = (m15['down_bar'].shift(1) & m15['up_bar']).fillna(False)
    m15['L0_up'] = (m15['up_bar'].shift(1) & m15['down_bar']).fillna(False)
    m15['High_shifted'] = m15['high'].shift(1)
    m15['Low_shifted'] = m15['low'].shift(1)
    m15['L0_up_val'] = m15.apply(lambda row: max(row['high'], row['High_shifted']) if row['L0_up'] else None, axis=1)
    m15['L0_down_val'] = m15.apply(lambda row: min(row['low'], row['Low_shifted']) if row['L0_down'] else None, axis=1)
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
    h1['down_bar'] = h1['close'] <= h1['close'].shift(1)
    h1['up_bar'] = h1['close'] > h1['close'].shift(1)
    h1['L1_down'] = (h1['down_bar'].shift(1) & h1['up_bar']).fillna(False)
    h1['L1_up'] = (h1['up_bar'].shift(1) & h1['down_bar']).fillna(False)
    h1['High_shifted'] = h1['high'].shift(1)
    h1['Low_shifted'] = h1['low'].shift(1)
    h1['L1_up_val'] = h1.apply(lambda row: max(row['high'], row['High_shifted']) if row['L1_up'] else None, axis=1)
    h1['L1_down_val'] = h1.apply(lambda row: min(row['low'], row['Low_shifted']) if row['L1_down'] else None, axis=1)
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
    h4['down_bar'] = h4['close'] <= h4['close'].shift(1)
    h4['up_bar'] = h4['close'] > h4['close'].shift(1)
    h4['L2_down'] = (h4['down_bar'].shift(1) & h4['up_bar']).fillna(False)
    h4['L2_up'] = (h4['up_bar'].shift(1) & h4['down_bar']).fillna(False)
    h4['High_shifted'] = h4['high'].shift(1)
    h4['Low_shifted'] = h4['low'].shift(1)
    h4['L2_up_val'] = h4.apply(lambda row: max(row['high'], row['High_shifted']) if row['L2_up'] else None, axis=1)
    h4['L2_down_val'] = h4.apply(lambda row: min(row['low'], row['Low_shifted']) if row['L2_down'] else None, axis=1)
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
    day['down_bar'] = day['close'] <= day['close'].shift(1)
    day['up_bar'] = day['close'] > day['close'].shift(1)
    day['L3_down'] = (day['down_bar'].shift(1) & day['up_bar']).fillna(False)
    day['L3_up'] = (day['up_bar'].shift(1) & day['down_bar']).fillna(False)
    day['High_shifted'] = day['high'].shift(1)
    day['Low_shifted'] = day['low'].shift(1)
    day['L3_up_val'] = day.apply(lambda row: max(row['high'], row['High_shifted']) if row['L3_up'] else None, axis=1)
    day['L3_down_val'] = day.apply(lambda row: min(row['low'], row['Low_shifted']) if row['L3_down'] else None, axis=1)
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

    swing = create_swing(swh_m15, swl_m15, offset_m15,
                        swh_h1, swl_h1, offset_h1,
                        swh_h4, swl_h4, offset_h4,
                        swh_day, swl_day, offset_day,
                        swh_m15_2, swl_m15_2)
    return m15, swing

def figure_fractal(m15,swing, select_positions):
    # region PLOT FLAG
    fig = go.Figure(data=[go.Candlestick(x = m15.index,
                                        open = m15['open'],
                                        high = m15['high'],
                                        low = m15['low'],
                                        close = m15['close'],
                                        increasing_line_color='white',  
                                        decreasing_line_color='white',
                                        increasing_fillcolor='white',
                                        decreasing_fillcolor='black')])

    if frtl_flag_m15 == 1:
        # Fractal high m15
        plot_marker(fig, swing.swh_m15.index, swing.swh_m15['high'] + swing.offset_m15, 'markers', 'triangle-up', 'red', 5, 'Fractal Highs m15')
        # Fractal low m15
        plot_marker(fig, swing.swl_m15.index, swing.swl_m15['low'] - swing.offset_m15, 'markers', 'triangle-down', 'green', 5, 'Fractal Lows m15')

    if frtl_flag_h1 == 1:
        # Fractal high h1
        plot_marker(fig, swing.swh_h1.index, swing.swh_h1['high'] + swing.offset_h1, 'markers', 'triangle-up', 'cyan', 5, 'Swing Highs h1')
        # Fractal low h1
        plot_marker(fig, swing.swl_h1.index, swing.swl_h1['low'] - swing.offset_h1, 'markers', 'triangle-down', 'cyan', 5, 'Swing Lows h1')

    if frtl_flag_h4 == 1:
        # Fractal high h4
        plot_marker(fig, swing.swh_h4.index, swing.swh_h4['high'], 'markers', 'triangle-up', 'cyan', 5, 'Swing Highs H4')
        # Fractal low h4
        plot_marker(fig, swing.swl_h4.index, swing.swl_h4['low'], 'markers', 'triangle-down', 'purple', 5, 'Swing Low H4')

    if frtl_flag_day == 1:    
        # Fractal high day
        plot_marker(fig, swing.swh_day.index, swing.swh_day['high'], 'markers', 'triangle-up', 'yellow', 5, 'Swing Highs day')
        # Fractal low h4
        plot_marker(fig, swing.swl_day.index, swing.swh_day['low'], 'markers', 'triangle-down', 'yellow', 5, 'Swing Low day')

    if frtl_flag_m15_2 == 1:
        # Fractal high m15 period 2
        plot_marker(fig, swing.swh_m15_2.index, swing.swh_m15_2['high'] + swing.offset_m15, 'markers', 'triangle-up', 'red', 5, 'Fractal Highs m15')
        # Fractal low m15 period 2
        plot_marker(fig, swing.swl_m15_2.index, swing.swl_m15_2['low'] - swing.offset_m15, 'markers', 'triangle-down', 'green', 5, 'Fractal Lows m15')
    # endregion

    # region PLOT SWING, TRACE, PRE-SWING
    if swing_m15 == 1:
        # Swing high m15
        plot_marker(fig, m15.index, m15['sh_m15'], 'markers', 'circle', 'red', 2, 'Swing High m15')
        # Swing low m15
        plot_marker(fig, m15.index, m15['sl_m15'], 'markers', 'circle', 'green', 2, 'Swing Low m15')

    if swing_h1 == 1:
        # Swing high h1
        plot_marker(fig, m15.index, m15['sh_h1'], 'markers', 'triangle-up', 'cyan', 5, 'Swing High H1')
        # Swing low h1
        plot_marker(fig, m15.index, m15['sl_h1'], 'markers', 'triangle-down', 'purple', 5, 'Swing Low H1')

    if swing_h4 == 1:
        # Swing high h4
        plot_marker(fig, m15.index, m15['sh_h4'], 'markers', 'triangle-up', 'yellow', 5, 'Swing High H4')
        # Swing low h4
        plot_marker(fig, m15.index, m15['sl_h4'], 'markers', 'triangle-down', 'orange', 5, 'Swing Low H4')

    if trace_m15 == 1:
        # upper band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['m15_big'].tolist() + m15['m15_up'].tolist()[::-1],
                    'toself',
                    'rgba(220,100,80,0.2)',
                    dict(color='rgba(0,0,0,0)'))
        # lower_band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['m15_down'].tolist() + m15['m15_small'].tolist()[::-1],
                    'toself',
                    'rgba(0,255,0,0.2)',
                    dict(color='rgba(0,0,0,0)'))

    if trace_h1 == 1:
        # upper band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['h1_big'].tolist() + m15['h1_up'].tolist()[::-1],
                    'toself',
                    'rgba(0,255,255,0.2)',
                    dict(color='rgba(0,0,0,0)'))
        # lower_band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['h1_down'].tolist() + m15['h1_small'].tolist()[::-1],
                    'toself',
                    'rgba(0,255,0,0.2)',
                    dict(color='rgba(0,0,0,0)'))

# endregion

    # region PLOT ATR,ENTRY, SL, TP, CLOSED TIME
    if trace_atr == 1:
        # ATR up
        plot_line(fig, m15.index, m15['atr_up'], 'lines', 1, 'rgba(0,255,0,0.3)', 'atr up')
        # ATR down
        plot_line(fig, m15.index, m15['atr_down'], 'lines', 1, 'rgba(0,255,0,0.3)', 'atr down')

    if trace_sell_cond == 1:
        # sell condition
        plot_marker(fig, m15.index, m15['show_sell_cond'], 'markers', 'circle', 'rgba(0, 255, 0, 1)', 10, 'show sell condition')

    if plot_entry == 1:
        # sell condition
        plot_marker(fig, select_positions.index, select_positions['entry'], 'markers', 'circle', 'green', 10, 'entry')

    if plot_stop_loss == 1:
        # sell condition
        plot_marker(fig, select_positions.index, select_positions['stop_loss'], 'markers', 'circle', 'red', 10, 'stop loss')

    if plot_take_profit == 1:
        # sell condition
        plot_marker(fig, select_positions.index, select_positions['take_profit'], 'markers', 'circle', 'yellow', 10, 'take profit')

    if plot_closed == 1:
        # position vector:
        for index, row in select_positions.iterrows():
            plot_line_no_name(fig, [index, row['closed_time']], [row['entry'], row['closed']], 'lines', 3, 'violet')

    if plot_half_closed == 1:
        # position vector:
        for index, row in select_positions.iterrows():
            if row['half'] == True:
                plot_line_no_name(fig, [index, row['close_half_time']], [row['entry'], (row['entry']+row['take_profit'])/2], 'lines', 3, 'orange')
                plot_line_no_name(fig, [row['close_half_time'], row['closed_time']], [(row['entry']+row['take_profit'])/2, row['closed']], 'lines', 3, 'red')

# endregion

    # region PLOT PREVIOUS SWING
    if plot_pre_sh_h1_1 == 1:
        plot_marker(fig, m15.index, m15['sh_h1_pre1'], 'markers', 'triangle-up', 'yellow', 5, 'Swing High H1 pre1')

    if plot_pre_sh_h1_2 == 1:
        plot_marker(fig, m15.index, m15['sh_h1_pre2'], 'markers', 'triangle-up', 'red', 5, 'Swing High H1 pre2')

    if plot_pre_sh_h1_3 == 1:
        plot_marker(fig, m15.index, m15['sh_h1_pre3'], 'markers', 'triangle-up', 'green', 5, 'Swing High H1 pre3')
    # endregion

    # region PLOT FRACTAL
    if plot_L0 == 1:
        plot_marker(fig, m15.index, m15['L0_up_val'], 'markers', 'circle', 'purple', 6, name = 'L0_up')
        plot_marker(fig, m15.index, m15['L0_down_val'], 'markers', 'circle', 'purple', 6, name = 'L0_down')

    if plot_L1 == 1:
        plot_marker(fig, m15.index, m15['L1_up_val'], 'markers', 'circle', 'purple', 6, 'L1_up')
        plot_marker(fig, m15.index, m15['L1_down_val'], 'markers', 'circle', 'gray', 6, 'L1_down')

    if plot_L2 == 1:
        plot_marker(fig, m15.index, m15['L2_up_val'], 'markers', 'circle', 'blue', 6, 'L2_up')
        plot_marker(fig, m15.index, m15['L2_down_val'], 'markers', 'circle', 'blue', 6, 'L2_down')

    if plot_L3 == 1:
        plot_marker(fig, m15.index, m15['L3_up_val'], 'markers', 'circle', 'orange', 6, 'L3_up')
        plot_marker(fig, m15.index, m15['L3_down_val'], 'markers', 'circle', 'oranges', 6, 'L3_down')

    if plot_L0_line == 1:
        plot_line(fig, m15.index, m15['L0_down_valine'], 'lines', 2, 'cyan', 'L0 down line')
        plot_line(fig, m15.index, m15['L0_up_valine'], 'lines', 2, 'blue', 'L0 up line')

    if plot_L0_pre_line == 1:
        plot_line(fig, m15.index, m15['L0_up_pre_1'], 'lines', 2, 'red', 'L0 up previous')
        plot_line(fig, m15.index, m15['L0_down_pre_1'], 'lines', 2, 'green', 'L0 down previous')    

    if plot_L1_line == 1:
        plot_line(fig, m15.index, m15['L1_down_valine'], 'lines', 2, 'gray', 'L1 down line')
        plot_line(fig, m15.index, m15['L1_up_valine'], 'lines', 2, 'gray', 'L1 up line')    
        # plot_marker(fig, m15.index, m15['L1_down_valine'], 'markers', 'circle-dot', 'gray', 5, 'L1 down line')
        # plot_marker(fig, m15.index, m15['L1_up_valine'], 'markers', 'circle-dot', 'gray', 5, 'L1 up line')

    if plot_L2_line == 1:
        plot_line(fig, m15.index, m15['L2_down_valine'], 'lines', 2, 'blue', 'L2 down line')
        plot_line(fig, m15.index, m15['L2_up_valine'], 'lines', 2, 'blue', 'L2 up line')
        # plot_marker(fig, m15.index, m15['L2_down_valine'], 'markers', 'circle-dot', 'blue', 5, 'L2 down line')
        # plot_marker(fig, m15.index, m15['L2_up_valine'], 'markers', 'circle-dot', 'blue', 5, 'L2 up line')

    if plot_L3_line == 1:
        plot_line(fig, m15.index, m15['L3_down_valine'], 'lines', 2, 'orange', 'L3 down line')
        plot_line(fig, m15.index, m15['L3_up_valine'], 'lines', 2, 'orange', 'L3 up line')
        # plot_marker(fig, m15.index, m15['L3_down_valine'], 'markers', 'circle-dot', 'orange', 5, 'L3 down line')
        # plot_marker(fig, m15.index, m15['L3_up_valine'], 'markers', 'circle-dot', 'orange', 5, 'L3 up line')    

    if plot_L0_zigzag == 1:
        plot_line(fig, m15.index, m15['L0_zigzag'], 'lines', 1, 'cyan', 'L0_zigzag')

    if plot_L1_zigzag == 1:
        plot_line(fig, m15.index, m15['L1_zigzag'], 'lines', 2, 'gray', 'L1_zigzag')

    if plot_L2_zigzag == 1:
        plot_line(fig, m15.index, m15['L2_zigzag'], 'lines', 2, 'blue', 'L2_zigzag')       

    if plot_L3_zigzag == 1:
        plot_line(fig, m15.index, m15['L3_zigzag'], 'lines', 2, 'orange', 'L3_zigzag')       

    if trace_L1 == 1:
        # upper band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['L1_big'].tolist() + m15['L1_up'].tolist()[::-1],
                    'toself',
                    gray,
                    dict(color='rgba(0,0,0,0)'))
        # lower_band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['L1_down'].tolist() + m15['L1_small'].tolist()[::-1],
                    'toself',
                    gray,
                    dict(color='rgba(0,0,0,0)'))

    if trace_L2 == 1:
        # upper band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['L2_big'].tolist() + m15['L2_up'].tolist()[::-1],
                    'toself',
                    ocean,
                    dict(color='rgba(0,0,0,0)'))
        # lower_band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['L2_down'].tolist() + m15['L2_small'].tolist()[::-1],
                    'toself',
                    ocean,
                    dict(color='rgba(0,0,0,0)'))

    if trace_L3 == 1:
        # upper band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['L3_big'].tolist() + m15['L3_up'].tolist()[::-1],
                    'toself',
                    orange,
                    dict(color='rgba(0,0,0,0)'))
        # lower_band
        plot_trace( fig, 
                    m15.index.tolist() + m15.index.tolist()[::-1],
                    m15['L3_down'].tolist() + m15['L3_small'].tolist()[::-1],
                    'toself',
                    orange,
                    dict(color='rgba(0,0,0,0)'))
    # endregion

    return fig

