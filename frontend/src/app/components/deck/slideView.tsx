import { DemoSlide } from "./demoSlide";
import { MetricsSlide } from "./metricsSlide";
import { PipelineSlide } from "./pipelineSlide";
import type { slideType } from "./slides";
import { TextSlide } from "./textSlide";

export function SlideView({ slide, step }: { slide: slideType, step: number }) {
    switch (slide.kind) {
        case "text":
            return <TextSlide slide={slide} />;
        case "pipeline":
            return <PipelineSlide slide={slide} step={step} />;
        case "metrics":
            return <MetricsSlide slide={slide} />;
        case "demo":
            return <DemoSlide slide={slide} />;
    }
}
