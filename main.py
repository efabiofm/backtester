import matplotlib
matplotlib.use('Agg')  # Usar 'Agg' para evitar tkinter
import backtrader as bt
from data_loader import get_chart_data

class PandasData(bt.feeds.PandasData):
    params = (
        ('datetime', None),
        ('open', 'open'),
        ('high', 'high'),
        ('low', 'low'),
        ('close', 'close'),
        ('volume', 'volume'),
        ('openinterest', None),
    )

class EMACrossStrategy(bt.Strategy):
    params = (
        ('fast_period', 20),
        ('slow_period', 200),
        ('atr_period', 14),
    )

    def __init__(self):
        # self.data.close indica a la EMA que use el cierre de la vela
        self.ma_fast = bt.indicators.EMA(self.data.close, period=self.params.fast_period)
        self.ma_slow = bt.indicators.EMA(self.data.close, period=self.params.slow_period)
        self.crossover = bt.indicators.CrossOver(self.ma_fast, self.ma_slow)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)

    def get_order_size(self, entry_price, stop_loss):
        current_balance = self.broker.get_cash()
        risk_per_trade = current_balance * 0.01
        return risk_per_trade / abs(entry_price - stop_loss)
    
    # def notify_order(self, order):
        # Este método se invoca cuando el estado de una orden cambia.
        # if order.status == bt.Order.Completed: # [Canceled, Rejected, Submitted, Accepted]
        #     if order.isbuy():
        #         print(f'Compra ejecutada: {order.executed.price}')
        #     elif order.issell():
        #         print(f'Venta ejecutada: {order.executed.price}')

    def next(self):
        atr_value = self.atr[0]
        if atr_value == 0:
            return

        if not self.position:
            if self.crossover > 0:
                entry_price = self.data.close[0]
                stop_loss = entry_price - (2 * atr_value)
                take_profit = entry_price + (4 * atr_value)
                size = self.get_order_size(entry_price, stop_loss)
                self.buy_bracket(size=size, limitprice=take_profit, stopprice=stop_loss)
            if self.crossover < 0:
                entry_price = self.data.close[0]
                stop_loss = entry_price + (2 * atr_value)
                take_profit = entry_price - (4 * atr_value)
                size = self.get_order_size(entry_price, stop_loss)
                self.sell_bracket(size=size, limitprice=take_profit, stopprice=stop_loss)

# Setup
symbol = 'BTC/USDT'
start_date = '2024-01-01'
end_date = '2025-01-01'
timeframe = '1h'
initial_balance = 10000

df = get_chart_data(start_date, end_date, timeframe, symbol)
data = PandasData(dataname=df)

cerebro = bt.Cerebro()
cerebro.broker.set_cash(initial_balance)
cerebro.broker.setcommission(commission=0.0005)

print(f'Balance inicial: {cerebro.broker.get_cash()}')

cerebro.addstrategy(EMACrossStrategy)
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.adddata(data)
cerebro.run()

final_value = round(cerebro.broker.get_cash(), 2)
strategy_returns = round((final_value - initial_balance) / initial_balance * 100, 2)

print(f'Balance final: {final_value}')
print(f'Rendimiento: {strategy_returns}%')

cerebro.plot(style='candlestick')
