import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import NewsStoryCard from '@/components/home/shards/Newsfeed/NewsStoryCard'

export default function NewsCard({ news }) {
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>News</CardTitle>
            </CardHeader>
            <CardContent className="px-3">
                {news?.length > 0 ? (
                    <ScrollArea className="h-80">
                        <div className="flex flex-col gap-1 pr-3">
                            {news.map((n, i) => (
                                <NewsStoryCard key={n.uuid ?? i} story={n} />
                            ))}
                        </div>
                    </ScrollArea>
                ) : (
                    <p className="px-3 text-sm text-muted-foreground">No news available.</p>
                )}
            </CardContent>
        </Card>
    )
}
