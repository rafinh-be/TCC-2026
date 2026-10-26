const sizeClassNames = {
    large: { list: "gap-4", card: "gap-5 px-6 py-5 text-xl", badge: "size-9 text-base" },
    compact: { list: "gap-3", card: "gap-4 px-4 py-3 text-base", badge: "size-7 text-sm" },
};

export function PointCards({ points, size }: { points: string[], size: keyof typeof sizeClassNames }) {
    const classNames = sizeClassNames[size];

    return (
        <ol className={`flex flex-col ${classNames.list}`}>
            {points.map((point, index) => (
                <li key={point} className={`flex items-start rounded-2xl border border-line bg-surface text-ink-muted ${classNames.card}`}>
                    <span className={`flex shrink-0 items-center justify-center rounded-full bg-primary-soft font-medium text-primary-ink ${classNames.badge}`}>
                        {index + 1}
                    </span>
                    <span>{point}</span>
                </li>
            ))}
        </ol>
    );
}
