# event_manager.py

class EventManager:
    """
    Gerenciador de Eventos que implementa o padrão Publicador-Assinante (Observer).
    Permite que diferentes partes do sistema se comuniquem de forma desacoplada.
    """
    def __init__(self):
        self._listeners = {} # Dicionário para armazenar os ouvintes por tipo de evento

    def subscribe(self, event_type: str, listener):
        """
        Adiciona um ouvinte para um tipo de evento específico.
        Um ouvinte é uma função ou método que será chamado quando o evento ocorrer.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if listener not in self._listeners[event_type]: # Evita duplicatas
            self._listeners[event_type].append(listener)
            # print(f"Ouvinte '{listener.__name__}' inscrito para '{event_type}'.") # Opcional: para depuração

    def unsubscribe(self, event_type: str, listener):
        """
        Remove um ouvinte de um tipo de evento.
        """
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)
            # print(f"Ouvinte '{listener.__name__}' desinscrito de '{event_type}'.") # Opcional: para depuração

    def notify(self, event_type: str, data=None):
        """
        Notifica todos os ouvintes registrados para um determinado tipo de evento.
        Passa 'data' como argumento para a função ou método do ouvinte.
        """
        if event_type in self._listeners:
            # print(f"Notificando ouvintes para o evento '{event_type}'...") # Opcional: para depuração
            for listener in self._listeners[event_type]:
                try:
                    listener(data)
                except Exception as e:
                    print(f"Erro ao notificar ouvinte '{listener.__name__}' para evento '{event_type}': {e}")
        # else:
            # print(f"Nenhum ouvinte para o evento '{event_type}'.") # Opcional: para depuração