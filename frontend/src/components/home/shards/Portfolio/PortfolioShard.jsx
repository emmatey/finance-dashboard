import { useState } from "react";
import usePortfolio from "./usePortfolio";


export default function PortfolioShard() {
    const [holdingsObjects, setHoldingsObjects] = useState([]);
    const [loading, setLoading] = useState(false);

    usePortfolio(setHoldingsObjects, setLoading);

    return (
        <div className='card'>
            {loading && (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100px' }}>
                    <span>Loading...</span>
                </div>
            )}
            {!loading && <table>
                <thead>
                    <tr>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    {}
                </tbody>
            </table>}
        </div>
    )
}