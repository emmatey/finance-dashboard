import TickerCard from './TickerCard';
import '../../../../styles/utilities.css'

export default function MarketRegion({ region, packets }) {
    return (
        <div className='card'>
            <strong>{region}</strong>
            <ul>
                {packets.map((packet) => (
                    <TickerCard key={packet.ticker} packet={packet} />
                ))}
            </ul>
        </div>
    );
}
