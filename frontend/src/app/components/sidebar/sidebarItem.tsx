type iconOptions = "home" | "settings" | "profile" | "notifications" | "message";

function getIcon(icon: iconOptions) {
    switch (icon) {
        case "settings":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" width="1.6em" height="1.6em" viewBox="0 0 24 24">
                    <path d="M0 0h24v24H0z" fill="none" />
                    <path fill="currentColor" fill-rule="evenodd" d="M13.354 8.75H4a.75.75 0 0 1 0-1.5h9.354a2.751 2.751 0 0 1 5.293 0H20a.75.75 0 0 1 0 1.5h-1.354a2.751 2.751 0 0 1-5.292 0M14.75 8a1.25 1.25 0 1 1 2.5 0a1.25 1.25 0 0 1-2.5 0m-4.103 8.75H20a.75.75 0 0 0 0-1.5h-9.353a2.751 2.751 0 0 0-5.293 0H4a.75.75 0 0 0 0 1.5h1.354a2.751 2.751 0 0 0 5.292 0M6.75 16a1.25 1.25 0 1 1 2.5 0a1.25 1.25 0 0 1-2.5 0" clip-rule="evenodd" />
                </svg>

            )
        case "home":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="0 0 24 24">
                    <path d="M0 0h24v24H0z" fill="none" />
                    <g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2">
                        <path d="M21 19v-6.733a4 4 0 0 0-1.245-2.9L13.378 3.31a2 2 0 0 0-2.755 0L4.245 9.367A4 4 0 0 0 3 12.267V19a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2" />
                        <path d="M9 15a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v6H9z" />
                    </g>
                </svg>
            )
        
        case "message":
            return (
                <svg xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="0 0 24 24">
                    <path d="M0 0h24v24H0z" fill="none" />
                    <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7.51 19.802a9 9 0 1 0-3.312-3.312l.003.005c.073.127.11.191.127.252c.016.057.02.108.016.168a1 1 0 0 1-.07.26l-.768 2.307l-.001.003c-.162.487-.243.73-.186.892c.05.142.163.253.304.304c.162.057.404-.023.889-.185l.006-.002l2.306-.769c.131-.044.198-.066.262-.07a.5.5 0 0 1 .167.017a1.3 1.3 0 0 1 .253.127z" />
                </svg>
            )
        default:
            return null;
    }
             
}

export function SidebarItem({ onClick, icon, label }: { onClick: () => void; icon: iconOptions; label: string }) {
    return (
        <li>
            <button className="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip={label} onClick={onClick}>
                {getIcon(icon)}
                <span className="is-drawer-close:hidden">{label}</span>
            </button>
        </li>
    );
}