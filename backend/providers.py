from importlib import import_module

PROVIDER_MODULES = {
    "ollama": "ollama_interaction",
    "gemini": "gemini_interaction",
}

PROVIDERS = tuple(PROVIDER_MODULES)

_active_provider = None


def set_provider(name):
    global _active_provider
    if name not in PROVIDER_MODULES:
        raise ValueError(f"Provedor desconhecido: {name}. Opções: {', '.join(PROVIDERS)}")
    _active_provider = name


def get_provider():
    if _active_provider is None:
        raise RuntimeError("Nenhum provedor definido. Use --provider.")
    return _active_provider


def chat(payload, verbose=False, debug_model=False):
    module = import_module(PROVIDER_MODULES[get_provider()])
    return module.chat(payload, verbose=verbose, debug_model=debug_model)
