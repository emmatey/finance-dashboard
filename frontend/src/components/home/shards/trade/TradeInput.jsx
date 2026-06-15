import TradeSearch from './TradeSearch.jsx';
import TradeOrderForm from './TradeOrderForm.jsx';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

export default function TradeInput({ 
    activeQuery, 
    setActiveQuery, 
    loading, 
    tickerInfoJson, 
    setPendingOrder 
}) {
    return (
        <div style={{ display: 'flex', gap: '16px' }}>
            <div className='card'>
                <TradeSearch
                    activeQuery={activeQuery}
                    setActiveQuery={setActiveQuery}
                    loading={loading}
                    tickerInfoJson={tickerInfoJson}
                />
            </div>
            <div className='card'>
                <TradeOrderForm
                    tickerInfoJson={tickerInfoJson}
                    setPendingOrder={setPendingOrder}
                />
            </div>
        </div>
    );
}