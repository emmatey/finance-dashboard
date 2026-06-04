
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResponse } from '../scripts/utils.js'

async function searchOffline(query) {
    const safeQuery = String(query).trim();

    const [companies, users, news] = await Promise.all([
        fetch(`/api/search/companies?q=${safeQuery}&local=true`),
        fetch(`/api/search/users?q=${safeQuery}`),
        fetch(`/api/search/news?q=${safeQuery}&local=true`)
    ]);

    const companiesData = await parseResponse(companies);
    const usersData = await parseResponse(users);
    const newsData = await parseResponse(news);

    return {
        'companies': companiesData,
        'users': usersData,
        'news': newsData
    }
}


export default function SearchBar() {


    return (
        <>
        <div>
            <form onSubmit={handleSubmit}>
                <div>
                    <input
                        id='search'
                        type='search'
                        placeholder='Search...'
                        list='offlineSuggest'
                        onKeyUp={handleKeyUp}
                        onInput={handleInput}
                    />
                    <button>Search</button>
                </div>
                <datalist id='offlineSuggest'>
                {dataList.map((i, index) => (
                    <option key={index} value={i}></option>
                ))}
                </datalist>
            </form>
        </div>
        </>
    );
}   