import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'

export default function ScreenerCard( {} ) {
    const [screenerData, setScreenerData] = useState(null);

    async function fetchScreeners() {
        /*
        Return value of the /api/screeners route.
        Returns:
        200 - {
            screener_name:[{company_data}, ...]
        }
        Company Data Format:
            {
                'screener_name': str,
                'rank': int,
                'ticker': str,
                'company_name': str,
                'current_price': float,
                'prev_close': float,
                'price_change_pct': float,
                'market_cap': float,
                'todays_volume': int,
                'three_month_avg_volume': int,
                'volume_change_pct': float
            }
        500 - Server error
         */
        // call backend for screeners
        // handle 500
            // Listen for !.ok or code is 500
            // return empty array
            // log error / error in console.
                // do not stop program.
        // handle 200
            // return jsonified data packets in a list 
            // set screenerdata to return value of this request.
            // logger.info (do not write to a file just blue in console if possible?) idk how to say this in js

        // return list of json objects that can be used in the html

        // use effect should run once on component mount. However, do that thing where the component is re-rendered on each change of a specific state i think key?=
        // Make that value the new paramater for the fetch screeners call. 
        // re render

        // before you write, what is the result of one of these screeners making a request, but then the user navigates to a new page before the retun value is recieved.
    }   

    


    return (
        <>
        // print all data in a basic unformatted way, only separated by data packet. 
        // just for testing put all the data out.
        </>
    )
}