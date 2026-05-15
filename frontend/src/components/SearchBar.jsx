import { useEffect, useState } from 'react';
import { searchOnline, searchOffline } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

export default function SearchBar() {
    const [data, setData] = useState(null);

    useEffect(() => {
        async function startSearch(){
            const result = await searchOffline("grindr")
            setData(result);
        }
        startSearch();
    }, [])
    console.log(data);
    return (
        <>
        <div>
            <input 
                id='search' 
                type='search' 
                placeholder='Search...'
            />
            <button></button>
        </div>
        </>
    );
}