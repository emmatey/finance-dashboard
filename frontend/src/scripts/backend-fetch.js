import { unpackFetchResponse } from './utils.js'

export async function searchOnline(query) {
    const safeQuery = String(query).trim();
    const response = await fetch(`/api/search?q=${safeQuery}`);
    const data = await unpackFetchResponse(response);

    return data;
}

export async function searchOffline(query) {
    /*
        Requests data similar to the search query via app.py.
    */
    const safeQuery = String(query).trim();

    const [companies, users, news] = await Promise.all([
        fetch(`/api/search/companies?q=${safeQuery}&local=true`),
        fetch(`/api/search/users?q=${safeQuery}`),
        fetch(`/api/search/news?q=${safeQuery}&local=true`)
    ]);

    const companiesData = await unpackFetchResponse(companies);
    const usersData = await unpackFetchResponse(users);
    const newsData = await unpackFetchResponse(news);

    return {
        'companies': companiesData,
        'users': usersData,
        'news': newsData
    }
}