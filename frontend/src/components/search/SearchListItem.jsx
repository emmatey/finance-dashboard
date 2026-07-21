import { useNavigate } from 'react-router-dom';

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
        <li
            onMouseDown={onClick}
            className="flex cursor-pointer items-center gap-3 rounded-xl px-3 py-2 hover:bg-muted"
        >
            {type === "company" && <img className="size-7 shrink-0" src='/images/searchBar/companyIcon.svg' alt="" />}
            {type === "user" && <img className="size-7 shrink-0" src='/images/searchBar/userIcon.svg' alt="" />}
            {type === "news" && <img className="size-7 shrink-0" src='/images/searchBar/newsIcon.svg' alt="" />}
            <span className="truncate text-sm">{text}</span>
        </li>
    );
}
