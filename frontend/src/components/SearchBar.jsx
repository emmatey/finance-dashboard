import { useEffect, useState } from 'react';
import { searchOnline, searchOffline } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

function buildDataList(query) {
    const result = await searchOffline("grindr")
    
}

export default function SearchBar() {
    const [data, setData] = useState(null);



    return (
        <>
        <div>
            <input 
                id='search' 
                type='search' 
                placeholder='Search...'
            />
            <button>Search</button>
        </div>
        </>
    );
}