import { use } from 'react';
import { searchOnline, searchOffline } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

export default function SearchBar() {
    searchOnline("grindr");

    return (
        <>
        <div>
            <input 
                id='search' 
                type='search' 
                placeholder='Search...' >
            </input>
            <button></button>
        </div>
        </>
    );
}