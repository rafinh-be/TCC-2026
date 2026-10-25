"use client";
import { createContext, useContext } from "react";

import type { documentTarget } from "@/utils/documentHref";

export const DocumentOpenerContext = createContext<((target: documentTarget) => void) | null>(null);

export function useDocumentOpener() {
    return useContext(DocumentOpenerContext);
}
