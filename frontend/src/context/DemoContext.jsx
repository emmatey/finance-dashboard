import { createContext, useContext, useEffect, useState } from "react";
import { parseResponse } from "@/scripts/utils";

const DemoContext = createContext(false);

async function demoModeRequest() {
    const response = await fetch("/api/internal/demo", {
        method: "GET"
    });
    return await parseResponse(response);
}

export function DemoProvider({ children }) {
    const [demoMode, setDemoMode] = useState(false);

    async function parseDemoModeRequestResponse() {
        try {
            const res = await demoModeRequest();
            setDemoMode(Boolean(res?.demo_mode));
        } catch (error) {
            setDemoMode(false);
        }
    }

    useEffect(() => {
        parseDemoModeRequestResponse();
    }, []);

    return (
        <DemoContext.Provider value={demoMode}>
            {children}
        </DemoContext.Provider>
    );
}

export const useDemo = () => useContext(DemoContext);