import { parseResponse } from '../../../../scripts/utils';
import { useState } from 'react';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';


export default function MarketOverview() {
    // Make a fetch request to the route "/api/market_overview"
    // Parse the response.
        // While pending 
            // use state loading is true
        // If reject, since this will always be calling to a fixed route with a fixed parameter theres no need 
            // ... to differentiate for the user what the response code is.
            // ... Simply dont render when this isn't working. Dont bother with feedback or a toast as API down will be evident elsewhere in UI
            // return 
        // else If resolve.
            // const data = [{
            //    region: str,
            //    ticker: str,
            //    company_name: str,
            //    current_price: float,
            //    prev_close: float,
            //    pct_change: float
            //}]

        // For each packet,
            // On each 'region' separate out the data packets.
                // *Some regions like usa will have many packets*
                // set dataUsestate {region: [ticker...], }

    return (
        <>
        {
            /*
                render from the 'data packets' useState

                I want a horizontal bar which has segments with two major categories
                first there's ticker scope wherein each packet is rendered within
                its own small frame. In this frame there should be used the colors from
                colors.css. Please keep css and style inlines to a minimal for the draft

                In the second scope there is a regional container for each group of tickers
                This could be just one ticker or many. The usa will have things like russ5k and nasdaq
                However africa will have just one ETF.
                
                Perhaps we could have a frame for a static image of a flag? 
                followed by frames for cards to sit in and a border? 

                No animaion only use color from colors.css. if you think you need more
                ask me first and then only add them to colors.css
            */
        }
        </>
    )
}