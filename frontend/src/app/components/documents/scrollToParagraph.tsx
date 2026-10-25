"use client";
import { useEffect } from "react";

import { paragraphElementId } from "@/utils/rehypeParagraphMarks";

export function ScrollToParagraph({ index }: { index: number }) {
    useEffect(() => {
        document.getElementById(paragraphElementId(index))?.scrollIntoView({ block: "center" });
    }, [index]);

    return null;
}
