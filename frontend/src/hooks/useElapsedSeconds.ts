"use client";
import { useEffect, useState } from "react";

export function useElapsedSeconds(startedAt: number | null, finishedAt: number | null) {
    const [now, setNow] = useState(0);

    useEffect(() => {
        if (startedAt === null || finishedAt !== null) return;
        const interval = setInterval(() => setNow(Date.now()), 100);
        return () => clearInterval(interval);
    }, [startedAt, finishedAt]);

    if (startedAt === null) return null;
    const end = finishedAt ?? Math.max(now, startedAt);
    return (end - startedAt) / 1000;
}
