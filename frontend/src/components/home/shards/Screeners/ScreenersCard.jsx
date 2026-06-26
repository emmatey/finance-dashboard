export default function ScreenersCard({ title, data }) {
    if (!data?.length) return null;

    const headers = Object.keys(data[0]);

    return (
        <div className="card">
            <h4>{title}</h4>
            <table>
                <thead>
                    <tr>
                        {headers.map((header) => (<th key={header}>{header}</th>))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((obj, i) => (
                        <tr key={i}>
                            {headers.map((header) => (
                                <td key={header}>{obj?.[header] ?? null}</td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
