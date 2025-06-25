# repository.py
import sqlite3
from database_manager import DatabaseManager
from models import Transaction, Category # Importa as classes de modelo

class TransactionRepository:
    """Gerencia as operações de persistência para transações financeiras."""
    def __init__(self):
        self.db_manager = DatabaseManager() # Obtém a instância Singleton do gerenciador de DB
        self.conn = self.db_manager.get_connection()

    def add(self, transaction: Transaction) -> bool:
        """Adiciona uma nova transação ao banco de dados."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (type, amount, date, description, category)
                VALUES (?, ?, ?, ?, ?)
            """, (transaction.type, transaction.amount, transaction.date,
                  transaction.description, transaction.category))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao adicionar transação ao banco de dados: {e}")
            return False

    def get_all(self) -> list[dict]:
        """Retorna todas as transações, ordenadas da mais recente para a mais antiga."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, type, amount, date, description, category FROM transactions ORDER BY date DESC")
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                "id": row[0], "type": row[1], "amount": row[2],
                "date": row[3], "description": row[4], "category": row[5]
            })
        return transactions

    def get_transactions_by_period(self, start_date: str, end_date: str) -> list[dict]:
        """Retorna transações dentro de um período específico."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, type, amount, date, description, category
            FROM transactions
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """, (start_date, end_date))
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                "id": row[0], "type": row[1], "amount": row[2],
                "date": row[3], "description": row[4], "category": row[5]
            })
        return transactions

    def delete(self, transaction_id: int) -> bool:
        """Exclui uma transação pelo ID."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            self.conn.commit()
            return cursor.rowcount > 0 # Retorna True se alguma linha foi afetada (excluída)
        except sqlite3.Error as e:
            print(f"Erro ao excluir transação: {e}")
            return False

class CategoryRepository:
    """Gerencia as operações de persistência para categorias."""
    def __init__(self):
        self.db_manager = DatabaseManager() # Obtém a instância Singleton do gerenciador de DB
        self.conn = self.db_manager.get_connection()

    def add(self, category: Category) -> bool:
        """Adiciona uma nova categoria ao banco de dados."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (category.name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Erro: Categoria '{category.name}' já existe.")
            return False
        except sqlite3.Error as e:
            print(f"Erro ao adicionar categoria: {e}")
            return False

    def get_all(self) -> list[dict]:
        """Retorna todas as categorias."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name ASC")
        rows = cursor.fetchall()
        categories = []
        for row in rows:
            categories.append({"id": row[0], "name": row[1]})
        return categories

    def update(self, category_id: int, new_name: str) -> bool:
        """Atualiza o nome de uma categoria existente."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, category_id))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            print(f"Erro: Categoria com nome '{new_name}' já existe.")
            return False
        except sqlite3.Error as e:
            print(f"Erro ao atualizar categoria: {e}")
            return False

    def delete(self, category_id: int) -> bool:
        """Exclui uma categoria pelo ID."""
        try:
            cursor = self.conn.cursor()
            # Opcional: verificar se existem transações associadas a esta categoria
            # e lidar com elas (ex: definir categoria para 'Outros' ou impedir exclusão)
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erro ao excluir categoria: {e}")
            return False