import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"


export default function ScreenersTable({ data }) {
    //from - {
    //screener_name: [{
    //    screener_name: str,
    //    rank: int,
    //    ticker: str,
    //    company_name: str,
    //    current_price: float,
    //    prev_close: float,
    //    price_change_pct: float,
    //    market_cap: float,
    //    todays_volume: int,
    //    three_month_avg_volume: int,
    //    volume_change_pct: float
    //}]
    return (
        <>
            {
                data.map((companyObj) => {
                    return (
                        <div key={companyObj.ticker}>{companyObj.company_name}</div>
                    )
                })
            }
        </>
    )
}