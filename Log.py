import pandas as pd


class Log:

    def __init__(self):
        self.src = 'arbitrator.csv'
        self.df = pd.DataFrame()
        self.load()

    def load(self):
        try:
            df = pd.read_csv(self.src, index_col=0)
            self.df = df
        except:
            pass

    def save(self):
        self.df.to_csv(self.src)

    def add(self, pair, amount, buyPrice, buyQty, finalAmount, sellPrice, sellQty, network, fee, exchange1, exchange2, resultado):
        data = {
            'pair': pair,
            'amount': amount,
            'buyPrice': buyPrice,
            'buyQty': buyQty,
            'finalAmount': finalAmount,
            'sellPrice': sellPrice,
            'sellQty': sellQty,
            'resultadoEsperado': resultado,
            'resultado': finalAmount/amount,
            'network': network,
            'fee': fee,
            'mode': f'{exchange1}->{exchange2}'
        }
        self.df = pd.concat([self.df, pd.DataFrame(data, columns=data.keys(), index=[0])], ignore_index=True)
        self.save()

