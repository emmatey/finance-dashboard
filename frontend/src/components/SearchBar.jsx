
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchOnline, searchOffline, unpackResponse } from '../scripts/backend-fetch.js'
import '../styles/colors.css';

async function buildDataListObjects(event) {
    /*
        Returns: {data list item: URL}
    */
    const query = event.target.value;
    const safeQuery = String(query).trim();
    const backend_fetch_result = searchOffline(safeQuery)

    let dataListObjects = [];
    const companiesObj = backend_fetch_result?.companies??false;
    if (companiesObj && companiesObj?.success == true) {
        for (const obj of companiesObj?.data??[]) {
            const company_list_item = {
                li_str: `${obj?.ticker??''}: ${obj?.company_name??''} - ${obj?.exchange??''}`,
                li_url: `/research?ticker=${obj?.ticker??safeQuery}`
            }
            dataListObjects.push(company_list_item);
        };
    };

    const newsObj = backend_fetch_result?.news??false
    if (newsObj && newsObj?.success == true) {
        for (const obj of newsObj?.data??[]) {
            const news_list_item = {
                li_str: `News: ${obj?.title??''}`,
                li_url: obj?.link??''
            }
            dataListObjects.push(news_list_item);
        };
    };

    const usersObj = backend_fetch_result?.users??false;
    if (usersObj && usersObj?.success == true) {
        for (const obj of usersObj?.data??[]) {
            const user_list_item = {
                li_str: `User: ${obj?.username} - Rank: ${obj?.rank??'N/A'}`,
                li_url: `/user/${obj?.username??''}`
            }
            dataListObjects.push(user_list_item);
        };
    };

    return dataListObjects
}

export default function SearchBar() {
    const [dataList, setDataList] = useState([]);
    const [dataListObjects, setDataListObjects] = useState([]);
    const navigate = useNavigate();

    async function handleKeyUp(query) {
        setTimeout(async ()=>{
            const objects = await buildDataListObjects(query);
            setDataListObjects(objects);
            setDataList(objects.map(i => i.li_str));
        }, 100)
    }

    function handleClick(event) {
        const selected = dataListObjects.find(obj => obj.li_str === event.target.value);
        if (!selected) return;

        if (selected.li_url.startsWith('http')) {
            window.open(selected.li_url);
        } else {
            navigate(selected.li_url);
        }
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
                onChange={handleClick}
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