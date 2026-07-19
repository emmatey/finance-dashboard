export default function HoldingsCard() {
    return (
        <div className="card h-100">
            <div className="card-body d-flex flex-column">
                <h5 className="card-title">Your Holdings</h5>
                <p className="text-muted small mb-0 flex-grow-1">Holdings data coming soon.</p>
                <div className="d-flex gap-2 mt-3">
                    <button className="btn btn-primary flex-grow-1">Buy</button>
                    <button className="btn btn-primary flex-grow-1">Sell</button>
                </div>
            </div>
        </div>
    )
}
