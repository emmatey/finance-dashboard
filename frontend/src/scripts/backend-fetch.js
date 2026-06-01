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

export async function logIn(username, password) {
    /* 
        Attempts to log user in.

        Returns: Bool
    */
    const safeUsername = String(username).trim();
    const safePassword = String(password).trim();
    const url = '/api/auth/login';

    try{
        const response = await fetch(url, {
            method:"POST",
            headers: { "Content-Type": "application/json" },
            body:JSON.stringify({
                username: safeUsername,
                password: safePassword
            })
        });
        
        const responseBody = await response.json();
        if (response.status === 400) {
            console.error(responseBody);
            throw new Error(`Server responded with status: ${response.status}`);
        } else if (response.status === 401) {
            console.log(responseBody);
            return (false);
        } else {
            return (true);
        }

    } catch (error) {
        console.error(error.message);
        return null;
    }
}