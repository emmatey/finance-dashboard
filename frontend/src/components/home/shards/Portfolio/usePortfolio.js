import { useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import { useAuth } from '@/context/AuthContext.jsx';

export default function usePortfolio(setHoldingsObjects, setLoading) {
    const { user } = useAuth();

    useEffect(() => {
        if (user === undefined) {
            setLoading(true)
            return
        };
        if (!user) {
            return;
        };

        async function fetchHoldings(user) {
            const url = '/api/';
            try {
                
            } catch (error) {
                console.error(error);
                return [];
            }
        }
    }, [user])
}