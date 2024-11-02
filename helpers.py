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
        high = df['High'].iloc[i]
        if all(high >= df['High'].iloc[i - j] for j in range(1, period+1)) and all(high >= df['High'].iloc[i + j] for j in range(1, period+1)):
            df.at[df.index[i], column] = True
    return df

def calc_swing_lows(df, period, column):
    df[column] = False
    
    for i in range(period, len(df) - period):
        low = df['Low'].iloc[i]
        if all(low <= df['Low'].iloc[i - j] for j in range(1, period+1)) and all(low <= df['Low'].iloc[i + j] for j in range(1, period+1)):
            df.at[df.index[i], column] = True
    return df

def process_swing(df, collumn, output, type):
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
    df['High-Low'] = df['High'] - df['Low']
    df['High-Close'] = np.abs(df['High'] - df['Close'].shift(1))
    df['Low-Close'] = np.abs(df['Low'] - df['Close'].shift(1))
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

def find_previous_swing(row, list, order):
    import numpy as np
    import pandas as pd

    sh_h1 = row['sh_h1']
    if pd.isna(sh_h1):
        return np.nan
    current_time = row.name
    previous_times = list.index[list.index <= current_time]
    if previous_times.empty:
        return np.nan
    if len(previous_times) > order:
        count = order
        # start at the backward index of order, check if the previous swing
        # equals the current swing, stop when swings are different
        while list[previous_times[-count]] == sh_h1 and count < len(previous_times):
            count +=1
        
        if count == len(previous_times) and list[previous_times[-count]] == sh_h1:
            return np.nan
        
        if list[previous_times[-count]] == sh_h1:
            return np.nan
        
        return list[previous_times[-count]]
        # if list[previous_times[-1]] == sh_h1:
        #     if len(previous_times) - 1 >= order:
        #         return list[previous_times[-order-1]]
        #     else:
        #         return np.nan            
        # else:
        #     return list[[previous_times[-order-1]]]
    else:
        return np.nan

def check_positions(candles, positions, entry, stop_loss, take_profit, closed):
    positions['close_half'] = 0.0
    positions['half'] = False
    for pos_index, position in positions.iterrows():
        candle_subset = candles.loc[pos_index:]
        
        for candle_index, candle in candle_subset.iterrows():
            if candle['High'] >= position[stop_loss]:
                positions.at[pos_index, closed] = position[stop_loss]
                break
            elif candle['Low'] <= position[take_profit]:
                positions.at[pos_index, closed] = position[take_profit]
                break
            elif candle['Low'] <= (position[entry]+position[take_profit])/2:
                positions.at[pos_index, 'half'] = True
                positions.at[pos_index, 'close_half'] = (position[entry] + position[take_profit])/2
            else:
                positions.at[pos_index, closed] = candle['Close']  # Position still open
            positions.at[pos_index, "closed_time"] = candle_index
    return positions

def plot_line(fig, go, x, y, mode, width, color, name):   
    fig.add_trace(go.Scatter(x = x, y= y,
                            mode=mode,
                            line=dict(width= width, color = color),
                            name=name))
    
def plot_marker(fig, go, x, y, mode, symbol, color, size, name):
    fig.add_trace(go.Scatter(x = x, y = y,
                            mode = mode,
                            marker = dict(symbol = symbol, color = color, size = size),
                            name = name))

def plot_trace(fig,go, x, y,fill, fillcolor, line):
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

def cal_drawdown(np, series):
    cumret=series.cumsum()
    highwatermark=np.zeros(series.shape)
    drawdown=np.zeros(series.shape)
    drawdownduration=np.zeros(series.shape)

    for t in range(1, series.shape[0]):
        highwatermark[t] = np.maximum(highwatermark[t-1], cumret[t])
        drawdown[t] = (1 + cumret[t]) / (1 + highwatermark[t]) - 1
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
        if last_L0_high and last_L0_low and last_L0_low_index > last_L0_high_index and df['High'].iloc[i] > last_L0_high:
            df.at[df.index[i], L1_up] = True
            df.at[df.index[i], L1_up_val] = df['High'].iloc[i]
            last_L0_high = None  # Reset after marking L1 high

        if last_L0_low and last_L0_high and last_L0_high_index > last_L0_low_index and df['Low'].iloc[i] < last_L0_low:
            df.at[df.index[i], L1_down] = True
            df.at[df.index[i], L1_down_val] = df['Low'].iloc[i]
            last_L0_low = None  # Reset after marking L1 lows
        
        if df[L0_up_val].iloc[i]:
            last_L0_high = df[L0_up_val].iloc[i]
            last_L0_high_index = i
        if df[L0_down_val].iloc[i]:
            last_L0_low = df[L0_down_val].iloc[i]
            last_L0_low_index = i

    return df
