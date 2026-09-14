import Header from '@/components/header/Header.jsx'
import HomeBody from '@/components/home/HomeBody.jsx'
import Landing from '@/components/home/Landing.jsx'
import { Spinner } from '@/components/ui/spinner.jsx'

import { useAuth } from '@/context/AuthContext.jsx'

export default function Home() {
    const { user } = useAuth();

    if (user === undefined) {
        return (
            <>
                <Header />
                <main className="flex min-h-screen items-center justify-center">
                    <Spinner className="size-8" />
                </main>
            </>
        );
    }

    return (
        <>
            {user ? <HomeBody /> : <Landing />}
        </>
    );
}
