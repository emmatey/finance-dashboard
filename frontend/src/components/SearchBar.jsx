import { use } from 'react';
import '../styles/colors.css';

export default function SearchBar() {
    function searchOnline() {
        
    }

    function searchOffline() {

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