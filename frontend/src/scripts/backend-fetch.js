export async function searchOnline(query) {
    const safeQuery = String(query).trim();
    const response = await fetch(`/api/search?q=${safeQuery}`);
    if (!response.ok){
        console.log(response.statusText)
        throw new Error(`Server responded with status: ${response.status}`);
    };

    const data = await response.json();
    return data;
}
export async function searchOffline(query) {
    // hit api/search/companies(local, i.e query param)
    // news (local)
    // users
    // i.e 3 api hits, concat.
    
}