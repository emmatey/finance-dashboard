export default function NewsCard({ news }) {
    return (
        <div className="card h-100">
            <div className="card-body">
                <h5 className="card-title">News</h5>
                {news.length > 0 ? (
                    <ul className="list-unstyled mb-0 overflow-auto" style={{ maxHeight: '400px' }}>
                        {news.map((n, i) => (
                            <li key={n.uuid ?? i} className="d-flex gap-2 align-items-start py-2 border-bottom">
                                {n.thumbnail && (
                                    <img src={n.thumbnail} alt="" className="object-fit-cover rounded-1 flex-shrink-0" style={{ width: '64px', height: '42px' }} />
                                )}
                                <div>
                                    <a href={n.link} target="_blank" rel="noreferrer" className="fw-semibold small d-block mb-1">
                                        {n.title}
                                    </a>
                                    <span className="text-muted small">
                                        {n.publisher}
                                        {n.providerPublishTime ? ` · ${new Date(n.providerPublishTime * 1000).toLocaleDateString()}` : ''}
                                    </span>
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-muted small mb-0">No news available.</p>
                )}
            </div>
        </div>
    )
}
