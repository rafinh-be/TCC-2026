import { referenceNumbering } from "./referenceNumbering";
import { references } from "./references";

export function ReferencesFooter({ ids }: { ids: string[] }) {
    return (
        <p className="flex flex-wrap gap-x-4 gap-y-1 text-lg text-ink-muted">
            <span>Fontes:</span>
            {ids.map((id) => (
                <a key={id} href={references[id].url} target="_blank" rel="noreferrer" className="hover:text-primary hover:underline">
                    [{referenceNumbering.get(id)}] {references[id].short}
                </a>
            ))}
        </p>
    );
}
