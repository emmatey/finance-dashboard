import { useState, useEffect } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'


export default function TransactionHistoryShard({ username }) {
    const [historyObjects, setHistoryObjects] = useState([]);

    async function fetchHistory() {
        const safeQuery = String(username).trim();
        const url = '/api/user/transactions';
        const queryParamurl = `/api/user/transactions?username=${safeQuery}`;
        try {
            const response = await fetch(username ? queryParamurl : url);
            setHistoryObjects(await parseResponse(response));
        } catch (error) {
            console.error(error);
            setHistoryObjects([]);
        }
    }

    useEffect(() => {
        fetchHistory().then(setHistoryObjects);
    }, [username]);

    console.log(historyObjects)
    return (
        <div className='card'>
            placeholder
        </div>
    )
}