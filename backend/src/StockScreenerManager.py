import logging
import time
from APIDataIO import APIDataIO as io
from CommonQueries import CommonQueries
from enum import Enum
from logging_utils import fmt_data
from YahooQueryService import YahooQueryService as yqs

logger = logging.getLogger(__name__)

# Screeners derived from already-stored data rather than fetched from yahooquery.
CUSTOM_SCREENERS = ["volume_spike_bullish", "volume_spike_bearish"]

# Screener names grouped by category, so the frontend can request a whole
# category at once or a single screener within it. Scoped to US equities -
# yahooquery also exposes ETF/mutual fund/crypto/non-US-region variants of
# many of these (e.g. 'day_gainers_de', 'day_gainers_etfs'), deliberately
# excluded since financial_metrics (PE, EPS, dividend yield, etc.) is shaped
# around equities and would be mostly null for those asset classes.
SCREENER_CATEGORIES: dict[str, list[str]] = {
    "movers": [
        "day_gainers",
        "day_losers",
        "most_actives",
        "most_watched_tickers",
        "fifty_two_wk_gainers",
        "fifty_two_wk_losers",
        "most_shorted_stocks",
        "upside_breakout_stocks_daily",
        "bullish_stocks_right_now",
        "bearish_stocks_right_now",
        "small_cap_gainers",
        "aggressive_small_caps",
        "largest_market_cap",
        "growth_technology_stocks",
    ],
    "value_growth": [
        "undervalued_growth_stocks",
        "undervalued_large_caps",
        "undervalued_wide_moat_stocks",
        "strong_undervalued_stocks",
        "morningstar_five_star_stocks",
        "net_net_strategy",
        "the_acquirers_multiple",
    ],
    "analyst_sentiment": [
        "analyst_strong_buy_stocks",
        "latest_analyst_upgraded_stocks",
        "community_sentiment_most_bullish",
        "community_sentiment_most_bearish",
    ],
    "institutional_activity": [
        "most_institutionally_bought_large_cap_stocks",
        "most_institutionally_held_large_cap_stocks",
        "most_institutionally_sold_large_cap_stocks",
        "stocks_most_bought_by_hedge_funds",
        "stocks_most_bought_by_pension_fund",
        "stocks_most_bought_by_private_equity",
        "stocks_most_bought_by_sovereign_wealth_fund",
        "stocks_with_most_institutional_buyers",
        "stocks_with_most_institutional_sellers",
        "top_stocks_owned_by_cathie_wood",
        "top_stocks_owned_by_goldman_sachs",
        "top_stocks_owned_by_ray_dalio",
        "top_stocks_owned_by_warren_buffet",
        "portfolio_actions_most_added",
        "portfolio_actions_most_deleted",
        "portfolio_anchors",
    ],
    # Morningstar's 11 broad sector rollups.
    "sector": [
        "ms_basic_materials",
        "ms_communication_services",
        "ms_consumer_cyclical",
        "ms_consumer_defensive",
        "ms_energy",
        "ms_financial_services",
        "ms_healthcare",
        "ms_industrials",
        "ms_real_estate",
        "ms_technology",
        "ms_utilities",
    ],
    "trending": [
        "most_visited",
        "most_visited_basic_materials",
        "most_visited_communication_services",
        "most_visited_consumer_cyclical",
        "most_visited_consumer_defensive",
        "most_visited_energy",
        "most_visited_financial_services",
        "most_visited_healthcare",
        "most_visited_industrials",
        "most_visited_real_estate",
        "most_visited_technology",
        "most_visited_utilities",
    ],
    # Granular GICS-style industry screeners.
    "industry": [
        "advertising_agencies",
        "aerospace_defense",
        "agricultural_inputs",
        "airlines",
        "airports_air_services",
        "aluminum",
        "apparel_manufacturing",
        "apparel_retail",
        "asset_management",
        "auto_manufacturers",
        "auto_parts",
        "auto_truck_dealerships",
        "banks_diversified",
        "banks_regional",
        "beverages_brewers",
        "beverages_non_alcoholic",
        "beverages_wineries_distilleries",
        "biotechnology",
        "broadcasting",
        "building_materials",
        "building_products_equipment",
        "business_equipment_supplies",
        "capital_markets",
        "chemicals",
        "coking_coal",
        "communication_equipment",
        "computer_hardware",
        "confectioners",
        "conglomerates",
        "consulting_services",
        "consumer_electronics",
        "copper",
        "credit_services",
        "department_stores",
        "diagnostics_research",
        "discount_stores",
        "drug_manufacturers_general",
        "drug_manufacturers_specialty_generic",
        "education_training_services",
        "electrical_equipment_parts",
        "electronic_components",
        "electronic_gaming_multimedia",
        "electronics_computer_distribution",
        "engineering_construction",
        "entertainment",
        "farm_heavy_construction_machinery",
        "farm_products",
        "financial_conglomerates",
        "financial_data_stock_exchanges",
        "food_distribution",
        "footwear_accessories",
        "furnishings_fixtures_appliances",
        "gambling",
        "gold",
        "grocery_stores",
        "health_information_services",
        "healthcare_plans",
        "high_yield_high_return",
        "home_improvement_retail",
        "household_personal_products",
        "industrial_distribution",
        "information_technology_services",
        "infrastructure_operations",
        "insurance_brokers",
        "insurance_diversified",
        "insurance_life",
        "insurance_property_casualty",
        "insurance_reinsurance",
        "insurance_specialty",
        "integrated_freight_logistics",
        "internet_content_information",
        "internet_retail",
        "leisure",
        "lodging",
        "lumber_wood_production",
        "luxury_goods",
        "marine_shipping",
        "medical_care_facilities",
        "medical_devices",
        "medical_distribution",
        "medical_instruments_supplies",
        "mega_cap_hc",
        "metal_fabrication",
        "mortgage_finance",
        "oil_gas_drilling",
        "oil_gas_e_p",
        "oil_gas_equipment_services",
        "oil_gas_integrated",
        "oil_gas_midstream",
        "oil_gas_refining_marketing",
        "other_industrial_metals_mining",
        "other_precious_metals_mining",
        "packaged_foods",
        "packaging_containers",
        "paper_paper_products",
        "personal_services",
        "pharmaceutical_retailers",
        "pollution_treatment_controls",
        "publishing",
        "railroads",
        "real_estate_development",
        "real_estate_diversified",
        "real_estate_services",
        "recreational_vehicles",
        "reit_diversified",
        "reit_healthcare_facilities",
        "reit_hotel_motel",
        "reit_industrial",
        "reit_mortgage",
        "reit_office",
        "reit_residential",
        "reit_retail",
        "reit_specialty",
        "rental_leasing_services",
        "residential_construction",
        "resorts_casinos",
        "restaurants",
        "scientific_technical_instruments",
        "security_protection_services",
        "semiconductor_equipment_materials",
        "semiconductors",
        "shell_companies",
        "silver",
        "software_application",
        "software_infrastructure",
        "solar",
        "specialty_business_services",
        "specialty_chemicals",
        "specialty_industrial_machinery",
        "specialty_retail",
        "staffing_employment_services",
        "steel",
        "telecom_services",
        "textile_manufacturing",
        "thermal_coal",
        "tobacco",
        "tools_accessories",
        "top_energy_us",
        "travel_services",
        "trucking",
        "uranium",
        "utilities_diversified",
        "utilities_independent_power_producers",
        "utilities_regulated_electric",
        "utilities_regulated_gas",
        "utilities_regulated_water",
        "utilities_renewable",
        "waste_management",
    ],
    # Derived screeners computed from already-stored data (see
    # volume_spike_screeners) rather than fetched from yahooquery.
    "custom": CUSTOM_SCREENERS,
}

# Flat list of every yahooquery-sourced screener name, derived from
# SCREENER_CATEGORIES so the two can't drift out of sync.
YQ_SCREENER_NAMES = [
    name
    for category, names in SCREENER_CATEGORIES.items()
    if category != "custom"
    for name in names
]


class TableLifetimes(Enum):
    YQ_SCREENER_UPDATE_FREQUENCY = 60 * 60

class StockScreenerManager(CommonQueries):
    """
    Handles fetching, filtering, deriving, and persisting stock screener data
    (yahooquery screeners like 'day_gainers', plus custom screeners derived
    from already-stored data like 'volume_spike_bullish').
    """

    def screener_fresh_report(self, screener_names, limit=None):
        """
        Checks the age of the screeners to be fetched.
        Returns: [{screener: bool}, ...]
            Fresh = True
            Stale = False
        """
        now = int(time.time())
        update_frequency = TableLifetimes.YQ_SCREENER_UPDATE_FREQUENCY.value
        fresh_report = {
            screener_name: False
            for screener_name in screener_names
            if screener_name not in CUSTOM_SCREENERS
        }

        placeholders = ",".join(["?" for _ in screener_names])
        last_updated_sql = f"""
        SELECT screener_name, unixepoch(last_updated) AS last_updated
        FROM screener_ages
        WHERE screener_name IN ({placeholders})
        """
        if limit:
            last_updated_sql = last_updated_sql + f"LIMIT {limit}"
        rows = self.select_query(
            query=last_updated_sql, placeholders=tuple(screener_names)
        )
        for row in rows:
            screener_name = row["screener_name"]
            last_updated = row["last_updated"]
            age = now - int(last_updated)
            if age < update_frequency:
                fresh_report[screener_name] = True
            else:
                fresh_report[screener_name] = False

        return fresh_report

    def fetch_and_filter_screeners(
        self, screener_names, screener_count=100, yqs_instance=None
    ):
        """
        Fetch the given screener names from yahooquery and apply the standard
        quality filters (see YahooQueryService._filter_screener_data).

        Pure fetch+filter - takes a list of any size (one screener for a lazy,
        on-demand refresh; many for a bulk/background sweep) and hands back a
        filtered screeners dict. Callers decide what to do with the result
        (merge in derived/custom screeners, persist it, etc).

        Returns:
            Filtered screeners dict, or None if the fetch failed (API down or
            circuit breaker active - see yq_screener_fetch_screeners).
        """
        if yqs_instance is None:
            yqs_instance = yqs()

        logger.info(
            f"Fetching {len(screener_names)} screeners: {fmt_data(screener_names)}"
        )
        screeners = yqs_instance.yq_screener_fetch_screeners(
            screeners=screener_names, count=screener_count
        )
        # yq_screener_fetch_screeners returns None if the API is down or the
        # circuit breaker is active.
        if screeners is None:
            logger.warning("Screener fetch returned None - API may be down or circuit breaker active")
            return None
        return yqs_instance._filter_screener_data(screeners)

    def write_screener_data(
        self, filtered_screeners, yqs_instance=None, dbio_instance=None
    ):
        """
        Persist an already-filtered screeners dict: extracts metadata/rankings
        and price/financial data, upserts symbols, and writes screener
        rankings + per-screener ages.

        Works for both real (yq-sourced) and derived/custom screener dicts,
        since it only cares about the filtered screener shape, not its origin.
        """
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()

        total_symbols = sum(len(v) for v in filtered_screeners.values())
        logger.info(
            f"Writing screener data: {len(filtered_screeners)} screeners, {total_symbols} symbols"
        )

        # Extract metadata and rankings
        metadata = yqs_instance.extract_screener_metadata(filtered_screeners)
        screeners_present: list[str] = list(metadata.keys())

        # Extract price and financial data
        price_modules, financial_metrics = yqs_instance.extract_screener_data(
            filtered_screeners
        )

        # Upsert symbols first (screener rankings reference symbol_id)
        dbio_instance.upsert_symbols(price_modules)

        # Insert screener rankings + refresh their ages (scoped to these screener names)
        dbio_instance.set_screener_results(metadata)
        dbio_instance.set_screener_ages(screeners_present)

        # Update financial metrics (incomplete data, don't update last_updated timestamp)
        dbio_instance.set_financial_metrics(financial_metrics, from_screeners=True)

    def screener_data_update_orchestrator(
        self,
        screener_names=YQ_SCREENER_NAMES,
        yqs_instance=None,
        dbio_instance=None,
    ):
        """
        Checks the age of screener data and updates if stale.
        Updates all screeners if data is older than SCREENER_UPDATE_FREQUENCY.
        """
        if yqs_instance is None:
            yqs_instance = yqs()
        if dbio_instance is None:
            dbio_instance = io()

        fresh_report = self.screener_fresh_report(screener_names)
        stale_screeners = [
            screener for screener, fresh_bool in fresh_report.items() if not fresh_bool
        ]
        if not stale_screeners:
            logger.info("All screeners up to date, skipping refresh.")
            return

        logger.info(
            f"Screener refresh: {len(stale_screeners)} stale, "
            f"{len(fresh_report) - len(stale_screeners)} fresh."
        )
        filtered_screeners = self.fetch_and_filter_screeners(stale_screeners)
        if filtered_screeners is None:
            logger.warning("Screener data update orchestrator aborted - fetch failed.")
            return

        self.write_screener_data(filtered_screeners, yqs_instance, dbio_instance)
        logger.info("Screener data update orchestrator complete.")

    def volume_spike_screeners(self) -> bool:
        """
        Find stocks with largest volume spikes, split by price direction.

        Analyzes screener data to identify volume spikes (trading volume significantly
        above 3-month average) and categorizes them as bullish (price up) or bearish
        (price down) based on daily price movement.

        Intended to be run immediately after all yahooquery screeners are updated
        (see screener_data_update_orchestrator), since it reads from financial_metrics
        rows that update populates.

        Returns:
            True on success, False on failure.
        """
        try:
            sql = """
            SELECT s.last_price, s.id, fm.prev_close, fm.todays_volume, fm.three_month_avg_volume
            FROM financial_metrics AS fm
            JOIN symbols AS s
            ON s.id = fm.symbol_id
            WHERE unixepoch(s.last_updated) > ?
            """
            age_threshold = int(time.time()) - int(60 * 30)
            rows = self.select_query(query=sql, placeholders=tuple([age_threshold]))

            # Calculate relative volume and separate by price direction
            bullish_spikes: list[dict] = []  # Volume spike + price up
            bearish_spikes: list[dict] = []  # Volume spike + price down

            for quote in rows:
                current_vol = quote.get("todays_volume", 0)
                avg_vol_3m = quote.get("three_month_avg_volume", 1)

                # Price change
                current_price = quote.get("last_price", 0)
                prev_close = quote.get("prev_close", 0)

                if (
                    avg_vol_3m > 0 and prev_close > 0
                ):  # Prevent divide by 0, crashing with corrupt data
                    relative_volume = current_vol / avg_vol_3m
                    price_change_pct = ((current_price - prev_close) / prev_close) * 100

                    # Only include significant volume spikes (> 1.5x normal)
                    if relative_volume > 1.5:
                        spike_data = {
                            "symbol_id": quote.get("id"),
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

            # Add Rank
            for idx, company in enumerate(bullish_spikes, start=1):
                company["rank"] = idx
                company["screener_name"] = "volume_spike_bullish"
            for idx, company in enumerate(bearish_spikes, start=1):
                company["screener_name"] = "volume_spike_bearish"
                company["rank"] = idx

            # Clear old rows for these two derived screeners before reinserting
            self.modify_query(
                f"""
                DELETE FROM screener_results
                WHERE screener_name IN ({",".join(['?' for _ in CUSTOM_SCREENERS])})
                """,
                tuple(CUSTOM_SCREENERS)
            )

            # Insert into DB
            insert_sql = """
                INSERT INTO screener_results (symbol_id, screener_name, rank)
                VALUES (?, ?, ?)
            """
            screener_tuples = []
            for screener in bullish_spikes + bearish_spikes:
                screener_result = (
                    screener["symbol_id"],
                    screener["screener_name"],
                    screener["rank"],
                )
                screener_tuples.append(screener_result)

            self.bulk_query(query=insert_sql, data_list=screener_tuples, label="screener_results")

            logger.info("Volume spike screeners updated successfully.")
            return True

        except Exception:
            logger.exception("volume_spike_screeners failed")
            return False
