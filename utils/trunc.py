def trunc(n, precision):
    n = str(n)
    if '.' not in n:
        return int(n)
    entero, decimal = n.split('.')
    decimal = decimal[0:precision] if len(decimal) > precision else decimal
    n = float(entero + '.' + decimal) if decimal != '' else float(entero)
    return n
