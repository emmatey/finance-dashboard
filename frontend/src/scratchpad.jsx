import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { parseResponse } from '../../scripts/utils'
import SearchListItem from './SearchListItem';
import SearchListHeader from './SearchListHeader';


export default function SearchBar() {
    const [companyData, setCompanyData] = useState([]);
    const [userData, setUserData] = useState([]);
    const [newsData, setNewsData] = useState([]);
    const [listIsOpen, setListIsOpen] = useState(false);

    async function searchOffline(query) {
        const safeQuery = String(query).trim();
        // Hit 'local' routes that check DB first, prior to using online api.
        const [companies, users, news] = await Promise.all([
            fetch(`/api/search/companies?q=${safeQuery}&local=true`),
            fetch(`/api/search/users?q=${safeQuery}`),
            fetch(`/api/search/news?q=${safeQuery}&local=true`)
        ]);

        const companiesData = (await parseResponse(companies)).data;
        const usersData = (await parseResponse(users)).data;
        const newsData = (await parseResponse(news)).data;

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
            setCompanyData([]);
            return;
        }
        setTimeout(async () => {
            try {
                const { companies, users, news } = await searchOffline(query);
                setCompanyData(companies);
                setUserData(users);
                setNewsData(news);
                if (companies.length > 0 || users.length > 0 || news.length > 0) {
                    setListIsOpen(true);
                }

            } catch (err) {
                console.error(err);
            };
        }, 200)
    }

    return (
        <div>
            <input id='searchBar' type='text' onKeyUp={handleKeyUp} />
            {listIsOpen && (
                <ul>
                    {companyData.length > 0 && (
                        <>
                            <SearchListHeader label="Companies" />
                            {companyData.map((item) => (
                                <SearchListItem
                                    key={item.id}
                                    text={`${item?.ticker} - ${item?.company_name}`}
                                    onClick={() => { }}
                                />
                            ))}
                        </>
                    )}
                    {userData.length > 0 && (
                        <>
                            <SearchListHeader label="Users" />
                            {userData.map((item) => (
                                <SearchListItem
                                    key={item.user_id}
                                    text={`${item?.username} - Rank: ${item?.rank}`}
                                    onClick={() => { }}
                                />
                            ))}
                        </>
                    )}
                    {newsData.length > 0 && (
                        <>
                            <SearchListHeader label="News" />
                            {newsData.map((item) => (
                                <SearchListItem
                                    key={item.id}
                                    text={item?.title}
                                    onClick={() => { }}
                                />
                            ))}
                        </>
                    )}
                </ul>
            )}
        </div>
    );
} 