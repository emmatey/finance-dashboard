import UserSummaryShard from './shards/UserSummary/UserSummaryShard'
import NewsfeedShard from './shards/Newsfeed/NewsfeedShard'
import PortfolioShard from './shards/Portfolio/PortfolioShard'
import MarketOverviewShard from './shards/MarketOverview/MarketOverviewShard'
import ScreenersShard from './shards/Screeners/ScreenersShard'
import ScoreboardShard from './shards/Scoreboard/ScoreboardShard'
import TradeShard from './shards/Trade/TradeShard'

export const SHARD_GROUPS = [
    {
        id: 'home',
        label: 'Home',
        shards: [
            { id: 'marketOverview', component: MarketOverviewShard },
            { id: 'newsfeed', component: NewsfeedShard },
            { id: 'userSummary', component: UserSummaryShard },
        ],
    },
    {
        id: 'portfolio',
        label: 'Portfolio',
        shards: [
            { id: 'portfolio', component: PortfolioShard },
        ],
    },
    {
        id: 'screeners',
        label: 'Screeners',
        shards: [
            { id: 'screeners', component: ScreenersShard },
        ],
    },
    {
        id: 'transact',
        label: 'Transact',
        shards: [
            { id: 'trade', component: TradeShard },
        ],
    },
    {
        id: 'leaderboard',
        label: 'Leaderboard',
        shards: [
            { id: 'scoreboard', component: ScoreboardShard },
        ],
    },
]
