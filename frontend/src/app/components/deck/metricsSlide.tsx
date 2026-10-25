import type { metricsSlideType } from "./slides";

export function MetricsSlide({ slide }: { slide: metricsSlideType }) {
    return (
        <div className="mx-auto flex h-full w-full max-w-4xl flex-col justify-center gap-6 px-10">
            <h2 className="text-4xl font-semibold tracking-tight text-ink">{slide.title}</h2>
            <p className="text-xl text-ink-muted">Os resultados serão exibidos aqui após a execução da avaliação.</p>
        </div>
    );
}
