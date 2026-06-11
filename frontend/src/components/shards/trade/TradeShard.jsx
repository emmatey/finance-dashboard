import { useState, useEffect } from 'react'
import { parseResponse } from '../../../scripts/utils.js'
import '../../../styles/utilities.css'
import '../../../styles/colors.css'

export default function TradeShard() {
    
    const [loading, setLoading] = useState(false);

    async function fetchHistory() {
        const safeQuery = String(username).trim();
        try {

        } catch (error) {

        }
    }

    useEffect(() => {
        
    }, [])

    return (
        <div className='card'>
            Trade!
        </div>
    )
}