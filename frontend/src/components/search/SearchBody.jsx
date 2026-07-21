import { useState, useEffect } from 'react'
import { parseResponse } from '@/scripts/utils.js'
import SearchListItem from './SearchListItem'
import SearchListHeader from './SearchListHeader'
import { Spinner } from '@/components/ui/spinner'
import { Card, CardContent } from '@/components/ui/card'

export default function SearchBody({ query }) {
    const [results, setResults] = useState(null);

    async function searchOnline(query) {
        const safeQuery = String(query).trim();
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(safeQuery)}`);
            return await parseResponse(response);
        } catch (error) {
            setResults([]);
            console.error(error);
        }
    }

    useEffect(() => {
        if (!query) return;
        searchOnline(query).then(setResults);
    }, [query]);

    if (!query) return <p className="p-4 text-sm text-muted-foreground">No query provided.</p>;
    if (!results) {
        return (
            <div className="flex items-center justify-center py-8">
                <Spinner className="size-6" />
            </div>
        );
    }

    const hasResults = (results.companies ?? []).length > 0
        || (results.users ?? []).length > 0
        || (results.news ?? []).length > 0;

    return (
        <div className="mx-auto max-w-2xl p-4">
            <Card>
                <CardContent>
                    {hasResults ? (
                        <ul>
                            {(results.companies ?? []).length > 0 && (
                                <div>
                                    <SearchListHeader text={"Companies"} />
                                    {results.companies.map((object) => (
                                        <SearchListItem key={object.ticker} object={object} type='company' />
                                    ))}
                                </div>
                            )}
                            {(results.users ?? []).length > 0 && (
                                <div>
                                    <SearchListHeader text={"Users"} />
                                    {results.users.map((object) => (
                                        <SearchListItem key={object.user_id} object={object} type='user' />
                                    ))}
                                </div>
                            )}
                            {(results.news ?? []).length > 0 && (
                                <div>
                                    <SearchListHeader text={"News"} />
                                    {results.news.map((object) => (
                                        <SearchListItem key={object.uuid} object={object} type='news' />
                                    ))}
                                </div>
                            )}
                        </ul>
                    ) : (
                        <p className="text-sm text-muted-foreground">No results for "{query}".</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}