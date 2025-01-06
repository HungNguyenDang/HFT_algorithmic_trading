# region IMPORT LIBRARIES
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import datetime
import copy
import math

import pyodbc
import pymysql
from sqlalchemy import create_engine
import MetaTrader5 as mt5

from dotenv import load_dotenv, dotenv_values
import os
load_dotenv()

from helpers import *
from fractal_01 import *
# endregion

# region CLASS
class Create_Server:
    def __init__(self, driver, server, username, password, db_name):
        self.driver = driver
        self.server = server
        self.username = username
        self.password = password
        self.db_name =db_name
# endregion       

# region VARIABLES
# 1$ = 0.1 lot x 1 pips
# lot = 0.1* money / pips
# Ex: 0.1* 100$ / 10 = 1 lot
fund = 10000
percent = 0.01
stop_margin = 1.5
prefix = "jp225"  # change when using manually and automatically

# Plot cummulative returns in %
plot_cumret = 0
# Plot close_half cummulative returns in %
plot_half_cumret = 0
# Plot to html file
plot_all = 0
# Plot cummulative pnl return
plot_pnl_cumret = 0

# save all positions to a csv file
generate_result = 1
# calculate positions entry, SL, TP
find_position = 1

# ----------------------------------------------------------------- #
# train from 2012 to 2020
# test from 2020 to 2024

format_day = '%Y-%m-%d %H:%M'
format_hour = '%Y-%m-%d %H:%M'

cal_year = 2016
for cal_year in range(2021,2025):

    # days imported from MongoDb
    from_day = f'{cal_year-1}-12-20'
    to_day = f'{cal_year+1}-01-05'

    # days for calculating
    from_day_cal = f'{cal_year}-01-01'
    to_day_cal = f'{cal_year}-12-31'

    from_month = datetime.datetime.strptime(from_day_cal, '%Y-%m-%d').month
    from_year = datetime.datetime.strptime(from_day_cal, '%Y-%m-%d').year
    to_month = datetime.datetime.strptime(to_day_cal, '%Y-%m-%d').month
    to_year = datetime.datetime.strptime(to_day_cal, '%Y-%m-%d').year
    csv_name = f"result/{prefix}_from_{from_month}-{from_year}_to_{to_month}-{to_year}.csv"

    sql_import = 1
    mongodb_import = 0
    # endregion

    # region IMPORT DATA from MICROSOFT SQL
    server = 'HUNG-LAPTOP' 
    username = 'trading'  
    password = 'Dulieulon123'
    driver = '{ODBC Driver 17 for SQL Server}'
    driver_alchemy = 'ODBC+Driver+17+for+SQL+Server'
    database_folder = 'D:\\trading-with-python\\SQL_Database' 
    link = "C:\\Program Files\\OANDA MetaTrader 5\\terminal64.exe"

    # CHANGE THESE VARIABLES
    db_name = prefix
    table_name = f"{prefix}_m15" # change when using manually
    pair_name = "JP225"  # change when using manually
    timeframe = mt5.TIMEFRAME_M15  # change when using manually
    chunk_size = 20000 # size of each time to insert data to sql

    Server = Create_Server(driver, server, username, password, db_name)

    # Create the SQLAlchemy engine
    engine = create_engine(f"mssql+pyodbc://{Server.username}:{Server.password}@{Server.server}/{Server.db_name}?driver={driver_alchemy}")

    if sql_import == 1:
        m15 = get_data_sql(engine, table_name, chunk_size)
        print("Initial table size: ", len(m15))
        m15 = m15[(m15['text_id'] >= from_day_cal) & (m15['text_id'] <= to_day_cal)]
        print("Table size after trim: ", len(m15))
        m15['time'] = pd.to_datetime(m15['time'], format = format_hour)
        m15.set_index('time', inplace=True)
    h1 = m15.resample('1h').asfreq() # Resample to 1 hour frequency
    h4 = m15.resample('4h').asfreq() # Resample to 4 hour frequency 
    day = m15.resample('1d').asfreq() # Resample to 1 day frequency
    # endregion

    # region IMPORT DATA from MONGODB
    if mongodb_import == 1:
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
    # endregion

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

        m15['take_profit'] = np.where(
            m15['confirm_buy']==True,
            m15['atr_up'],
            np.where(
                m15['confirm_sell']==True,
                m15['atr_down'],
                None
            )
        )

        positions = m15.dropna(subset=['entry', 'stop_loss', 'take_profit'])
        positions = positions[['entry', 'stop_loss', 'take_profit', 'confirm_buy', 'confirm_sell',]]
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
            0.5*((positions['entry']+positions['take_profit'])/2-positions['entry'])+ \
                np.maximum(0, 0.5*(positions['closed'] - positions['entry'])), 
            np.where(
                (positions['half'] & positions['confirm_sell']), 
                0.5*(positions['entry']-(positions['entry']+positions['take_profit'])/2)+ \
                    np.maximum(0, 0.5*(positions['entry'] - positions['closed'])), 
                positions['pnl']
            )
        )

        # Close half position when price goes half way to take profit, move stop loss to break even for another half
        positions['R_half'] = positions.apply(lambda row: row['pnl_half']/row['sl_pip']
                                            if row['half']
                                            else row['R'], axis=1)
        positions['lot'] = 0.1*fund*percent/(positions['sl_pip']*10000)*10000000 # multiply to 10000 for indice (US500: 100000) (JP225: 10000000)
        positions['pnl_cumret'] = positions['pnl']*positions['lot']*100000/10000000 # divide back to 10000 for indice (US500: 100000) (JP225: 10000000)
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

        half_cumret, half_maxDD, half_maxDDD, half_startDD = cal_drawdown(select_positions['R_half'])
        half_sharpe = cal_sharpe(select_positions['R_half'])
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
        select_positions['entry'] = round(select_positions['entry'], 5)
        select_positions['stop_loss'] = round(select_positions['stop_loss'], 5)
        select_positions['take_profit'] = round(select_positions['take_profit'], 5)
        select_positions['lot'] = round(select_positions['lot'], 2)
        select_positions['pnl_cumret'] = round(select_positions['pnl_cumret'], 2)
        result = select_positions[['entry', 'stop_loss', 'take_profit', 'lot', 'pnl_cumret']]
        result.to_csv(csv_name, header=False)
        print(len(select_positions))
    # endregion

    # region PRINT
    # print(select_positions[['R', 'R_half']])
    print("all of position: ", positions.shape)
    print("selected positions: ", select_positions.shape)
    print("sum R: ", sum(select_positions['R']))
    print("sum R_half: ", sum(select_positions['R_half']))
    print("number of close half positions: ", select_positions['half'].sum())
    print("half's sharpe: ", half_sharpe)

    half_and_tp = len(select_positions[(select_positions['half'] == True) & (select_positions['closed'] == select_positions['take_profit'])])
    half_and_sl = len(select_positions[(select_positions['half'] == True) & (select_positions['closed'] == select_positions['stop_loss'])])
    pure_sl = len(select_positions[(select_positions['half'] == False) & (select_positions['closed'] == select_positions['stop_loss'])])
    pure_tp = len(select_positions[(select_positions['half'] == False) & (select_positions['closed'] == select_positions['take_profit'])])
    print('pure sl: ', pure_sl)
    print('pure tp: ', pure_tp)
    print('half and sl: ', half_and_sl)
    print('half and tp: ', half_and_tp)
    # print("maxDD: ", maxDD)

    if plot_cumret == 1:
        import matplotlib.pyplot as plt
        plt.plot(cumret)
        plt.show()

    if plot_half_cumret == 1:
        import matplotlib.pyplot as plt
        plt.plot(half_cumret)
        plt.show()

    if plot_pnl_cumret == 1:
        import matplotlib.pyplot as plt
        pnl_cumret = select_positions['pnl_cumret'].cumsum()
        plt.plot(pnl_cumret)
        plt.show()
    # endregion

