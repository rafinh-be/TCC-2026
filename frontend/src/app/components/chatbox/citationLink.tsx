import Link from "next/link";

export function CitationLink({ href, title, children }: { href: string, title?: string, children: React.ReactNode }) {
    return (
        <Link
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            title={title}
            className="mx-0.5 inline-flex min-w-5 items-center justify-center rounded-full border border-line bg-primary-soft px-1.5 align-super text-xs leading-5 text-primary-ink no-underline hover:border-primary"
        >
            {children}
        </Link>
    );
}
