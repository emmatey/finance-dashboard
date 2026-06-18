import TradeSearch from './TradeSearch.jsx';
import TradeOrderForm from './TradeOrderForm.jsx';
import TradeHoldings from './TradeHoldings.jsx';
import TradeMarketData from './TradeMarketData.jsx';
import '../../../../styles/utilities.css';
import '../../../../styles/colors.css';

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