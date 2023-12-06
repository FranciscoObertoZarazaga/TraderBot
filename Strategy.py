def squeeze_strategy(df, n=-1):
    sm = df['sm']
    is_min = sm[n-1] > sm[n - 2] and sm[n - 3] > sm[n - 2] and sm[n-2] < 0
    is_max = sm[n-1] < sm[n - 2] and sm[n - 3] < sm[n - 2] and sm[n-2] > 0
    if is_min:
        return 1
    if is_max:
        return -1
    return 0
