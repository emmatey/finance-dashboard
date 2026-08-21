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
            <CardContent class="grid">
                <a target="_blank" rel="noreferrer" ref="https://github.com/emmatey">Author</a>
                <a target="_blank" rel="noreferrer" ref="https://github.com/emmatey/finance-dashboard">Source Code</a>
            </CardContent>
        </Card>
    )
}