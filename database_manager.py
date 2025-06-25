# database_manager.py
import sqlite3

class DatabaseManager:
    """Gerencia uma única instância da conexão com o banco de dados SQLite (Singleton)."""
    _instance = None       # Armazena a única instância da classe
    _connection = None     # Armazena a conexão com o banco de dados

    def __new__(cls):
        # Garante que apenas uma instância de DatabaseManager seja criada
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            try:
                # Inicializa a conexão com o banco de dados apenas uma vez
                # O banco de dados será criado se não existir
                cls._connection = sqlite3.connect('finance_tracker.db')
                print("Conexão com o banco de dados estabelecida.")
                # Cria as tabelas necessárias se elas não existirem
                cls._instance._create_tables_if_not_exists()
            except sqlite3.Error as e:
                print(f"Erro ao conectar ou criar banco de dados: {e}")
                cls._instance = None # Invalida a instância se a conexão falhar
        return cls._instance

    def _create_tables_if_not_exists(self):
        """Cria as tabelas 'transactions' e 'categories' se elas ainda não existirem."""
        cursor = self._connection.cursor()
        # Tabela para transações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,          -- 'income' ou 'expense'
                amount REAL NOT NULL,        -- Valor da transação
                date TEXT NOT NULL,          -- Data no formato AAAA-MM-DD
                description TEXT,            -- Descrição da transação
                category TEXT                -- Categoria da transação
            )
        """)
        # Tabela para categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE    -- Nome único da categoria
            )
        """)
        self._connection.commit() # Confirma as alterações no esquema do banco de dados
        print("Tabelas verificadas/criadas.")

        # Adiciona uma categoria padrão se não existir (ex: 'Outros')
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", ("Outros",))
            self._connection.commit()
            print("Categoria 'Outros' adicionada (se não existia).")
        except sqlite3.IntegrityError:
            # A categoria 'Outros' já existe, ignore
            pass
        except sqlite3.Error as e:
            print(f"Erro ao adicionar categoria padrão: {e}")


    def get_connection(self):
        """Retorna a conexão ativa com o banco de dados."""
        return self._connection

    def close_connection(self):
        """Fecha a conexão com o banco de dados, se estiver aberta."""
        if self._connection:
            self._connection.close()
            self._connection = None
            print("Conexão com o banco de dados fechada.")
            