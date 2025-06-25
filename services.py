# services.py
from repository import TransactionRepository, CategoryRepository
from models import Transaction, Category
from event_manager import EventManager
import datetime # Para validação e manipulação de datas

class TransactionService:
    """Serviço que gerencia a lógica de negócio das transações financeiras."""
    def __init__(self, event_manager: EventManager):
        self.repo = TransactionRepository()
        self.event_manager = event_manager

    def register_transaction(self, type: str, amount: float, date_str: str, description: str, category: str) -> bool:
        """
        Registra uma nova transação após validar os dados.
        Notifica ouvintes após sucesso.
        """
        try:
            # Validações de negócio
            if not isinstance(amount, (int, float)) or amount <= 0:
                print("Erro: Valor da transação deve ser numérico e positivo.")
                return False
            if type not in ["income", "expense"]:
                print("Erro: Tipo de transação inválido. Use 'income' ou 'expense'.")
                return False
            
            # Validação de formato de data
            try:
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("Erro: Formato de data inválido. Use AAAA-MM-DD.")
                return False

            transaction = Transaction(type, amount, date_str, description, category)
            if self.repo.add(transaction):
                # Notifica os observadores que uma nova transação foi adicionada
                self.event_manager.notify("transaction_added", transaction.to_dict())
                return True
            return False
        except ValueError as ve:
            print(f"Erro de validação ao registrar transação: {ve}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao registrar transação: {e}")
            return False

    def get_all_transactions(self) -> list[dict]:
        """Obtém todas as transações."""
        return self.repo.get_all()

    def get_transactions_for_report(self, start_date: str = None, end_date: str = None) -> list[dict]:
        """Obtém transações para relatórios, podendo filtrar por período."""
        if start_date and end_date:
            return self.repo.get_transactions_by_period(start_date, end_date)
        return self.repo.get_all()

    def delete_transaction(self, transaction_id: int) -> bool:
        """Exclui uma transação e notifica os observadores."""
        if self.repo.delete(transaction_id):
            self.event_manager.notify("transaction_deleted", {"id": transaction_id})
            return True
        return False


class CategoryService:
    """Serviço que gerencia a lógica de negócio das categorias."""
    def __init__(self, event_manager: EventManager):
        self.repo = CategoryRepository()
        self.event_manager = event_manager

    def add_category(self, name: str) -> bool:
        """Adiciona uma nova categoria após validação."""
        try:
            category = Category(name)
            if self.repo.add(category):
                self.event_manager.notify("category_added", category.to_dict())
                return True
            return False
        except ValueError as ve:
            print(f"Erro de validação ao adicionar categoria: {ve}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao adicionar categoria: {e}")
            return False

    def get_all_categories(self) -> list[dict]:
        """Obtém todas as categorias."""
        return self.repo.get_all()

    def update_category(self, category_id: int, new_name: str) -> bool:
        """Atualiza o nome de uma categoria."""
        try:
            updated_category = Category(new_name) # Usa o modelo para validação básica
            if self.repo.update(category_id, updated_category.name):
                self.event_manager.notify("category_updated", {"id": category_id, "name": new_name})
                return True
            return False
        except ValueError as ve:
            print(f"Erro de validação ao atualizar categoria: {ve}")
            return False
        except Exception as e:
            print(f"Erro inesperado ao atualizar categoria: {e}")
            return False

    def delete_category(self, category_id: int) -> bool:
        """Exclui uma categoria e notifica os observadores."""
        # TODO: Adicionar lógica para reatribuir transações desta categoria para 'Outros' antes de deletar
        if self.repo.delete(category_id):
            self.event_manager.notify("category_deleted", {"id": category_id})
            return True
        return False

