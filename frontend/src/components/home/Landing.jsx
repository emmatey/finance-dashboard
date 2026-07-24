import { useNavigate } from 'react-router-dom'
import Header from '@/components/Header.jsx'
import { Button } from '@/components/ui/button'

export default function Landing() {
    const navigate = useNavigate()

    return (
        <>
        <Header />
        <div className="flex flex-col items-center gap-4 px-6 py-24 text-center">
            <h1 className="font-heading text-3xl font-semibold">Welcome to Finance Dashboard</h1>
            <p className="max-w-md text-muted-foreground">
                Track your portfolio, research the market, and keep an eye on your finances in one place.
            </p>

            <div className="mt-4 flex items-center gap-3">
                <Button onClick={() => navigate('/auth?mode=login')}>Log in</Button>
                <Button variant="outline" onClick={() => navigate('/auth?mode=register')}>New here? Register</Button>
            </div>
        </div>
        </>
    )
}
