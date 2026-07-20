import { formatNumber } from '@/scripts/utils.js'

export default function CompanyProfileCard({ profile }) {
    const profileData = profile?.[0];
    return (
        <div className="card h-100">
            <div className="card-body">
                <h5 className="card-title">Company Profile</h5>
                {profileData ? (
                    <>
                        <p className="small overflow-auto" style={{ maxHeight: '170px' }}>{profileData.company_desc ?? 'No description available.'}</p>
                        <table className="table table-sm mb-0">
                            <tbody>
                                {[
                                    ['Sector', profileData.sector],
                                    ['Industry', profileData.industry],
                                    ['Employees', profileData.employee_count != null ? formatNumber(profileData.employee_count, 0) : null],
                                    ['Website', profileData.website
                                        ? <a href={profileData.website} target="_blank" rel="noreferrer">{profileData.website}</a>
                                        : null],
                                ].map(([label, value]) => (
                                    <tr key={label}>
                                        <th className="text-muted fw-normal small" style={{ width: '40%' }}>{label}</th>
                                        <td className="small">{value ?? 'N/A'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </>
                ) : (
                    <p className="text-muted small mb-0">Loading…</p>
                )}
            </div>
        </div>
    )
}
