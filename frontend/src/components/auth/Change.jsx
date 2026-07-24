import Header from '@/components/Header.jsx'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Change({ onSetMode }) {
    return (
        <div className="flex justify-center px-6 py-16">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle>Change username or password</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground">Coming soon.</p>
                </CardContent>
            </Card>
        </div>
    )
}
