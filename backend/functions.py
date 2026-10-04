"""
Módulo de Funções Auxiliares do Backend.

Este módulo contém funções utilitárias para comandos executados durante o chat.
"""

def clear(historico_conversa):
    """
    Reseta o histórico da conversa, limpando todas as mensagens anteriores.
    
    :param historico_conversa: Lista com o histórico atual.
    :return: String "continue" indicando que a execução do comando foi concluída.
    """
    historico_conversa.clear()
    return "continue"