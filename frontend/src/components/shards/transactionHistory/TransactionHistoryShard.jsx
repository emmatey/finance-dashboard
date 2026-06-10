import { useState, useEffect } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'


export default function TransactionHistoryShard({ username }) {
    const [historyObjects, setHistoryObjects] = useState([]);
    const [loading, setLoading] = useState(false);

    async function fetchHistory() {
        const safeQuery = String(username).trim();
        try {
            const response = await fetch(`/api/user/transactions?username=${encodeURIComponent(safeQuery)}`);
            return await parseResponse(response);
        } catch (error) {
            console.error(error);
            return [];
        }
    }

    useEffect(() => {
        if (username === undefined) {
            setLoading(true);
        } else if (username) {
            setLoading(false);
            fetchHistory().then(setHistoryObjects);
        }
    }, [username]);

    console.log(historyObjects)
    return (
        <div className='card'>
        
        </div>
    )
}