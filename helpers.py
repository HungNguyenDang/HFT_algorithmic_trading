import pandas as pd
from pymongo import MongoClient
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import tkinter as tk
import numpy as np
import plotly.graph_objects as go
import pyodbc

client = MongoClient('localhost', 27017)
db = client['OANDA']

def increase_date(entry):
    current_date = datetime.strptime(entry.get(), "%Y-%m-%d")
    new_date = current_date + timedelta(days=1)
    entry.delete(0, tk.END)
    entry.insert(0, new_date.strftime("%Y-%m-%d"))

def decrease_date(entry):
    current_date = datetime.strptime(entry.get(), "%Y-%m-%d")
    new_date = current_date - timedelta(days=1)
    entry.delete(0, tk.END)
    entry.insert(0, new_date.strftime("%Y-%m-%d"))

def calc_swing_highs(df, period, column):
    df[column] = False
    
    for i in range(period, len(df) - period):
        high = df['high'].iloc[i]
        if all(high >= df['high'].iloc[i - j] for j in range(1, period+1)) and all(high >= df['high'].iloc[i + j] for j in range(1, period+1)):
            df.at[df.index[i], column] = True
    return df

def calc_swing_lows(df, period, column):
    df[column] = False
    
    for i in range(period, len(df) - period):
        low = df['low'].iloc[i]
        if all(low <= df['low'].iloc[i - j] for j in range(1, period+1)) and all(low <= df['low'].iloc[i + j] for j in range(1, period+1)):
            df.at[df.index[i], column] = True
    return df

def process_swing(df, collumn, output, type):
    # assgin value to swing
    current_value = None
    df[output] = None
    for index, row in df.iterrows():
        if not df.loc[index,collumn]:
            if current_value is not None:
                df.at[index,output] = current_value
        else:
            current_value = df.loc[index,type]
            df.at[index,output] = current_value
    return df

def true_range(df):
    import numpy as np
    df['High-Low'] = df['high'] - df['low']
    df['High-Close'] = np.abs(df['high'] - df['close'].shift(1))
    df['Low-Close'] = np.abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    return df

def sma(df, length):
    return df.rolling(window=length).mean()

def ema(df, length):
    return df.ewm(span=length, adjust=False).mean()

def rma(df, length):
    alpha = 1.0 / length
    return df.ewm(alpha=alpha, adjust=False).mean()

def wma(df, length):
    weights = np.arange(1, length + 1)
    return df.rolling(window=length).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

def atr(df, length=14, smoothing='RMA'):
    df = true_range(df)
    if smoothing == 'SMA':
        df['ATR'] = sma(df['TR'], length)
    elif smoothing == 'EMA':
        df['ATR'] = ema(df['TR'], length)
    elif smoothing == 'WMA':
        df['ATR'] = wma(df['TR'], length)
    else:
        df['ATR'] = rma(df['TR'], length)
    return df

def find_previous_swing(row, list, order, value):
    swing = row[value]
    if pd.isna(swing):
        return np.nan
    current_time = row.name
    previous_times = list.index[list.index <= current_time]
    if previous_times.empty:
        return np.nan
    if len(previous_times) > order:
        count = order
        # start at the backward index of order, check if the previous swing
        # equals the current swing, stop when swings are different
        while list[previous_times[-count]] == swing and count < len(previous_times):
            count +=1
        
        if count == len(previous_times) and list[previous_times[-count]] == swing:
            return np.nan
        
        if list[previous_times[-count]] == swing:
            return np.nan
        
        return list[previous_times[-count]]
    else:
        return np.nan

def find_previous_swing_index(row, list, order, value, confirm):
    import numpy as np
    import pandas as pd
    swing = row[value]
    bool = row[confirm]
    if pd.isna(swing):
        return np.nan
    current_time = row.name
    previous_times = list.index[list.index <= current_time]
    if previous_times.empty:
        return np.nan
    if len(previous_times) > order:
        count = order
        # if the current bar has no swing, the latest swing is the previous
        if bool == False:
            return previous_times[-count]

        # start at the backward index of order, check if the previous swing
        # equals the current swing, stop when swings are different
        while list[previous_times[-count]] == swing and count < len(previous_times):
            count +=1
        if count == len(previous_times) and list[previous_times[-count]] == swing:
            return np.nan
        if list[previous_times[-count]] == swing:
            return np.nan
        return previous_times[-count]
    else:
        return np.nan

def check_positions(candles, positions, entry, stop_loss, take_profit, closed):
    positions['half'] = False
    for pos_index, position in positions.iterrows():
        candle_subset = candles.loc[pos_index:]

        for candle_index, candle in candle_subset.iterrows():
            if position['confirm_buy'] == True:
                if candle['low'] <= position[stop_loss]:
                    positions.at[pos_index, closed] = position[stop_loss]
                    positions.at[pos_index, "closed_time"] = candle_index
                    break
                elif candle['high'] >= position[take_profit]:
                    positions.at[pos_index, closed] = position[take_profit]
                    positions.at[pos_index, "closed_time"] = candle_index
                    break
                elif candle['high'] >= (position[entry]+position[take_profit])/2:
                    positions.at[pos_index, 'half'] = True
                    positions.at[pos_index, 'close_half_time'] = candle_index
                else:
                    positions.at[pos_index, closed] = candle['close']  # Position still open
            if position['confirm_sell'] == True:
                if candle['high'] >= position[stop_loss]:
                    positions.at[pos_index, closed] = position[stop_loss]
                    positions.at[pos_index, "closed_time"] = candle_index
                    break
                elif candle['low'] <= position[take_profit]:
                    positions.at[pos_index, closed] = position[take_profit]
                    positions.at[pos_index, "closed_time"] = candle_index
                    break
                elif candle['low'] <= (position[entry]+position[take_profit])/2:
                    positions.at[pos_index, 'half'] = True
                    positions.at[pos_index, 'close_half_time'] = candle_index
                else:
                    positions.at[pos_index, closed] = candle['close']  # Position still open
    return positions

def plot_line(fig, x, y, mode, width, color,name):   
    fig.add_trace(go.Scatter(x = x, y= y,
                            mode=mode,
                            line=dict(width= width, 
                                      color = color),
                                      name=name))
    
def plot_line_no_name(fig, x, y, mode, width, color):   
    fig.add_trace(go.Scatter(x = x, y= y,
                            mode=mode,
                            line=dict(width= width, 
                                      color = color),
                            showlegend=False))    

def plot_marker(fig, x, y, mode, symbol, color, size, name):
    fig.add_trace(go.Scatter(x = x, y = y,
                            mode = mode,
                            marker = dict(symbol = symbol, color = color, size = size),
                            name = name))

def plot_trace(fig, x, y,fill, fillcolor, line):
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        fill=fill,
        fillcolor=fillcolor,
        line=line,
        showlegend=False
    ))

def cal_sharpe(series):
    import numpy as np
    sharpeRatio=np.sqrt(len(series))*np.mean(series)/np.std(series)
    return sharpeRatio

def cal_drawdown(series):
    cumret=series.cumsum()
    highwatermark=np.zeros(series.shape)
    drawdown=np.zeros(series.shape)
    drawdownduration=np.zeros(series.shape)

    for t in range(1, series.shape[0]):
        highwatermark[t] = np.maximum(highwatermark[t-1], cumret.iloc[t])
        drawdown[t] = (1 + cumret.iloc[t]) / (1 + highwatermark[t]) - 1
        if drawdown[t] == 0:
            drawdownduration[t] = 0
        else:
            drawdownduration[t] = drawdownduration[t-1] + 1
    
    maxDD = np.min(drawdown)
    i = np.argmin(drawdown)  # drawdown < 0 always
    maxDDD = np.max(drawdownduration)

    return cumret, maxDD, maxDDD, i

def finding_fractal(df, L1_up, L1_down, L1_up_val, L1_down_val, L0_up_val, L0_down_val):
    last_L0_high = None
    last_L0_low = None
    last_L0_high_index = None
    lasst_L0_low_index = None

    # Mark L1 turning points
    for i in range(1, len(df)):
        if last_L0_high and last_L0_low and last_L0_low_index > last_L0_high_index and df['high'].iloc[i] > last_L0_high:
            df.at[df.index[i], L1_up] = True
            df.at[df.index[i], L1_up_val] = df['high'].iloc[i]
            last_L0_high = None  # Reset after marking L1 high

        if last_L0_low and last_L0_high and last_L0_high_index > last_L0_low_index and df['low'].iloc[i] < last_L0_low:
            df.at[df.index[i], L1_down] = True
            df.at[df.index[i], L1_down_val] = df['low'].iloc[i]
            last_L0_low = None  # Reset after marking L1 lows
        
        if df[L0_up_val].iloc[i]:
            last_L0_high = df[L0_up_val].iloc[i]
            last_L0_high_index = i
        if df[L0_down_val].iloc[i]:
            last_L0_low = df[L0_down_val].iloc[i]
            last_L0_low_index = i

    return df

def collection_from_mongodb(collection_name):
    collection = db[collection_name]
    data = collection.find({})
    pair = list(data)
    df = pd.DataFrame(pair)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df

def count_check(smt):
    return (smt.notna() & (smt > 0)).sum()

def two_check(df, smt1, smt2):
    return df[[smt1, smt2]].notna().all(axis=1).sum()

def three_check(df, smt1, smt2, smt3):
    return df[[smt1, smt2, smt3]].notna().all(axis=1).sum()

def get_data_sql(engine, table_name, chunk_size):
    # Define the query to fetch data from the table `audusd_m15`
    query = f"SELECT * FROM {table_name}"

    # Read the data in chunks
    chunk_iter = pd.read_sql_query(query, engine, chunksize=chunk_size)

    # Initialize an empty list to store each chunk
    chunks = []

    # Process each chunk
    for chunk in chunk_iter:
        # Perform any necessary data processing on the chunk here
        chunks.append(chunk)

    # Concatenate all chunks into a single DataFrame
    df = pd.concat(chunks, ignore_index=True)
    
    return df

def create_table(Server, table_name, database_folder):
    try:
        connection = pyodbc.connect(
            f"DRIVER={Server.driver};SERVER={Server.server};UID={Server.username};PWD={Server.password}"
        )
        print("Connection successful!")
    except pyodbc.Error as e:
        print(f"Error connecting to database: {e}")

    # Create a cursor object to interact with the SQL Server
    cursor = connection.cursor()

    # Check if the database exists
    cursor.execute(f"SELECT name FROM master.dbo.sysdatabases WHERE name = '{Server.db_name}'")
    database_exists = cursor.fetchone()

    if not database_exists:
        # Create the database if it doesn't exist

        # Save the current autocommit mode
        previous_autocommit = connection.autocommit
        # Enable autocommit mode
        connection.autocommit = True
        # Execute the CREATE DATABASE statement
        create_database_query = fr"""CREATE DATABASE {Server.db_name} 
        ON  ( NAME = {Server.db_name}_dat, FILENAME = '{database_folder}\{Server.db_name}.mdf') 
        LOG ON  ( NAME = {Server.db_name}_log, FILENAME = '{database_folder}\{Server.db_name}_log.ldf');"""
        cursor.execute(create_database_query)
        # Restore the previous autocommit mode
        connection.autocommit = previous_autocommit
        
        print(f"Database {Server.db_name} created successfully!")
    else:
        print(f"Database {Server.db_name} already exists.")

    # Check if the table exists and create it if it does not
    table_check_query = f"""
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
        BEGIN
            CREATE TABLE {table_name} (
                id INT IDENTITY(1,1) PRIMARY KEY,
                time datetime,
                [open] FLOAT,
                [high] FLOAT,
                [low] FLOAT,
                [close] FLOAT,
                tick_volume BIGINT,
                spread INT,
                text_id VARCHAR(255)
            )
        END
    """
        
    # Execute the table creation query
    cursor.execute(table_check_query)
    print(f"Table {table_name} checked and created if it did not exist.")

    # Commit the transaction
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

    print(f"Database '{Server.db_name}' and table '{table_name}' are connected.")

