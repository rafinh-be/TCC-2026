"""
Interface de Usuário (Frontend) em Streamlit - Agente Obstétrico RAG.

Esta aplicação fornece a interface web interativa para médicos e profissionais de saúde
interagirem com o sistema de IA em tempo real via WebSocket (ws://127.0.0.1:8000/ws/chat).
"""

import streamlit as st
import json
from websockets.sync.client import connect

# -----------------------------------------------------------------------------
# Configuração Global da Página (Título, Ícone e Layout)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Agente Obstétrico - TCC",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Estilização CSS Personalizada para Interface Moderna
# -----------------------------------------------------------------------------
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

# URL do endpoint WebSocket no backend FastAPI
WS_URL = "ws://127.0.0.1:8000/ws/chat"

# -----------------------------------------------------------------------------
# Inicialização das Variáveis no Session State do Streamlit
# -----------------------------------------------------------------------------
# Mensagens exibidas na interface do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Histórico estruturado mantido para envio no payload da API/WebSocket
if "historico_conversa" not in st.session_state:
    st.session_state.historico_conversa = []

# -----------------------------------------------------------------------------
# Barra Lateral (Sidebar)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("🩺 Agente Obstétrico")
    st.caption("Sistema RAG via WebSocket")
    st.markdown("---")
    
    # Teste de conexão ativa com o servidor WebSocket do backend
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
    # Botão para reiniciar a conversa e limpar o estado
    if st.button("🗑️ Limpar Conversa", use_container_width=True):
        st.session_state.messages = []
        st.session_state.historico_conversa = []
        st.rerun()

# -----------------------------------------------------------------------------
# Cabeçalho Principal da Aplicação
# -----------------------------------------------------------------------------
st.markdown('<div class="main-header">Assistente de Obstetrícia & Ginecologia</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">TCC 2026 — Dúvidas clínicas e orientações baseadas em evidências</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Exibição do Histórico de Mensagens no Chat
# -----------------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🩺"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# -----------------------------------------------------------------------------
# Campo de Entrada de Mensagem (Chat Input) e Envio via WebSocket
# -----------------------------------------------------------------------------
if user_prompt := st.chat_input("Digite sua dúvida médica ou mensagem..."):
    # Adiciona a mensagem do usuário à lista de exibição local
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_prompt)

    # Bloco do assistente com spinner de carregamento
    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("Consultando base de evidências via WebSocket..."):
            try:
                # Conecta ao servidor WebSocket do backend para enviar a mensagem
                with connect(WS_URL, open_timeout=5) as websocket:
                    payload = {
                        "message": user_prompt,
                        "historico_conversa": st.session_state.historico_conversa
                    }
                    websocket.send(json.dumps(payload, ensure_ascii=False))
                    
                    # Aguarda a resposta do servidor
                    response_raw = websocket.recv()
                    data = json.loads(response_raw)
                    
                    assistant_response = data.get("assistant", "Sem resposta do assistente.")
                    
                    # Atualiza o histórico de conversas compartilhado no Session State
                    if "historico_conversa" in data:
                        st.session_state.historico_conversa = data["historico_conversa"]
                    
                    # Renderiza a resposta no chat
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            except Exception as e:
                # Trata erros de conexão WebSocket exibindo mensagem de aviso amigável
                error_msg = f"❌ Erro na comunicação WebSocket com `ws://127.0.0.1:8000/ws/chat`: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

