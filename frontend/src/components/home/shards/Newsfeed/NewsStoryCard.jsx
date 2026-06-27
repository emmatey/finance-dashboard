import { formatUTCSeconds } from "@/scripts/utils"

export default function NewsStoryCard({ story }) {
    function handleClick() {
        if (story?.link) {
            window.open(story.link, '_blank', 'noopener,noreferrer');
        }
    }

    return (
        <div className='flex flex-row items-center gap-3 p-3 hover:bg-muted cursor-pointer transition-colors rounded-lg' onClick={handleClick}>
            <img
                src={story?.thumbnail}
                className="flex-shrink-0 w-14 h-14 object-cover rounded-md"
                onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/images/searchBar/newsIcon.svg'
                }}
                alt="Article thumbnail."
            />
            <div className="flex flex-col gap-1">
                <span className="text-sm font-medium leading-snug line-clamp-2">
                    {story?.title ?? "Title not found"}
                </span>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <span>{story?.publisher ?? "Unknown publisher"}</span>
                    <span>·</span>
                    <span>{story?.providerPublishTime ? formatUTCSeconds(story.providerPublishTime) : "Unknown date"}</span>
                </div>
            </div>
        </div>
    )
}
