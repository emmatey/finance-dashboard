import { useState } from 'react'
import Header from '@/components/Header.jsx'

import UserSummaryShard from './shards/UserSummary/UserSummaryShard'

export default function HomeBody({ username }) {
    const [activeView, setActiveView] = useState('portfolio')
    const [holdingsTab, setHoldingsTab] = useState('portfolio')

    return (
        <div>
            <Header />
            <h3> Hello {username}! You are logged in! And super cute </h3>
            <UserSummaryShard />

        </div>
    )
}
