
import { useEffect, useState } from 'react';
import { searchOnline, searchOffline } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

async function buildDataListObjects(event) {
    /*
        Returns: {data list item: URL}
    */
    const query = event.target.value;
    const safeQuery = String(query).trim();
    
    let listItems = [];
    const companiesObj = backend_fetch_result?.companies??false;
    if (companiesObj && companiesObj?.success == true) {
        for (const obj of companiesObj?.data??[]) {
            const company_list_item = {
                li_str: "(`${obj?.ticker??''}: ${obj?.company_name??''} - ${obj?.exchange??''}`)",
                li_url: `/api/research/online?ticker=${safeQuery}`
            }
            listItems.push(company_list_item);
        };
    };

    const newsObj = backend_fetch_result?.news??false
    if (newsObj && newsObj?.success == true) {
        for (const obj of newsObj?.data??[]) {
            const news_list_item = {
                li_str: `News: ${obj?.title??''}`,
                li_url: `/api/news?id=${obj?.id??''}`
            }

            listItems.push(news_list_item);
        };
    };

    const usersObj = backend_fetch_result?.users??false;
    if (usersObj && usersObj?.success == true) {
        for (const obj of usersObj?.data??[]) {
            const user_list_item = {
                li_str: `User: ${obj?.username} - Rank: ${obj?.rank??'N/A'}`,
                li_url: `/api/user/${obj?.username??''}`
            }
            listItems.push(user_list_item);
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