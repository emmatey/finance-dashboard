import TickerCard from './TickerCard';

export default function MarketRegion({ region, packets }) {
    return (
        <div>
            <strong>{region}</strong>
            <ul>
                {packets.map((packet) => (
                    <TickerCard key={packet.ticker} packet={packet} />
                ))}
            </ul>
        </div>
    );
}
