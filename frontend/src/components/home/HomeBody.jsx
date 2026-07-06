import { useState } from 'react'
import Header from '@/components/Header.jsx'

import PortfolioShard from './shards/Portfolio/PortfolioShard'
import TradeShard from './shards/Trade/TradeShard'

export default function HomeBody({ username }) {
    const [activeView, setActiveView] = useState('portfolio')
    const [holdingsTab, setHoldingsTab] = useState('portfolio')

    return (
        <div>
            <Header />
            <h3> Hello {username}! You are logged in! And super cute </h3>
            <PortfolioShard />
        </div>
    )
}
