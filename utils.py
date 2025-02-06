risk_percentage = 0.01

def get_order_size(current_balance, entry_price, stop_loss):
    risk_per_trade = current_balance * risk_percentage
    risk_per_unit = Math.abs(entry_price - stop_loss)
    return risk_per_trade / risk_per_unit
