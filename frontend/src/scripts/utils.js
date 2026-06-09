
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

export function formatNumber(n, decimals = 2) {
    /*
        Formats a number with locale-aware thousands separators and a configurable
        number of decimal places. Returns 'N/A' for null or undefined values.
    */
    if (n == null) return 'N/A'
    return Number(n).toLocaleString('en-US', { maximumFractionDigits: decimals })
}

export function formatLargeNumber(n) {
    /*
        Abbreviates large numbers using T/B/M suffixes (e.g. 2500000000 → "2.50B").
        Falls back to locale-formatted output for values under 1 million.
        Returns 'N/A' for null or undefined values.
    */
    if (n == null) return 'N/A'
    const abs = Math.abs(n)
    if (abs >= 1e12) return (n / 1e12).toFixed(2) + 'T'
    if (abs >= 1e9)  return (n / 1e9).toFixed(2)  + 'B'
    if (abs >= 1e6)  return (n / 1e6).toFixed(2)  + 'M'
    return Number(n).toLocaleString('en-US')
}

export function formatAnalystRating(rating) {
    /*
        Converts a raw analyst rating string (snake_case or camelCase) into a
        human-readable title-cased label. Returns 'N/A' for falsy values.
    */
    if (!rating) return 'N/A'
    return rating
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/\b\w/g, c => c.toUpperCase())
}

export function getAnalystRatingColorClass(rating) {
    /*
        Maps an analyst rating string to a Bootstrap text color utility class.
        Buy-side ratings → success, sell-side → danger, everything else → warning.
    */
    if (!rating) return ''
    const r = rating.toLowerCase()
    if (r.includes('buy')) return 'text-success'
    if (r.includes('sell') || r.includes('underperform')) return 'text-danger'
    return 'text-warning'
}

export function getSentimentLabel(score) {
    /*
        Converts a numeric insider sentiment score in the range [-1, 1] to a
        human-readable label. Returns 'No Data' for null or undefined values.
    */
    if (score == null) return 'No Data'
    if (score >  0.5)  return 'Strongly Bullish'
    if (score >  0.15) return 'Bullish'
    if (score > -0.15) return 'Neutral'
    if (score > -0.5)  return 'Bearish'
    return 'Strongly Bearish'
}

export function getSentimentColorClass(score) {
    /*
        Maps a numeric insider sentiment score to a Bootstrap text color utility class.
        Returns 'text-muted' for null or undefined values.
    */
    if (score == null) return 'text-muted'
    if (score >  0.15) return 'text-success'
    if (score < -0.15) return 'text-danger'
    return 'text-warning'
}

export async function parseResponse(response) {
    // 1. Defend against bad inputs
    if (!(response instanceof Response)) {
        throw new Error("response parameter must be a Response object.");
    }

    let body;
    
    // 2. Safely try to parse the JSON once
    try { 
        body = await response.json(); 
    } catch (error) {
        console.error(error);
    }

    // 3. Handle HTTP errors (4xx, 5xx)
    if (!response.ok) {
        console.error("Server Error Payload:", body);
        throw new Error(`Server responded with status: ${response.status}`);
    }

    // 4. Handle API-level business logiparseResc failures
    if (body?.success === false) {
        console.error("API Logic Failure:", body);
        throw new Error(body.message ?? 'Request failed');
    }

    // 5. Cleanly strip 'success' without mutating, and return the rest
    if (body && 'success' in body) {
        const { success, ...cleanBody } = body;
        return cleanBody;
    }

    return body;
}