import { useEffect } from "react";
import { parseResponse } from "@/scripts/utils";
import { useAuth } from "@/context/AuthContext";


export default function useUserSummary() {
    const { user } = useAuth();

    useEffect(() => {
        
    }, []);
}