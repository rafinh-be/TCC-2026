"use client";
import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

let resolvePendingTransition: (() => void) | null = null;

export function NewChatLink({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (pathname !== "/") return;
        resolvePendingTransition?.();
        resolvePendingTransition = null;
    }, [pathname]);

    const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (pathname !== "/chat" || !document.startViewTransition) return;
        e.preventDefault();
        document.startViewTransition(
            () => new Promise<void>((resolve) => {
                resolvePendingTransition = resolve;
                router.push("/");
            })
        );
    };

    return (
        <Link
            href="/"
            onClick={handleClick}
            className="is-drawer-close:tooltip is-drawer-close:tooltip-right text-ink hover:bg-primary-soft"
            data-tip="Nova conversa"
        >
            {children}
        </Link>
    );
}
