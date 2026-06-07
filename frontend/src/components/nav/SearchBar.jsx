import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResponse } from '../../scripts/utils'


export default function SearchBar() {
    const [companyListItems, setCompanyListItems] = useState([]);
    const [userlistItems, setUserListItems] = useState([]);
    const [newsListItems, setNewsListItems] = useState([]);
    const [listIsOpen, setListIsOpen] = useState(false);

    async function searchOffline(query) {
        const safeQuery = String(query).trim();
        // Hit 'local' routes that check DB first, prior to using online api.
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

    async function handleKeyUp(event) {
        const query = event.target.value;
        const { companies, users, news } = await searchOffline(query);
        
        const companyNamesPlusTickers = companies["data"].map((item) => (`${item?.ticker} - ${item?.company_name}`));
        const userNames = users["data"].map((item) => (``))
        const newsHeadlines = news["data"].map((item) => (item?.title || null));


        setCompanyListItems(companyNamesPlusTickers);
        setUserListItems(users);
        setNewsListItems(newsHeadlines);
    }

    return (
        <>
            {console.log(userlistItems)}
            <div>
                <input id='searchBar' list='searchList' type='text' onKeyUp={handleKeyUp}></input>

                { listIsOpen ?  : null}
            </div>
        </>
    );
}   