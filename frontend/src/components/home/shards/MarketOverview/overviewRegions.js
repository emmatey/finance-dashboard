// 'region' : Display Name
const SYMBOLS = {
    'USA S&P 500': 'USA',
    'USA Dow': 'USA',
    'USA Nasdaq': 'USA',
    'USA Russell 2000': 'USA',
    'EU': 'Europe',
    'LATAM': 'Latin America',
    'Africa': 'Africa',
    'Australia': 'Australia',
    'India': 'India',
    'Japan': 'Japan',
    'China': 'China',
    'Gold': 'Commodities',
    'Copper': 'Commodities',
    'Oil': 'Commodities'
}

export default function getDisplayName(regionValue){
    return SYMBOLS?.[regionValue] ?? "Other";
}

