from datetime import datetime

def format_uzb_time(dt: datetime) -> str:
    """
    Formats a datetime object into a string with Uzbek day period context.
    
    05:00 - 11:59 -> ertalabki
    12:00 - 17:59 -> kunduzgi
    18:00 - 22:59 -> kechki
    23:00 - 04:59 -> tungi
    """
    hour = dt.hour
    time_str = dt.strftime("%H:%M")
    
    if 5 <= hour < 12:
        period = "ertalabki"
    elif 12 <= hour < 18:
        period = "kunduzgi"
    elif 18 <= hour < 23:
        period = "kechki"
    else:
        period = "tungi"
        
    return f"{period} {time_str}"
