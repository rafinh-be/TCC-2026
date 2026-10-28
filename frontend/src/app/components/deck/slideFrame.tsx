import type { ReactNode } from "react";

export function SlideFrame({ title, children }: { title: string, children: ReactNode }) {
    return (
        <div className="flex h-full w-full flex-col gap-10 px-32 pb-12 pt-24">
            <h2 className="text-4xl font-semibold tracking-tight text-ink">{title}</h2>
            <div className="min-h-0 flex-1">{children}</div>
        </div>
    );
}
