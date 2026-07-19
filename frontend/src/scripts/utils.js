export function formatCurrencyUSD(n) {
    /*
        Formats a number as a USD currency string with full precision.
        Returns 'N/A' for null or undefined values.
    */
    if (n == null) return 'N/A'
    return Number(n).toLocaleString('en-US', { style: 'currency', currency: 'USD' })
}

export function formatPercent(n) {
    /*
        Converts a decimal ratio to a percentage string rounded to 2 decimal places.
        e.g. 0.053 → "5.30%". Returns 'N/A' for null or undefined values.
    */
    if (n == null) return 'N/A'
    return (Number(n) * 100).toFixed(2) + '%'
}

export function formatUTCSeconds(timestamp) {
  /**
   * Converts a Unix timestamp (in seconds) to US short date format (M/D/YY).
   * * @param {number} timestamp - The Unix timestamp in seconds.
   * @returns {string} - The formatted date (e.g., "3/31/26").
   */

  // Convert seconds to milliseconds
  const date = new Date(timestamp * 1000);
  
  return date.toLocaleDateString('en-US', {
    month: 'numeric', 
    day: 'numeric',   
    year: '2-digit'   
  });
}

export function formatNumber(n, decimals = 2) {
    /*
        Formats a number with locale-aware thousands separators and a configurable
        number of decimal places. Returns 'N/A' for null or undefined values.
    */
    if (n == null) return 'N/A'
    return Number(n).toLocaleString('en-US', { maximumFractionDigits: decimals })
}

export async function parseResponse(response) {
    let body = {};
    try {
        body = await response.json();
    } catch (e) {
        console.error(e);
    }

    if (!response.ok || body?.success === false) {
        const error = new Error(body.message || `Request failed with status ${response.status}`);
        error.status = response.status;
        error.data = body;
        throw error;
    }

    // Success: return data without the 'success' key
    const { success, ...cleanBody } = body;
    return cleanBody;
}

export function getRandomAccentColor() {
    const colors = ['var(--blue-3)', 'var(--yellow-4)', 'var(--red-3)', 'var(--green-3)'];
    return colors[getRandomIntInclusive(0, colors.length - 1)];
}

export function getRandomIntInclusive(min, max) {
    /* 
        https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random#examples
    */
    const minCeiled = Math.ceil(min);
    const maxFloored = Math.floor(max);
    return Math.floor(Math.random() * (maxFloored - minCeiled + 1) + minCeiled); // The maximum is inclusive and the minimum is inclusive
}

export function adjustPendingOrder(qtyUnit, qty, currentPrice) {
    if (!qtyUnit || !qty || !currentPrice) {
        return false;
    }
    
    if (qtyUnit === 'shares') {
        const shares = Math.round(qty * 10) / 10; // Ensure it's valid 1/10th
        const dollars = Math.round(shares * currentPrice * 100) / 100; // Round to cents
        return [dollars, shares];
    }

    if (qtyUnit === 'dollars') {
        const rawShares = qty / currentPrice;
        const adjustedShares = Math.round(rawShares * 10) / 10;
        const adjustedDollars = Math.round(adjustedShares * currentPrice * 100) / 100;

        return [adjustedDollars, adjustedShares];
    }

    return [0, 0];
}