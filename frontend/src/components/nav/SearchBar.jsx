import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResponse } from '../../scripts/utils'
import SearchListItem from './SearchListItem';
import SearchListHeader from './SearchListHeader';


export default function SearchBar() {
    const [companyListItems, setCompanyListItems] = useState([]);
    const [userListItems, setUserListItems] = useState([]);
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
        if (!query.trim()) {
            setListIsOpen(false);
            setCompanyListItems([]);
            return;
        }

        const { companies, users, news } = await searchOffline(query);

        const companyNamesPlusTickers = companies["data"].map((item) => (`${item?.ticker} - ${item?.company_name}`));
        const userNames = users["data"].map((item) => (`${item?.username} - Rank: ${item?.rank}`));
        const newsHeadlines = news["data"].map((item) => (item?.title || null));

        setCompanyListItems(companyNamesPlusTickers);
        setUserListItems(userNames);
        setNewsListItems(newsHeadlines);
        setListIsOpen(true);
    }

    return (
        <>
            <div>
                <input id='searchBar' type='text' onKeyUp={handleKeyUp} />

                {listIsOpen && (
                    <ul>
                        {companyListItems.length > 0 && (
                            <>
                                <SearchListHeader label="Companies" />
                                {companyListItems.map((item, i) => (
                                    <SearchListItem key={i} text={item} />
                                ))}
                            </>
                        )}

                        {userListItems.length > 0 && (
                            <>
                                <SearchListHeader label="Users" />
                                {userListItems.map((item, i) => (
                                    <SearchListItem key={i} text={item} />
                                ))}
                            </>
                        )}

                        {newsListItems.length > 0 && (
                            <>
                                <SearchListHeader label="News" />
                                {newsListItems.map((item, i) => (
                                    <SearchListItem key={i} text={item} />
                                ))}
                            </>
                        )}
                    </ul>
                )}
            </div>
        </>
    );
}   