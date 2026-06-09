import { useState } from 'react';
import '../../styles/utilities.css';

export default function SearchListItem({ object, type, image }) {
    /*
        A custom data list item.
            Props:
                object - The JSON object passed from <SearchBar /> which contains info
                    about a search result.
                type - 'company' or 'user' or 'news'. Decides onClick behavior. 
                image - A link to an image to display.
            Function:
                Parse object passed and render text, an image, b
    */
    let text = "...";

    let onClick = undefined;
    if (type === 'company') {
        onClick = () => (
            console.log("clicked me!")
            // redirect to research
        )
        let exchange = false;
        exchange = String(object.exchange).toLocaleLowerCase();
        if (exchange === "unknown") {
            text = `${object.ticker} - ${object.company_name}`;
        } else {
            text = `${object.ticker}: ${object.exchange} - ${object.company_name}`;
        }
    } else if (type === 'user') {
        onClick = () => (
            console.log("clicked me!")
            // redirect to user page with username as url
        )
        text = `Rank: ${object.rank} - Username: ${object.username}`;
    } else if (type === 'news') {
        onClick = () => (
            console.log("clicked me!")
            // Redirect to external news story. popup
        )
        text = `${object.publisher}: ${object.title}`;
    } else {
        throw new TypeError("Invalid 'type' prop in SearchListItem component.")
    };

    return (
        <li className="card" onClick={onClick} style={{ cursor: 'pointer', listStyle: 'none' }}>
            {text}
        </li>
    );
}
