from CommonQueries import CommonQueries
from MarketOverviewCoordinator import TableLifetimes
import logging
import time

logger = logging.getLogger(__name__)


class CustomScreenerManager(CommonQueries):
    """
    Used to query the database for financial metrics, and then derive arbitrary
    'custom' screeners like 'volume_spikes_bearish' which are not found in yahooquery.

    This is generally intended to be run immediately after all yahooquery screeners are updated.
    """

    def volume_spike_screeners(self):
        """
        Find stocks with largest volume spikes, split by price direction.

        Analyzes screener data to identify volume spikes (trading volume significantly
        above 3-month average) and categorizes them as bullish (price up) or bearish
        (price down) based on daily price movement.
        """
        sql = """
        SELECT s.last_price, s.ticker, fm.prev_close, fm.todays_volume, fm.three_month_avg_volume
        FROM financial_metrics AS fm
        JOIN symbols AS s
        ON s.id = fm.symbol_id
        WHERE unixepoch(s.last_updated) > ?
        """
        age_threshold = int(time.time()) - int(
            TableLifetimes.SCREENER_UPDATE_FREQUENCY.value
        )
        rows = self.select_query(query=sql, placeholders=tuple([age_threshold]))

        # Calculate relative volume and separate by price direction
        bullish_spikes = []  # Volume spike + price up
        bearish_spikes = []  # Volume spike + price down

        for quote in rows:
            current_vol = quote.get("todays_volume", 0)
            avg_vol_3m = quote.get("three_month_avg_volume", 1)

            # Price change
            current_price = quote.get("last_price", 0)
            prev_close = quote.get("prev_close", 0)

            if avg_vol_3m > 0 and prev_close > 0:
                relative_volume = current_vol / avg_vol_3m
                price_change_pct = ((current_price - prev_close) / prev_close) * 100

                # Only include significant volume spikes (> 1.5x normal)
                if relative_volume > 1.5:
                    spike_data = {
                        "symbol": quote.get("ticker"),
                        "relative_volume": relative_volume,
                    }

                    # Separate by price direction
                    if price_change_pct > 0:
                        bullish_spikes.append(spike_data)
                    else:
                        bearish_spikes.append(spike_data)

        # Sort by relative volume (highest spike first)
        bullish_spikes.sort(key=lambda x: x["relative_volume"], reverse=True)
        bearish_spikes.sort(key=lambda x: x["relative_volume"], reverse=True)

        # Return both screeners
        return {
            "volume_spike_bullish": bullish_spikes,
            "volume_spike_bearish": bearish_spikes,
        }
