import { unpackResponse } from '../scripts/backend-fetch.js';
import { useEffect, useState } from 'react';
import { searchOnline, searchOffline } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

async function buildDataListObjects(event) {
    /*
        Returns: {data list item: URL}
    */
    const query = event.target.value;
    const safeQuery = String(query).trim();
    const backend_fetch_result = await searchOffline(safeQuery);
    
    let listItems = [];
    const companiesObj = backend_fetch_result?.companies??false;
    if (companiesObj && companiesObj?.success == true) {
        for (const obj of companiesObj?.data??[]) {
            const list_item = {
                li_str: "(`${obj?.ticker??''}: ${obj?.company_name??''} - ${obj?.exchange??''}`)",
                li_url: 
            }
            listItems.push;
        };
    };

    const newsObj = backend_fetch_result?.news??false
    if (newsObj && newsObj?.success == true) {
        for (const obj of newsObj?.data??[]) {
            listItems.push(`News: ${obj?.title}`);
        };
    };
    
    const usersObj = backend_fetch_result?.users??false;
    if (usersObj && usersObj?.success == true) {
        for (const obj of usersObj?.data??[]) {
            listItems.push(`User: ${obj?.username} - Rank: ${obj?.rank??'N/A'}`);
        };
    };

    return listItems
}

async function request_at_selected_url() {
    
}

export default function SearchBar() {
    const [dataList, setDataList] = useState([]);

    async function handleKeyUp(query) {
        setTimeout(async ()=>{

        }, 100)
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