import { use } from 'react';
import '../styles/colors.css';

export default function SearchBar() {
    function searchOnline() {
        // hit api/search
    }

    function searchOffline() {
        // hit api/search/companies(local, i.e query param)
        // news (local)
        // users
        // i.e 3 api hits, concat.
    }

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