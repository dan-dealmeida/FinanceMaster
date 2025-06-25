# reporting_strategy.py
from abc import ABC, abstractmethod
import pandas as pd # Biblioteca para manipulação de dados em DataFrames

class ReportStrategy(ABC):
    """Interface abstrata para todas as estratégias de relatório."""
    @abstractmethod
    def generate_report(self, transactions_data: list) -> str:
        """
        Método abstrato que as estratégias concretas devem implementar.
        Recebe uma lista de dicionários de transações e retorna uma string formatada do relatório.
        """
        pass

class CategoryReportStrategy(ReportStrategy):
    """Estratégia concreta para gerar um relatório de despesas/receitas por categoria."""
    def generate_report(self, transactions_data: list) -> str:
        if not transactions_data:
            return "Nenhuma transação para gerar relatório por categoria."
        
        # Converte a lista de dicionários para um DataFrame do pandas
        df = pd.DataFrame(transactions_data)
        
        # Garante que a coluna 'amount' é numérica
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        # Agrupa as transações por categoria e soma os valores
        # Separa receitas e despesas para um relatório mais claro
        income_by_category = df[df['type'] == 'income'].groupby('category')['amount'].sum().reset_index()
        expense_by_category = df[df['type'] == 'expense'].groupby('category')['amount'].sum().reset_index()

        report_str = "--- Relatório por Categoria ---\n\n"

        if not income_by_category.empty:
            report_str += "Receitas por Categoria:\n"
            report_str += income_by_category.to_string(index=False, header=False, float_format="%.2f") + "\n\n"
        
        if not expense_by_category.empty:
            report_str += "Despesas por Categoria:\n"
            report_str += expense_by_category.to_string(index=False, header=False, float_format="%.2f") + "\n"

        if income_by_category.empty and expense_by_category.empty:
            return "Nenhuma transação para gerar relatório por categoria."
            
        return report_str

class MonthlyReportStrategy(ReportStrategy):
    """Estratégia concreta para gerar um relatório de balanço mensal."""
    def generate_report(self, transactions_data: list) -> str:
        if not transactions_data:
            return "Nenhuma transação para gerar relatório mensal."
        
        df = pd.DataFrame(transactions_data)
        df['date'] = pd.to_datetime(df['date']) # Converte a coluna de data para datetime objects
        
        # Garante que a coluna 'amount' é numérica
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        df['month'] = df['date'].dt.to_period('M') # Extrai o mês e ano como Period objects

        # Calcula o saldo para cada transação (receita +ve, despesa -ve)
        df['signed_amount'] = df.apply(lambda row: row['amount'] if row['type'] == 'income' else -row['amount'], axis=1)

        # Agrupa por mês e soma os saldos
        monthly_balance = df.groupby('month')['signed_amount'].sum().reset_index()
        monthly_balance.columns = ['Mês', 'Balanço Total']
        
        # Formata a coluna 'Mês' para 'YYYY-MM'
        monthly_balance['Mês'] = monthly_balance['Mês'].astype(str)

        report_str = "--- Relatório Mensal ---\n\n"
        report_str += monthly_balance.to_string(index=False, float_format="%.2f") + "\n"
        
        return report_str

class ReportGenerator:
    """
    Contexto para o padrão Strategy. Utiliza uma estratégia de relatório para gerar relatórios.
    """
    def __init__(self, strategy: ReportStrategy):
        self._strategy = strategy # Define a estratégia inicial

    def set_strategy(self, strategy: ReportStrategy):
        """Permite trocar a estratégia de relatório em tempo de execução."""
        self._strategy = strategy

    def execute_report_generation(self, transactions_data: list) -> str:
        """Executa a geração do relatório usando a estratégia atualmente definida."""
        return self._strategy.generate_report(transactions_data)