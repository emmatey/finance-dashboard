import { Card } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'

const NAV_ITEMS = [
    { view: 'portfolio',   label: 'Portfolio' },
    { view: 'market',      label: 'Market Watch' },
    { view: 'trade',       label: 'Trade' },
    { view: 'leaderboard', label: 'Leaderboard' },
]

export default function NavPanel({ activeView, setActiveView }) {
    return (
        <Card className="w-52 shrink-0 rounded-xl">
            <div className="flex flex-col gap-1 p-2">
                {NAV_ITEMS.map(({ view, label }) => (
                    <Button
                        key={view}
                        variant={activeView === view ? 'secondary' : 'ghost'}
                        className="w-full justify-start rounded-lg"
                        onClick={() => setActiveView(view)}
                    >
                        {label}
                    </Button>
                ))}
            </div>
        </Card>
    )
}
