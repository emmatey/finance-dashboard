import { useState, useEffect } from 'react'

export default function Home() {
  const [data, setData] = useState(null)

  useEffect(() => {
    // 1. Define the async function inside
    const fetchData = async () => {
      try {
        const res = await fetch("/api/scoreboard");
        const json = await res.json();
        setData(json);
      } catch (error) {
        console.error("Failed to fetch:", error);
      }
    };

    fetchData();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div>
      <h1>Scoreboard</h1>
      {/* 2. Use curly braces and <pre> for formatting */}
      <pre>
        {data ? JSON.stringify(data, null, 2) : "Loading..."}
      </pre>
    </div>
  )
}