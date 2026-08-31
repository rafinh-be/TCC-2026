"use client";

import { useEffect, useState } from "react";

export default function Home() {
    const [data, setData] = useState<{ message: string } | null>(null);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/api/data")
            .then((res) => res.json())
            .then((data) => setData(data));
    }, []);

    return (
        <section>
            <h1>About us!</h1>
            <p>Welcome</p>

            <h1>Recebi isso aqui { data ? data.message : "loading..."}</h1>
        </section>
    )
}