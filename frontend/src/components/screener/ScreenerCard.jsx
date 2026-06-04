import Header from "../Header";
import Footer from "../Footer";
import { parseResponse } from "../../scripts/utils";
import { useEffect, useState } from "react";

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
                
              
            </table>
        </div>
        </>
    )
}