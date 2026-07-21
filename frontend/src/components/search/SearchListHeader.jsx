export default function SearchListHeader({ text }) {
    return (
        <li className="px-3 py-1.5 text-xs font-semibold text-muted-foreground">
            {text}
        </li>
    );
}