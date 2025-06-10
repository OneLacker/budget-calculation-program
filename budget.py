import tkinter as tk
from tkinter import messagebox

class BudgetApp:
    def __init__(self, root):
        self.root = root
        root.title("Калькулятор бюджета")

        self.incomes = []
        self.expenses = []

        tk.Label(root, text="Доходы").grid(row=0, column=0, padx=10, pady=5)
        self.income_entry = tk.Entry(root)
        self.income_entry.grid(row=0, column=1, padx=10)
        tk.Button(root, text="Добавить", command=self.add_income).grid(row=0, column=2)

        self.income_listbox = tk.Listbox(root)
        self.income_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        tk.Button(root, text="Удалить выбранное", command=self.delete_income).grid(row=1, column=3, padx=5, pady=5)

        tk.Label(root, text="Расходы").grid(row=2, column=0, padx=10, pady=5)
        self.expense_entry = tk.Entry(root)
        self.expense_entry.grid(row=2, column=1, padx=10)
        tk.Button(root, text="Добавить", command=self.add_expense).grid(row=2, column=2)

        self.expense_listbox = tk.Listbox(root)
        self.expense_listbox.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        
        tk.Button(root, text="Удалить выбранное", command=self.delete_expense).grid(row=3, column=3, padx=5, pady=5)

        tk.Button(root, text="Рассчитать", command=self.calculate).grid(row=4, column=0, columnspan=3, pady=10)
        self.result_label = tk.Label(root, text="")
        self.result_label.grid(row=5, column=0, columnspan=3, pady=5)

    def add_income(self):
        try:
            value = float(self.income_entry.get())
            self.incomes.append(value)
            self.income_listbox.insert(tk.END, f"{value:.2f} руб.")
            self.income_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для дохода!")
            
    def add_expense(self):
        try:
            value = float(self.expense_entry.get())
            self.expenses.append(value)
            self.expense_listbox.insert(tk.END, f"{value:.2f} руб.")
            self.expense_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для расхода!")
    
    def delete_income(self):
        selected = self.income_listbox.curselection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите запись для удаления!")
            return
        for idx in reversed(selected):
            self.income_listbox.delete(idx)
            del self.incomes[idx]

    def delete_expense(self):
        selected = self.expense_listbox.curselection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите запись для удаления!")
            return
        for idx in reversed(selected):
            self.expense_listbox.delete(idx)
            del self.expenses[idx]

    def calculate(self):
        total_income = sum(self.incomes)
        total_expense = sum(self.expenses)
        balance = total_income - total_expense
        
        message = (f"Доходы: {total_income:.2f} руб.\n"
                   f"Расходы: {total_expense:.2f} руб.\n"
                   f"Баланс: {balance:.2f} руб.\n")
        if balance > 0:
            message += "Поздравляем! У вас положительный баланс."
        elif balance < 0:
            message += "Внимание! Расходы превышают доходы."
        else:
            message += "Баланс равен нулю."
        self.result_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()