import { useEffect, useRef } from 'react';

export default function Scratchpad() {
    const testRef = useRef(null);

    testRef.current = setTimeout(() => {
        console.log("set timeout argument function body")
        console.log(testRef.current);
    }, 10)

    console.log("after set timeout is called.");
    console.log(testRef.current);

    return (
        <>
        </>
    )
}