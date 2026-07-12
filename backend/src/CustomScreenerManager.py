from CommonQueries import CommonQueries
import logging


logger = logging.getLogger(__name__)

class CustomScreenerManager(CommonQueries):
    """
    Used to query the database for financial metrics, and then derive arbitrary
    'custom' screeners like 'volume_spikes_bearish' which are not found in yahooquery
    """
    def volume_spike_screeners(self, screeners: Dict, qty: int = 25) -> Dict[str, List[Dict]]:
        """
        Find stocks with largest volume spikes, split by price direction.
        
        Analyzes screener data to identify volume spikes (trading volume significantly
        above 3-month average) and categorizes them as bullish (price up) or bearish
        (price down) based on daily price movement.
        """
        # rows = select volume from financial metrics and price from screeners of all companies that have data 1 hour
        # or newer.
        
        # Calculate relative volume and separate by price direction
        bullish_spikes = []  # Volume spike + price up
        bearish_spikes = []  # Volume spike + price down
        
        for quote in rows:
            current_vol = quote.get('regularMarketVolume', 0)
            avg_vol_3m = quote.get('averageDailyVolume3Month', 1)
            
            # Price change
            current_price = quote.get('regularMarketPrice', 0)
            prev_close = quote.get('regularMarketPreviousClose', 0)
            
            if avg_vol_3m > 0 and prev_close > 0:
                relative_volume = current_vol / avg_vol_3m
                price_change_pct = ((current_price - prev_close) / prev_close) * 100
                
                # Only include significant volume spikes (> 1.5x normal)
                if relative_volume > 1.5:
                    spike_data = {
                        'symbol': quote.get('symbol'),
                        'relative_volume': relative_volume
                    }
                    
                    # Separate by price direction
                    if price_change_pct > 0:
                        bullish_spikes.append(spike_data)
                    else:
                        bearish_spikes.append(spike_data)
        
        # Sort by relative volume (highest spike first)
        bullish_spikes.sort(key=lambda x: x['relative_volume'], reverse=True)
        bearish_spikes.sort(key=lambda x: x['relative_volume'], reverse=True)
        
        # Return both screeners
        self.screeners.update({
            'volume_spike_bullish': bullish_spikes[:qty],
            'volume_spike_bearish': bearish_spikes[:qty]
        })