import { useState } from 'react'
import Header from '@/components/Header.jsx'
import NavPanel from '@/components/home/NavPanel.jsx'
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
        <div className="flex flex-col h-screen">
            <Header />
            <div className="flex flex-row flex-1 min-h-0 gap-3 p-3">
                <NavPanel activeView={activeView} setActiveView={setActiveView} />
                <Card className="flex-1 min-w-0 rounded-xl overflow-hidden">
                    <div className="h-full overflow-y-auto p-4 flex flex-col gap-4">

                        {activeView === 'portfolio' && (
                            <>
                                <UserSummaryShard />
                                <BalanceHistoryShard />
                                <div className="flex gap-2">
                                    <Button
                                        variant={holdingsTab === 'portfolio' ? 'secondary' : 'ghost'}
                                        size="sm"
                                        className="rounded-lg"
                                        onClick={() => setHoldingsTab('portfolio')}
                                    >
                                        Holdings
                                    </Button>
                                    <Button
                                        variant={holdingsTab === 'transactions' ? 'secondary' : 'ghost'}
                                        size="sm"
                                        className="rounded-lg"
                                        onClick={() => setHoldingsTab('transactions')}
                                    >
                                        Transactions
                                    </Button>
                                </div>
                                {holdingsTab === 'portfolio'    && <PortfolioShard />}
                                {holdingsTab === 'transactions' && <TransactionHistoryShard />}
                            </>
                        )}

                        {activeView === 'market' && (
                            <>
                                <MarketOverviewShard />
                                <ScreenersShard />
                                <NewsfeedShard />
                            </>
                        )}

                        {activeView === 'trade' && <TradeShard />}

                        {activeView === 'leaderboard' && <ScoreboardShard />}

                    </div>
                </Card>
            </div>
        </div>
    )
}
