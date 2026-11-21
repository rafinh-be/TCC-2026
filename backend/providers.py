from importlib import import_module

PROVIDER_MODULES = {
    "ollama": "ollama_interaction",
    "gemini": "gemini_interaction",
}

EMBEDDING_MODULES = {
    "ollama": "local_embeddings",
    "gemini": "google_embeddings",
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


def chat(payload, verbose=False, debug_model=False, provider=None, think=None, model_variant=None, seed=None):
    module = import_module(PROVIDER_MODULES[provider or get_provider()])
    kwargs = {"think": think} if (provider or get_provider()) == "ollama" and think is not None else {}
    if model_variant is not None and (provider or get_provider()) == "ollama":
        kwargs["model_variant"] = model_variant
    if seed is not None and (provider or get_provider()) == "ollama":
        kwargs["seed"] = seed
    return module.chat(payload, verbose=verbose, debug_model=debug_model, **kwargs)

def chat_stream(payload, verbose=False, debug_model=False, provider=None, think=None, model_variant=None, seed=None):
    module = import_module(PROVIDER_MODULES[provider or get_provider()])
    kwargs = {"think": think} if (provider or get_provider()) == "ollama" and think is not None else {}
    if model_variant is not None and (provider or get_provider()) == "ollama":
        kwargs["model_variant"] = model_variant
    if seed is not None and (provider or get_provider()) == "ollama":
        kwargs["seed"] = seed
    return module.chat_stream(payload, verbose=verbose, debug_model=debug_model, **kwargs)

def create_embedding_model():
    module = import_module(EMBEDDING_MODULES[get_provider()])
    return module.create_embedding_model()

def embedding_signature():
    module = import_module(EMBEDDING_MODULES[get_provider()])
    return module.embedding_signature()
