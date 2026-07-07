// The backend has no notion of "region" vs "commodity" - MarketOverviewCoordinator.SYMBOLS
// (backend/src/MarketOverviewCoordinator.py) is one flat {label: ticker} dict. This mapping
// is purely a homepage display grouping and must mirror SYMBOLS' keys.
export const CATEGORY_ORDER = ['Regions', 'Commodities']

const CATEGORY_BY_REGION = {
    'USA S&P 500': 'Regions',
    'USA Dow': 'Regions',
    'USA Nasdaq': 'Regions',
    'USA Russell 2000': 'Regions',
    EU: 'Regions',
    LATAM: 'Regions',
    Africa: 'Regions',
    Australia: 'Regions',
    India: 'Regions',
    Japan: 'Regions',
    China: 'Regions',
    Gold: 'Commodities',
    Copper: 'Commodities',
    Oil: 'Commodities',
}

// Anything not in the map above (e.g. a new ticker added to SYMBOLS without updating this
// file) falls into 'Other' instead of silently disappearing from the page.
export function getMarketOverviewCategory(regionName) {
    return CATEGORY_BY_REGION[regionName] ?? 'Other'
}
