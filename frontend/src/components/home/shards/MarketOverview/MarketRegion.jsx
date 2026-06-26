import TickerCard from './TickerCard';
import '@/styles/utilities.css'

export default function MarketRegion({ name, items }) {
    return (
        <>
            {items.map((ticker) => (
                <TickerCard key={ticker.symbol} ticker={ticker} />
            ))}
        </>
    )
}
