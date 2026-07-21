import { adjustPendingOrder } from '@/scripts/utils';
import { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';


export default function TradeOrderForm({ tickerInfoJson, setPendingOrder, viewController }) {
    const [txType, setTxType] = useState("buy");
    const [txQty, setTxQty] = useState(0);
    const [txUnit, setTxUnit] = useState('shares');

    let currentPrice = null;
    let ticker = null;
    let qtyOwned = null;
    let cashBalance = null;
    if (tickerInfoJson) {
        currentPrice = tickerInfoJson.current_price;
        ticker = tickerInfoJson.ticker;
        qtyOwned = tickerInfoJson.qty_owned;
        cashBalance = tickerInfoJson.cash_balance;
    };

    function checkCanAfford(txDollarQty, cashBalance) {
        if (Number(cashBalance) >= Number(txDollarQty)) {
            return true;
        } else {
            return false
        };
    }
    function checkCanSell(txShareQty) {
        if (Number(qtyOwned) >= Number(txShareQty)) {
            return true;
        } else {
            return false
        };
    }

    function handleSubmit(event) {
        event.preventDefault()

        // Block submission if there's no valid quantity or active price
        if (!txQty || !currentPrice) {
            console.error(`No valid quantity or active price.`);
            return;
        };

        const [txDollarQty, txShareQty] = adjustPendingOrder(txUnit, Number(txQty), currentPrice)

        if (txType === 'sell') {
            if (!checkCanSell(txShareQty)) {
                toast.error("Unable to make transaction! You own less shares than you're attempting to sell!");
                return;
            };
        } else if (txType === 'buy') {
            if (!checkCanAfford(txDollarQty, cashBalance)) {
                toast.error("Unable to make transaction! You cannot afford this transaction!")
                return;
            };
        }

        setPendingOrder({
            'txTicker': ticker,
            'txType': txType,
            'txShareQty': txShareQty,
            'txDollarQty': txDollarQty,
            'txUnit': txUnit
        })
        viewController['setShowConfirmationScreen'](true);
        viewController['setShowInput'](false);
    }

    return (
        <form name='tradeTransactForm' onSubmit={handleSubmit} className="flex flex-col gap-4">
            <ToggleGroup
                type="single"
                variant="outline"
                spacing={0}
                value={txType}
                onValueChange={(value) => value && setTxType(value)}
                className="w-full"
            >
                <ToggleGroupItem value="buy" className="flex-1">Buy</ToggleGroupItem>
                <ToggleGroupItem value="sell" className="flex-1">Sell</ToggleGroupItem>
            </ToggleGroup>

            <div className="flex items-center gap-2">
                <Input
                    type='number'
                    name='qtyInput'
                    placeholder={txUnit === 'shares' ? 'Qty of Shares' : 'Amount in USD'}
                    value={txQty}
                    onChange={(e) => setTxQty(e.target.value)}
                    min={txUnit === 'shares' ? '0.1' : '1'}
                    step={txUnit === 'shares' ? '0.1' : '1'}
                    className="flex-1"
                />

                <Select name='qtyUnit' value={txUnit} onValueChange={setTxUnit}>
                    <SelectTrigger>
                        <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value='shares'>Shares</SelectItem>
                        <SelectItem value='dollars'>Dollars</SelectItem>
                    </SelectContent>
                </Select>
            </div>

            <Button type='submit' disabled={!tickerInfoJson}>Submit</Button>
            <Toaster />
        </form>
    );
}