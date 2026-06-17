import Header from "../../Header";
import Footer from "../../Footer";
import { parseResponse } from "../../../scripts/utils";


export default function ScreenerCard({ title, data }) {
    // 'data' is a list of objects
    const headers = Object.keys(data[0]);

    return (
        <>
        <div className="card">
            <h4>{title}</h4>
            <table>
                <tr>
                { headers.map((header) => (<th>{header}</th>)) }
                </tr>
                
                { data.map((obj) => (
                    <tr>
                        {headers.map((header) => (
                            <td>{obj?.[header] || null} </td>
                        ))}
                    </tr>
                )) }
            </table>
        </div>
        </>
    )
}