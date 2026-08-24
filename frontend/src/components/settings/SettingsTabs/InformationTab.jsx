import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router-dom";


export default function InformationTab() {

    return (
        <Card>
            <CardHeader>
                <CardTitle>
                    Learn More About the Project
                </CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2 text-sm">
                <a className="text-muted-foreground hover:text-foreground flex items-center justify-between rounded-sm px-2 py-1 transition-colors hover:bg-accent" target="_blank" rel="noreferrer" href="https://github.com/emmatey">
                    <span>Author</span>
                    <span className="text-xs">↗</span>
                </a>
                <a className="text-muted-foreground hover:text-foreground flex items-center justify-between rounded-sm px-2 py-1 transition-colors hover:bg-accent" target="_blank" rel="noreferrer" href="https://github.com/emmatey/finance-dashboard">
                    <span>Source Code</span>
                    <span className="text-xs">↗</span>
                </a>
            </CardContent>
        </Card>
    )
}