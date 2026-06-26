import { useState } from 'react'
import Header from '@/components/Header.jsx'
import { Card } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'

import UserSummaryShard from './shards/UserSummary/UserSummaryShard.jsx'
import BalanceHistoryShard from './shards/BalanceHistory/BalanceHistoryShard.jsx'
import PortfolioShard from './shards/Portfolio/PortfolioShard.jsx'
import TransactionHistoryShard from './shards/TransactionHistory/TransactionHistoryShard.jsx'
import MarketOverviewShard from './shards/MarketOverview/MarketOverviewShard.jsx'
import ScreenersShard from './shards/Screeners/ScreenersShard.jsx'
import NewsfeedShard from './shards/Newsfeed/NewsfeedShard.jsx'
import ScoreboardShard from './shards/Scoreboard/ScoreboardShard.jsx'
import TradeShard from './shards/Trade/TradeShard.jsx'

export default function HomeBody({ username }) {
    const [activeView, setActiveView] = useState('portfolio')
    const [holdingsTab, setHoldingsTab] = useState('portfolio')

    return (
        <div>
            <Header />
            <h3> Hello {username}! You are logged in! And super cute </h3>
            <NewsfeedShard />
        </div>
    )
}
