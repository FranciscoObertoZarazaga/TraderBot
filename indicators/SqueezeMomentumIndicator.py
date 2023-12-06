import numpy as np


def squeeze_momentum_indicator(df, length=20, length_kc=20):
    df = df.copy()
    # calculate momentum value
    highest = df['High'].rolling(window=length_kc).max()
    lowest = df['Low'].rolling(window=length_kc).min()
    m_avg = df['Close'].rolling(window=length).mean()
    m1 = (highest + lowest) / 2
    df['value'] = (df['Close'] - (m1 + m_avg)/2)
    fit_y = np.array(range(0, length_kc))
    df['value'] = df['value'].rolling(window=length_kc).apply(lambda x: np.polyfit(fit_y, x, 1)[0] * (length_kc - 1) + np.polyfit(fit_y, x, 1)[1], raw=True)
    return df['value']
