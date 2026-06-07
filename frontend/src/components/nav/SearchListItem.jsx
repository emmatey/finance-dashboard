import '../../styles/utilities.css';

export default function SearchListItem({ text, onClick }) {
    return (
        <li className="card" onClick={onClick} style={{ cursor: 'pointer', listStyle: 'none' }}>
            {text}
        </li>
    );
}
