import streamlit as st
import json
from websockets.sync.client import connect

# Configuração da página
st.set_page_config(
    page_title="Agente Obstétrico - TCC",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada para visual moderno
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

WS_URL = "ws://127.0.0.1:8000/ws/chat"

# Inicialização de Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "historico_conversa" not in st.session_state:
    st.session_state.historico_conversa = []

# Barra Lateral (Sidebar)
with st.sidebar:
    st.title("🩺 Agente Obstétrico")
    st.caption("Sistema RAG via WebSocket")
    st.markdown("---")
    
    # Verificação de status do WebSocket
    try:
        with connect(WS_URL, open_timeout=2) as ws_check:
            st.success("🟢 WebSocket Conectado (`/ws/chat`)")
    except Exception:
        st.error("🔴 WebSocket Desconectado (`ws://127.0.0.1:8000/ws/chat`)")

    st.markdown("---")
    st.markdown("### ℹ️ Sobre")
    st.info(
        "Este agente utiliza RAG (Retrieval-Augmented Generation) ancorado em base de evidências obstétricas "
        "locais para orientar dúvidas clínicas via WebSocket."
    )
    
    st.markdown("---")
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.historico_conversa = []
        st.rerun()

# Conteúdo Principal
st.markdown('<div class="main-header">Assistente de Obstetrícia & Ginecologia</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">TCC 2026 — Dúvidas clínicas e orientações baseadas em evidências</div>', unsafe_allow_html=True)

# Renderiza histórico de mensagens na UI
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🩺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Caixa de Entrada do Usuário
if user_prompt := st.chat_input("Digite sua dúvida médica ou mensagem..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("Consultando base de evidências via WebSocket..."):
            try:
                with connect(WS_URL, open_timeout=5) as websocket:
                    payload = {
                        "message": user_prompt,
                        "historico_conversa": st.session_state.historico_conversa
                    }
                    websocket.send(json.dumps(payload, ensure_ascii=False))
                    
                    response_raw = websocket.recv()
                    data = json.loads(response_raw)
                    
                    assistant_response = data.get("assistant", "Sem resposta do assistente.")
                    
                    if "historico_conversa" in data:
                        st.session_state.historico_conversa = data["historico_conversa"]
                    
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                error_msg = f"❌ Erro na comunicação WebSocket com `ws://127.0.0.1:8000/ws/chat`: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
