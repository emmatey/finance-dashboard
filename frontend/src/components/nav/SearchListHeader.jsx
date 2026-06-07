import '../../styles/utilities.css';

export default function SearchListHeader({ label }) {
    return <li className='card' style={{ fontWeight: 'bold', listStyle: 'none', padding: '4px 0' }}>{label}</li>;
}
