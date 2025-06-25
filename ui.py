# ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from services import TransactionService, CategoryService
from event_manager import EventManager
from reporting_strategy import ReportGenerator, CategoryReportStrategy, MonthlyReportStrategy

class MainApplication(tk.Tk):
    """
    Classe principal da aplicação que gerencia a janela e as diferentes views (telas).
    """
    def __init__(self, event_manager: EventManager, transaction_service: TransactionService, category_service: CategoryService):
        super().__init__()
        self.event_manager = event_manager
        self.transaction_service = transaction_service
        self.category_service = category_service

        self.title("Sistema de Gerenciamento Financeiro Pessoal")
        self.geometry("900x600") # Tamanho inicial da janela
        self.create_widgets()
        self.current_view = None
        self.show_home_view()

    def create_widgets(self):
        """Cria o menu de navegação lateral."""
        self.sidebar_frame = ttk.Frame(self, width=150, padding="10", relief="raised")
        self.sidebar_frame.pack(side="left", fill="y")

        ttk.Button(self.sidebar_frame, text="Início", command=self.show_home_view).pack(pady=5, fill="x")
        ttk.Button(self.sidebar_frame, text="Registrar Transação", command=self.show_transaction_entry_view).pack(pady=5, fill="x")
        ttk.Button(self.sidebar_frame, text="Ver Extrato", command=self.show_transaction_list_view).pack(pady=5, fill="x")
        ttk.Button(self.sidebar_frame, text="Categorias", command=self.show_category_manager_view).pack(pady=5, fill="x")
        ttk.Button(self.sidebar_frame, text="Relatórios", command=self.show_report_view).pack(pady=5, fill="x")

        self.content_frame = ttk.Frame(self, padding="10")
        self.content_frame.pack(side="right", fill="both", expand=True)

    def switch_view(self, new_view_class):
        """Troca a view atualmente exibida na área de conteúdo."""
        if self.current_view:
            self.current_view.destroy() # Destrói a view anterior
        self.current_view = new_view_class(self.content_frame, self.event_manager, self.transaction_service, self.category_service)
        self.current_view.pack(fill="both", expand=True)

    def show_home_view(self):
        """Exibe a view inicial (pode ser um dashboard simples)."""
        if self.current_view: self.current_view.destroy()
        self.current_view = HomeView(self.content_frame, self.event_manager, self.transaction_service, self.category_service)
        self.current_view.pack(fill="both", expand=True)

    def show_transaction_entry_view(self):
        """Exibe a view para registrar novas transações."""
        self.switch_view(TransactionEntryView)

    def show_transaction_list_view(self):
        """Exibe a view para visualizar o extrato de transações."""
        self.switch_view(TransactionListView)

    def show_category_manager_view(self):
        """Exibe a view para gerenciar categorias."""
        self.switch_view(CategoryManagerView)

    def show_report_view(self):
        """Exibe a view para gerar relatórios."""
        self.switch_view(ReportView)


class BaseView(ttk.Frame):
    """Classe base para todas as views, fornecendo acesso comum a serviços e gerenciador de eventos."""
    def __init__(self, parent, event_manager: EventManager, transaction_service: TransactionService, category_service: CategoryService):
        super().__init__(parent)
        self.event_manager = event_manager
        self.transaction_service = transaction_service
        self.category_service = category_service

# --- Views Específicas ---

class HomeView(BaseView):
    def __init__(self, parent, event_manager, transaction_service, category_service):
        super().__init__(parent, event_manager, transaction_service, category_service)
        ttk.Label(self, text="Bem-vindo ao Gerenciador Financeiro Pessoal!", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(self, text="Use o menu à esquerda para navegar.", font=("Arial", 12)).pack(pady=10)

        # Exibir um resumo rápido (ex: saldo atual)
        self.balance_label = ttk.Label(self, text="", font=("Arial", 14))
        self.balance_label.pack(pady=20)
        self.update_balance()

        # Inscrever-se para atualizações de transações
        self.event_manager.subscribe("transaction_added", self.update_balance)
        self.event_manager.subscribe("transaction_deleted", self.update_balance)


    def update_balance(self, *args):
        """Atualiza o saldo total exibido."""
        transactions = self.transaction_service.get_all_transactions()
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
        current_balance = total_income - total_expense
        self.balance_label.config(text=f"Saldo Atual: R$ {current_balance:,.2f}")


class TransactionEntryView(BaseView):
    """View para registrar novas transações."""
    def __init__(self, parent, event_manager, transaction_service, category_service):
        super().__init__(parent, event_manager, transaction_service, category_service)
        self.create_widgets()
        self.load_categories()

        # Inscrever-se para atualizações de categorias para o combobox
        self.event_manager.subscribe("category_added", self.load_categories)
        self.event_manager.subscribe("category_updated", self.load_categories)
        self.event_manager.subscribe("category_deleted", self.load_categories)


    def create_widgets(self):
        ttk.Label(self, text="Registrar Nova Transação", font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        # Tipo de Transação
        ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.type_var = tk.StringVar(value="expense") # Valor padrão
        self.type_radio_expense = ttk.Radiobutton(form_frame, text="Despesa", variable=self.type_var, value="expense")
        self.type_radio_expense.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.type_radio_income = ttk.Radiobutton(form_frame, text="Receita", variable=self.type_var, value="income")
        self.type_radio_income.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Valor
        ttk.Label(form_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Data
        ttk.Label(form_frame, text="Data (AAAA-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(form_frame)
        self.date_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d")) # Data atual como padrão

        # Descrição
        ttk.Label(form_frame, text="Descrição:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.description_entry = ttk.Entry(form_frame)
        self.description_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Categoria
        ttk.Label(form_frame, text="Categoria:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly")
        self.category_combobox.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Botão Salvar
        ttk.Button(self, text="Salvar Transação", command=self.save_transaction).pack(pady=15)

    def load_categories(self, *args):
        """Carrega as categorias disponíveis no combobox."""
        categories = self.category_service.get_all_categories()
        category_names = [c['name'] for c in categories]
        self.category_combobox['values'] = category_names
        if "Outros" in category_names:
            self.category_var.set("Outros") # Define "Outros" como categoria padrão
        elif category_names:
            self.category_var.set(category_names[0]) # Define a primeira categoria se "Outros" não existir

    def save_transaction(self):
        """Coleta os dados e tenta salvar a transação."""
        trans_type = self.type_var.get()
        amount_str = self.amount_entry.get()
        date_str = self.date_entry.get()
        description = self.description_entry.get()
        category = self.category_var.get()

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Erro de Validação", "O valor deve ser um número válido.")
            return

        if not category:
            messagebox.showerror("Erro de Validação", "Selecione ou crie uma categoria.")
            return

        if self.transaction_service.register_transaction(trans_type, amount, date_str, description, category):
            messagebox.showinfo("Sucesso", "Transação salva com sucesso!")
            # Limpa os campos após salvar
            self.amount_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
            self.type_var.set("expense") # Reseta para despesa padrão
            self.load_categories() # Recarrega categorias caso alguma tenha sido adicionada

        else:
            messagebox.showerror("Erro", "Falha ao salvar transação. Verifique os dados.")


class TransactionListView(BaseView):
    """View para visualizar e filtrar o extrato de transações."""
    def __init__(self, parent, event_manager, transaction_service, category_service):
        super().__init__(parent, event_manager, transaction_service, category_service)
        self.create_widgets()
        self.load_transactions()

        # Inscrever-se para eventos de atualização de transações
        self.event_manager.subscribe("transaction_added", self.load_transactions)
        self.event_manager.subscribe("transaction_deleted", self.load_transactions)

    def create_widgets(self):
        ttk.Label(self, text="Extrato de Transações", font=("Arial", 14, "bold")).pack(pady=10)

        # Frame para filtros
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=5, fill="x")

        ttk.Label(filter_frame, text="De:").pack(side="left", padx=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_date_entry.insert(0, (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))


        ttk.Label(filter_frame, text="Até:").pack(side="left", padx=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        ttk.Button(filter_frame, text="Filtrar", command=self.load_transactions).pack(side="left", padx=10)

        # Treeview para exibir transações
        self.tree = ttk.Treeview(self, columns=("ID", "Tipo", "Valor", "Data", "Descrição", "Categoria"), show="headings")
        self.tree.pack(fill="both", expand=True)

        # Definir cabeçalhos das colunas
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Valor", text="Valor")
        self.tree.heading("Data", text="Data")
        self.tree.heading("Descrição", text="Descrição")
        self.tree.heading("Categoria", text="Categoria")

        # Configurar larguras das colunas (aproximadas)
        self.tree.column("ID", width=30, stretch=tk.NO)
        self.tree.column("Tipo", width=70, stretch=tk.NO)
        self.tree.column("Valor", width=80, stretch=tk.NO)
        self.tree.column("Data", width=80, stretch=tk.NO)
        self.tree.column("Descrição", width=200, stretch=tk.YES)
        self.tree.column("Categoria", width=100, stretch=tk.NO)

        # Botão para excluir transação
        ttk.Button(self, text="Excluir Transação Selecionada", command=self.delete_selected_transaction).pack(pady=10)


    def load_transactions(self, *args):
        """Carrega e exibe as transações no Treeview, aplicando filtros de data."""
        for item in self.tree.get_children():
            self.tree.delete(item) # Limpa a Treeview antes de recarregar

        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        # Validação de data básica
        try:
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro de Data", "Formato de data inválido. Use AAAA-MM-DD.")
            return

        transactions = self.transaction_service.get_transactions_for_report(start_date, end_date)

        for trans in transactions:
            self.tree.insert("", "end", values=(
                trans['id'],
                "Receita" if trans['type'] == 'income' else "Despesa",
                f"R$ {trans['amount']:,.2f}",
                trans['date'],
                trans['description'],
                trans['category']
            ))

    def delete_selected_transaction(self):
        """Exclui a transação selecionada na Treeview."""
        selected_item = self.tree.focus() # Obtém o item selecionado
        if not selected_item:
            messagebox.showwarning("Atenção", "Nenhuma transação selecionada para exclusão.")
            return

        values = self.tree.item(selected_item, 'values')
        transaction_id = values[0] # O ID é a primeira coluna

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a transação ID {transaction_id}?"):
            if self.transaction_service.delete_transaction(transaction_id):
                messagebox.showinfo("Sucesso", "Transação excluída com sucesso!")
                # O evento 'transaction_deleted' já irá acionar o load_transactions
            else:
                messagebox.showerror("Erro", "Falha ao excluir transação.")


class CategoryManagerView(BaseView):
    """View para adicionar, editar e excluir categorias."""
    def __init__(self, parent, event_manager, transaction_service, category_service):
        super().__init__(parent, event_manager, transaction_service, category_service)
        self.create_widgets()
        self.load_categories()

        # Inscrever-se para eventos de atualização de categorias
        self.event_manager.subscribe("category_added", self.load_categories)
        self.event_manager.subscribe("category_updated", self.load_categories)
        self.event_manager.subscribe("category_deleted", self.load_categories)


    def create_widgets(self):
        ttk.Label(self, text="Gerenciar Categorias", font=("Arial", 14, "bold")).pack(pady=10)

        # Entrada para nova categoria
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=5)
        ttk.Label(entry_frame, text="Nome da Categoria:").pack(side="left", padx=5)
        self.category_name_entry = ttk.Entry(entry_frame, width=30)
        self.category_name_entry.pack(side="left", padx=5)
        ttk.Button(entry_frame, text="Adicionar", command=self.add_category).pack(side="left", padx=5)
        ttk.Button(entry_frame, text="Atualizar Selecionada", command=self.update_category).pack(side="left", padx=5)


        # Treeview para exibir categorias
        self.tree = ttk.Treeview(self, columns=("ID", "Nome"), show="headings")
        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome da Categoria")

        self.tree.column("ID", width=30, stretch=tk.NO)
        self.tree.column("Nome", width=200, stretch=tk.YES)

        self.tree.bind("<<TreeviewSelect>>", self.on_category_select) # Evento de seleção

        # Botão para excluir categoria
        ttk.Button(self, text="Excluir Categoria Selecionada", command=self.delete_category).pack(pady=10)


    def load_categories(self, *args):
        """Carrega e exibe as categorias no Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        categories = self.category_service.get_all_categories()
        for cat in categories:
            self.tree.insert("", "end", values=(cat['id'], cat['name']))
        
        # Limpa o campo de entrada e deseleciona qualquer item na treeview
        self.category_name_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def on_category_select(self, event):
        """Preenche o campo de entrada com o nome da categoria selecionada."""
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            self.category_name_entry.delete(0, tk.END)
            self.category_name_entry.insert(0, values[1]) # O nome está na segunda coluna (índice 1)


    def add_category(self):
        """Adiciona uma nova categoria."""
        name = self.category_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Atenção", "O nome da categoria não pode ser vazio.")
            return
        
        if self.category_service.add_category(name):
            messagebox.showinfo("Sucesso", f"Categoria '{name}' adicionada com sucesso!")
            self.category_name_entry.delete(0, tk.END) # Limpa o campo
            # O evento "category_added" irá acionar o load_categories

        else:
            messagebox.showerror("Erro", "Falha ao adicionar categoria. Verifique se o nome já existe.")


    def update_category(self):
        """Atualiza a categoria selecionada."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenção", "Nenhuma categoria selecionada para atualização.")
            return
        
        category_id = self.tree.item(selected_item, 'values')[0]
        new_name = self.category_name_entry.get().strip()

        if not new_name:
            messagebox.showwarning("Atenção", "O novo nome da categoria não pode ser vazio.")
            return
        
        if self.category_service.update_category(category_id, new_name):
            messagebox.showinfo("Sucesso", "Categoria atualizada com sucesso!")
            self.category_name_entry.delete(0, tk.END)
            # O evento "category_updated" irá acionar o load_categories
        else:
            messagebox.showerror("Erro", "Falha ao atualizar categoria. Verifique se o nome já existe ou se o ID é válido.")

    def delete_category(self):
        """Exclui a categoria selecionada."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenção", "Nenhuma categoria selecionada para exclusão.")
            return

        category_id = self.tree.item(selected_item, 'values')[0]
        category_name = self.tree.item(selected_item, 'values')[1]

        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a categoria '{category_name}' (ID: {category_id})?"):
            # TODO: Antes de excluir, o ideal seria reatribuir transações com esta categoria para 'Outros'.
            # Por simplicidade, nesta versão a exclusão da categoria não verifica transações associadas.
            if self.category_service.delete_category(category_id):
                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!")
                # O evento "category_deleted" irá acionar o load_categories
            else:
                messagebox.showerror("Erro", "Falha ao excluir categoria.")


class ReportView(BaseView):
    """View para gerar e exibir relatórios financeiros."""
    def __init__(self, parent, event_manager, transaction_service, category_service):
        super().__init__(parent, event_manager, transaction_service, category_service)
        self.report_generator = ReportGenerator(CategoryReportStrategy()) # Estratégia padrão
        self.create_widgets()
        self.generate_report() # Gera o relatório inicial

        # Assinar para eventos de transação para atualizar o relatório automaticamente
        self.event_manager.subscribe("transaction_added", self.generate_report)
        self.event_manager.subscribe("transaction_deleted", self.generate_report)


    def create_widgets(self):
        ttk.Label(self, text="Gerar Relatórios Financeiros", font=("Arial", 14, "bold")).pack(pady=10)

        # Controles de seleção de relatório e período
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10, fill="x")

        ttk.Label(control_frame, text="Tipo de Relatório:").pack(side="left", padx=5)
        self.report_type_var = tk.StringVar(value="category") # Padrão
        self.report_type_combobox = ttk.Combobox(control_frame, textvariable=self.report_type_var, state="readonly",
                                                 values=["category", "monthly"])
        self.report_type_combobox.pack(side="left", padx=5)
        self.report_type_combobox.bind("<<ComboboxSelected>>", self.on_report_type_select)

        ttk.Label(control_frame, text="De:").pack(side="left", padx=5)
        self.start_date_entry = ttk.Entry(control_frame, width=12)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_date_entry.insert(0, (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%d"))

        ttk.Label(control_frame, text="Até:").pack(side="left", padx=5)
        self.end_date_entry = ttk.Entry(control_frame, width=12)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        ttk.Button(control_frame, text="Gerar Relatório", command=self.generate_report).pack(side="left", padx=10)

        # Área de texto para exibir o relatório
        self.report_text = tk.Text(self, wrap="word", height=20, width=80, font=("Consolas", 10))
        self.report_text.pack(pady=10, fill="both", expand=True)
        self.report_text.config(state="disabled") # Torna o Text Read-Only

    def on_report_type_select(self, event):
        """Muda a estratégia de relatório com base na seleção do usuário."""
        selected_type = self.report_type_var.get()
        if selected_type == "category":
            self.report_generator.set_strategy(CategoryReportStrategy())
        elif selected_type == "monthly":
            self.report_generator.set_strategy(MonthlyReportStrategy())
        self.generate_report() # Gera o relatório com a nova estratégia

    def generate_report(self, *args):
        """Coleta os dados e gera o relatório usando a estratégia selecionada."""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        try:
            # Validação básica de data
            datetime.datetime.strptime(start_date, "%Y-%m-%d")
            datetime.datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro de Data", "Formato de data inválido. Use AAAA-MM-DD.")
            self.report_text.config(state="normal")
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "Erro: Formato de data inválido.")
            self.report_text.config(state="disabled")
            return

        transactions_data = self.transaction_service.get_transactions_for_report(start_date, end_date)
        report_output = self.report_generator.execute_report_generation(transactions_data)

        self.report_text.config(state="normal") # Habilita para escrita
        self.report_text.delete(1.0, tk.END) # Limpa conteúdo anterior
        self.report_text.insert(tk.END, report_output) # Insere o novo relatório
        self.report_text.config(state="disabled") # Desabilita novamente
