import '../../styles/utilities.css';

export default function SearchListItem({ text, setComponentRegistry }) {
    // One parent function which takes 
        // three functions for onclick go here, one for each type
        // of list item

    return (
        <li className="card" onClick={onClick} style={{ cursor: 'pointer', listStyle: 'none' }}>
            {text}
        </li>
    );
}
