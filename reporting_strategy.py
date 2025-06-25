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

    @abstractmethod
    def get_report_data(self, transactions_data: list) -> pd.DataFrame:
        """
        Método abstrato para retornar os dados processados para plotagem.
        Recebe uma lista de dicionários de transações e retorna um DataFrame do pandas.
        """
        pass


class CategoryReportStrategy(ReportStrategy):
    """Estratégia concreta para gerar um relatório de despesas/receitas por categoria e dados para gráfico."""
    def generate_report(self, transactions_data: list) -> str:
        if not transactions_data:
            return "Nenhuma transação para gerar relatório por categoria."
        
        df = pd.DataFrame(transactions_data)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

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

    def get_report_data(self, transactions_data: list) -> pd.DataFrame:
        """
        Retorna um DataFrame com a soma de receitas e despesas por categoria,
        formatado para plotagem.
        """
        if not transactions_data:
            return pd.DataFrame(columns=['Categoria', 'Tipo', 'Valor'])

        df = pd.DataFrame(transactions_data)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        # Prepara dados para gráfico: receitas e despesas como valores positivos/negativos
        # Agrupamento separado para receitas e despesas
        income_df = df[df['type'] == 'income'].groupby('category')['amount'].sum().reset_index()
        income_df['type'] = 'Receita'

        expense_df = df[df['type'] == 'expense'].groupby('category')['amount'].sum().reset_index()
        expense_df['type'] = 'Despesa'
        
        # Concatena e renomeia colunas para consistência
        combined_df = pd.concat([income_df, expense_df])
        combined_df.columns = ['Categoria', 'Valor', 'Tipo']
        
        return combined_df

class MonthlyReportStrategy(ReportStrategy):
    """Estratégia concreta para gerar um relatório de balanço mensal e dados para gráfico."""
    def generate_report(self, transactions_data: list) -> str:
        if not transactions_data:
            return "Nenhuma transação para gerar relatório mensal."
        
        df = pd.DataFrame(transactions_data)
        df['date'] = pd.to_datetime(df['date']) # Converte a coluna de data para datetime objects
        
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        df['month'] = df['date'].dt.to_period('M') # Extrai o mês e ano como Period objects

        df['signed_amount'] = df.apply(lambda row: row['amount'] if row['type'] == 'income' else -row['amount'], axis=1)

        monthly_balance = df.groupby('month')['signed_amount'].sum().reset_index()
        monthly_balance.columns = ['Mês', 'Balanço Total']
        
        monthly_balance['Mês'] = monthly_balance['Mês'].astype(str)

        report_str = "--- Relatório Mensal ---\n\n"
        report_str += monthly_balance.to_string(index=False, float_format="%.2f") + "\n"
        
        return report_str

    def get_report_data(self, transactions_data: list) -> pd.DataFrame:
        """
        Retorna um DataFrame com o balanço mensal, formatado para plotagem.
        """
        if not transactions_data:
            return pd.DataFrame(columns=['Mês', 'Balanço Total'])

        df = pd.DataFrame(transactions_data)
        df['date'] = pd.to_datetime(df['date'])
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
        df['month'] = df['date'].dt.to_period('M').astype(str) # Convert to string directly for plotting x-axis

        df['signed_amount'] = df.apply(lambda row: row['amount'] if row['type'] == 'income' else -row['amount'], axis=1)

        monthly_balance = df.groupby('month')['signed_amount'].sum().reset_index()
        monthly_balance.columns = ['Mês', 'Balanço Total']
        
        # Sort by month to ensure correct plotting order
        monthly_balance['Mês_Sort'] = pd.to_datetime(monthly_balance['Mês'])
        monthly_balance = monthly_balance.sort_values(by='Mês_Sort').drop(columns='Mês_Sort')

        return monthly_balance


class ReportGenerator:
    """
    Contexto para o padrão Strategy. Utiliza uma estratégia de relatório para gerar relatórios e dados para plotagem.
    """
    def __init__(self, strategy: ReportStrategy):
        self._strategy = strategy # Define a estratégia inicial

    def set_strategy(self, strategy: ReportStrategy):
        """Permite trocar a estratégia de relatório em tempo de execução."""
        self._strategy = strategy

    def execute_report_generation(self, transactions_data: list) -> str:
        """Executa a geração do relatório textual usando a estratégia atualmente definida."""
        return self._strategy.generate_report(transactions_data)

    def get_report_data(self, transactions_data: list) -> pd.DataFrame:
        """Obtém os dados processados para plotagem usando a estratégia atualmente definida."""
        return self._strategy.get_report_data(transactions_data)