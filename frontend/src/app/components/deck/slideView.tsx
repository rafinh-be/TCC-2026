import { ChunkingSlide } from "./chunkingSlide";
import { CompareSlide } from "./compareSlide";
import { ConceptsSlide } from "./conceptsSlide";
import { DemoSlide } from "./demoSlide";
import { EmbeddingMapSlide } from "./embeddingMapSlide";
import { MetricsSlide } from "./metricsSlide";
import { GridSlide } from "./gridSlide";
import { PipelineSlide } from "./pipelineSlide";
import { RetrievalCompareSlide } from "./retrievalCompareSlide";
import { ProviderCompareSlide } from "./providerCompareSlide";
import type { slideType } from "./slides";
import { SourcesSlide } from "./sourcesSlide";
import { TextSlide } from "./textSlide";
import { TitleSlide } from "./titleSlide";

export function SlideView({ slide, step }: { slide: slideType, step: number }) {
    switch (slide.kind) {
        case "title":
            return <TitleSlide slide={slide} />;
        case "text":
            return <TextSlide slide={slide} />;
        case "grid":
            return <GridSlide slide={slide} />;
        case "concepts":
            return <ConceptsSlide slide={slide} step={step} />;
        case "pipeline":
            return <PipelineSlide slide={slide} step={step} />;
        case "metrics":
            return <MetricsSlide slide={slide} />;
        case "demo":
            return <DemoSlide slide={slide} />;
        case "chunking":
            return <ChunkingSlide slide={slide} />;
        case "embeddingMap":
            return <EmbeddingMapSlide slide={slide} />;
        case "retrievalCompare":
            return <RetrievalCompareSlide slide={slide} />;
        case "providerCompare":
            return <ProviderCompareSlide slide={slide} />;
        case "compare":
            return <CompareSlide slide={slide} />;
        case "sources":
            return <SourcesSlide slide={slide} />;
    }
}
