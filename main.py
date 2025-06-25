# main.py
from database_manager import DatabaseManager
from event_manager import EventManager
from services import TransactionService, CategoryService
from ui import MainApplication
import tkinter as tk

if __name__ == "__main__":
    # 1. Inicializa o DatabaseManager (Singleton), garantindo que o DB e tabelas existam.
    db_manager = DatabaseManager()

    # 2. Inicializa o EventManager (para o padrão Observer).
    event_manager = EventManager()

    # 3. Inicializa os serviços (camada de lógica de negócio), passando o event_manager.
    transaction_service = TransactionService(event_manager)
    category_service = CategoryService(event_manager)

    # 4. Cria a aplicação principal Tkinter, passando os serviços e o event_manager.
    app = MainApplication(event_manager, transaction_service, category_service)

    # 5. Inicia o loop principal da aplicação.
    # Isso fará com que a janela seja exibida e a aplicação fique responsiva.
    app.mainloop()

    # 6. Ao fechar a aplicação, fecha a conexão com o banco de dados.
    # Isso é importante para liberar recursos.
    db_manager.close_connection()
    print("Aplicação encerrada. Conexão com o banco de dados fechada.")

