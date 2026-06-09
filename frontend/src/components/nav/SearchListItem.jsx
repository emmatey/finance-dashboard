import '../../styles/utilities.css';

export default function SearchListItem({ object, type }) {
    // One parent function which takes 
        // three functions for onclick go here, one for each type
        // of list item

    function onClick() {
        let a = 1;
    }

    return (
        <li className="card" onClick={onClick} style={{ cursor: 'pointer', listStyle: 'none' }}>
            test
        </li>
    );
}
