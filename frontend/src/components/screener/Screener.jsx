import Header from "../Header";
import Footer from "../Footer";

export default function Screener() {
    async function fetchScreenerData() {
        try {
            const url = "/api/screeners";
            const response = fetch(url, {
                method: "POST"  
            });

            const responseBody = await response.json();
            // 500 or 200
            if (response.status === 500) {
               console.error(responseBody);
               throw new Error(`Server responded with status: ${response.status}`); 
            }


        } catch (error) {
            console.error(error.message);
            return null;
        };
    }


    return (
        <>
        <p> Screener! </p>
        </>
    )
}
