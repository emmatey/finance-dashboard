import TradeSearch from './TradeInput/TradeSearch.jsx';
import TradeOrderForm from './TradeInput/TradeOrderForm.jsx';
import TradeHoldings from './TradeInput/TradeHoldings.jsx';
import TradeMarketData from './TradeInput/TradeMarketData.jsx';
import '@/styles/utilities.css';
import '@/styles/colors.css';

export default function TradeInput({
    activeQuery,
    setActiveQuery,
    loading,
    tickerInfoJson,
    setPendingOrder,
    viewController
}) {
    return (
        <div style={{ display: 'flex', gap: '16px' }}>
            <div className='card' style={{ zIndex: 1 }}>
                <TradeSearch
                    activeQuery={activeQuery}
                    setActiveQuery={setActiveQuery}
                    loading={loading}
                    tickerInfoJson={tickerInfoJson}
                />
                <hr />
                <TradeMarketData
                    activeQuery={activeQuery}
                    loading={loading}
                    tickerInfoJson={tickerInfoJson}
                />
            </div>

            <div className='card'>
                <TradeOrderForm
                    tickerInfoJson={tickerInfoJson}
                    setPendingOrder={setPendingOrder}
                    viewController={viewController}
                />
            </div>

            <div className='card'>
                <TradeHoldings tickerInfoJson={tickerInfoJson} />
            </div>
        </div>
    );
}