import { NewChatLink } from "./newChatLink";
import { DocumentLinks } from "./documentLinks";

export function Sidebar({ children, content }: { children?: React.ReactNode, content?: React.ReactNode }) {

    return (
        <div className="drawer lg:drawer-open">
            <input id="app-drawer" type="checkbox" className="drawer-toggle" />
            <div className="drawer-content flex h-dvh flex-col bg-page">
                <div className="px-3 pt-3">
                    <label htmlFor="app-drawer" aria-label="Abrir ou fechar menu" className="btn btn-square btn-ghost btn-sm text-ink-muted hover:bg-line">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" strokeLinejoin="round" strokeLinecap="round" strokeWidth="2" fill="none" stroke="currentColor" className="size-5"><path d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2z"></path><path d="M9 4v16"></path></svg>
                    </label>
                </div>
                <div className="flex min-h-0 flex-1 flex-col overflow-hidden">{content}</div>
            </div>

            <div className="drawer-side is-drawer-close:overflow-visible">
                <label htmlFor="app-drawer" aria-label="Fechar menu" className="drawer-overlay"></label>
                <div className="flex min-h-full flex-col border-r border-line bg-surface transition-[width] duration-200 ease-out is-drawer-close:w-16 is-drawer-open:w-64">
                    <div className="px-4 pt-5 pb-3 text-sm font-semibold tracking-tight text-primary-ink is-drawer-close:hidden">
                        Assistente Obstétrico
                    </div>
                    <ul className="menu w-full grow gap-1 px-2">
                        <li>
                            <NewChatLink>
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" strokeLinejoin="round" strokeLinecap="round" strokeWidth="2" fill="none" stroke="currentColor" className="size-4 text-primary"><path d="M12 5v14"></path><path d="M5 12h14"></path></svg>
                                <span className="is-drawer-close:hidden">Nova conversa</span>
                            </NewChatLink>
                        </li>
                        <DocumentLinks />
                        {children}
                    </ul>
                </div>
            </div>
        </div>
    )
}
