def reorder_point(avg_daily_usage, lead_time_days, safety_stock):
    return (avg_daily_usage * lead_time_days) + safety_stock

def calculate_safety_stock(max_daily_usage, max_lead_time, avg_daily_usage, avg_lead_time):
    return (max_daily_usage * max_lead_time) - (avg_daily_usage * avg_lead_time)
