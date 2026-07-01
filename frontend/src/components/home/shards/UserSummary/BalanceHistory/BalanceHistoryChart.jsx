import useBalanceHistory from "./useBalanceHistory"


export default function BalanceHistoryChart({ snapshots }) {
    /*
        cash_balance: 10000
        ​​​grand_total: 10000
        ​​​portfolio_value: 0
        ​​​snap_datetime: "2026-06-08 05:08:50"
        ​​username: "emma"
    */
    const { loading, data, error, responseCode } = useBalanceHistory();

    return (
        
    )
}
