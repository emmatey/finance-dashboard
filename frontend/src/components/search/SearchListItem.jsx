import { useNavigate } from 'react-router-dom';
import '../../styles/utilities.css';

export default function SearchListItem({ object, type }) {
    /*
        A custom data list item.
            Props:
                object - The JSON object passed from <SearchBar /> which contains info
                    about a search result.
                type - 'company' or 'user' or 'news'. Decides onClick behavior. 
    */
    let navigate = useNavigate();
    let text = "...";

    let onClick = undefined;
    if (type === 'company') {
        onClick = () => (
            navigate(`/research?ticker=${object.ticker}`)
        )
        let exchange = false;
        exchange = String(object.exchange).toLocaleLowerCase();
        if (exchange === "unknown") {
            text = `${object.ticker} - ${object.company_name}`;
        } else {
            text = `${object.ticker}: ${object.exchange} - ${object.company_name}`;
        }
    } else if (type === 'user') {
        onClick = () => navigate(`/user/${object.username}`)
        text = `User: ${object.username} - Rank: ${object.rank ?? 'N/A'}`;
    } else if (type === 'news') {
        onClick = () => window.open(object.link, '_blank')
        text = `${object.publisher}: ${object.title}`;
    } else {
        throw new TypeError("Invalid 'type' prop in SearchListItem component.")
    };

    return (
        <li className="card" onMouseDown={onClick} style={{ cursor: 'pointer', listStyle: 'none' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {type === "company" && <img className="thumbnail" src='/images/searchBar/companyIcon.svg'/>}
                {type === "user" && <img className="thumbnail" src='/images/searchBar/userIcon.svg'/>}
                {type === "news" && <img className="thumbnail" src='/images/searchBar/newsIcon.svg'/>}
            </div>
            <span>{text}</span>
        </li>
    );
}
