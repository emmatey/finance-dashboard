
export async function unpackResponse(response) {
    /* */
    if (!(response instanceof Response)) {
        throw new Error("response parameter must be a Response object.")
    }
    if (!response.ok){
        console.error(response.statusText)
        throw new Error(`Server responded with status: ${response.status}`);
    }

    let data = {}
    try {
        data = await response.json();
    } catch (error) {
      console.error(`The response object provided. /n'${response}'/m is not compatable with JSON format.e`, error)
      console.error("Response status was:", response.status)
      data = {}
    }

    return data;
}

export async function searchOnline(query) {
    const safeQuery = String(query).trim();
    const response = await fetch(`/api/search?q=${safeQuery}`);
    const data = await unpackResponse(response);
    
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
    
    const companiesData = await unpackResponse(companies);
    const usersData = await unpackResponse(users);
    const newsData = await unpackResponse(news);

    return { 
        'companies': companiesData,
        'users': usersData,
        'news': newsData
    }
}