# models.py

class Transaction:
    """Representa uma transação financeira (receita ou despesa)."""
    def __init__(self, type: str, amount: float, date: str, description: str = "", category: str = "Outros"):
        if type not in ["income", "expense"]:
            raise ValueError("Tipo de transação deve ser 'income' ou 'expense'.")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Valor da transação deve ser numérico e positivo.")
        # Simples validação de data, pode ser melhorado com datetime
        if not isinstance(date, str) or len(date) != 10 or date[4] != '-' or date[7] != '-':
             raise ValueError("Formato de data inválido. Use AAAA-MM-DD.")

        self.type = type
        self.amount = amount
        self.date = date
        self.description = description
        self.category = category

    def to_dict(self):
        """Converte o objeto Transaction para um dicionário."""
        return {
            "type": self.type,
            "amount": self.amount,
            "date": self.date,
            "description": self.description,
            "category": self.category
        }

class Category:
    """Representa uma categoria para transações financeiras."""
    def __init__(self, name: str):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nome da categoria não pode ser vazio.")
        self.name = name.strip()

    def to_dict(self):
        """Converte o objeto Category para um dicionário."""
        return {"name": self.name}