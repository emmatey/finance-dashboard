import { useEffect, useState } from 'react';
import { searchOnline, searchOffline } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

async function buildDataList(event) {
    /*
        Builds a datalist from the db items LIKE the search query.
    */
    const query = event.target.value;
    const safeQuery = String(query).trim();
    const result = await searchOffline(safeQuery);
    
    let listItems = [];
    const companiesObj = result?.companies??false;
    if (companiesObj && companiesObj?.success == true) {
        for (const obj of companiesObj?.data??[]) {
            listItems.push(`${obj?.ticker??''}: ${obj?.company_name??''} - ${obj?.exchange??''}`);
        };
    };

    const newsObj = result?.news??false
    if (newsObj && newsObj?.success == true) {
        for (const obj of newsObj?.data??[]) {
            listItems.push(`News: ${obj?.title}`);
        };
    };
    
    const usersObj = result?.users??false;
    if (usersObj && usersObj?.success == true) {
        for (const obj of usersObj?.data??[]) {
            listItems.push(`User: ${obj?.username} - Rank: ${obj?.rank??'N/A'}`);
        };
    };

    return listItems
}

export default function SearchBar() {
    const [dataList, setDataList] = useState([]);

    async function handleKeyUp(query) {
        const data = await buildDataList(query);
        setDataList(data);
    }

    return (
        <>
        <div>
            <input 
                id='search' 
                type='search' 
                placeholder='Search...'
                list='offlineSuggest'
                onKeyUp={handleKeyUp}
            />
            <button>Search</button>
            <datalist id='offlineSuggest'>
                {dataList.map((i, index) => (
                    <option key={index} value={i}></option>
                ))}
            </datalist>
        </div>
        </>
    );
}   