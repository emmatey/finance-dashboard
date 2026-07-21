import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { formatNumber } from '@/scripts/utils.js'

export default function CompanyProfileCard({ profile }) {
    const profileData = profile?.[0];
    return (
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Company Profile</CardTitle>
            </CardHeader>
            <CardContent>
                {profileData ? (
                    <>
                        <p className="mb-3 max-h-[170px] overflow-auto text-sm text-muted-foreground">
                            {profileData.company_desc ?? 'No description available.'}
                        </p>
                        <div className="space-y-1.5 text-sm">
                            {[
                                ['Sector', profileData.sector],
                                ['Industry', profileData.industry],
                                ['Employees', profileData.employee_count != null ? formatNumber(profileData.employee_count, 0) : null],
                                ['Website', profileData.website
                                    ? <a href={profileData.website} target="_blank" rel="noreferrer" className="text-primary underline underline-offset-4">{profileData.website}</a>
                                    : null],
                            ].map(([label, value]) => (
                                <div key={label} className="flex items-center justify-between gap-2 border-b border-border py-1 last:border-0">
                                    <span className="text-muted-foreground">{label}</span>
                                    <span>{value ?? 'N/A'}</span>
                                </div>
                            ))}
                        </div>
                    </>
                ) : (
                    <div className="flex items-center justify-center py-8">
                        <Spinner className="size-5" />
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
