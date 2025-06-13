import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json

class BudgetApp:
    def __init__(self, root):
        self.root = root
        root.title("Калькулятор бюджета")

        self.incomes = []
        self.expenses = []

        self.income_types = ["Зарплата", "Подарки", "Дополнительный доход", "Другое"]
        self.expense_types = ["Транспорт", "Супермаркет", "Развлечения", "Кафе", "Коммуналка", "Другое"]

        tk.Label(root, text="Доходы").grid(row=0, column=0, padx=8, pady=5, sticky="w")
        self.income_entry = tk.Entry(root)
        self.income_entry.grid(row=0, column=1, padx=8)
        self.income_type_var = tk.StringVar(value=self.income_types[0])
        self.income_type_menu = ttk.Combobox(root, textvariable=self.income_type_var, values=self.income_types, state="readonly", width=20)
        self.income_type_menu.grid(row=0, column=2)
        tk.Button(root, text="Добавить", command=self.add_income).grid(row=0, column=3, padx=3)

        self.income_listbox = tk.Listbox(root, width=45)
        self.income_listbox.grid(row=1, column=0, columnspan=4, padx=10, pady=2, sticky="ew")
        tk.Button(root, text="Удалить доход", command=self.delete_income).grid(row=2, column=0, columnspan=4, padx=10, pady=4, sticky="ew")

        tk.Label(root, text="Расходы").grid(row=3, column=0, padx=8, pady=5, sticky="w")
        self.expense_entry = tk.Entry(root)
        self.expense_entry.grid(row=3, column=1, padx=8)
        self.expense_type_var = tk.StringVar(value=self.expense_types[0])
        self.expense_type_menu = ttk.Combobox(root, textvariable=self.expense_type_var, values=self.expense_types, state="readonly", width=20)
        self.expense_type_menu.grid(row=3, column=2)
        tk.Button(root, text="Добавить", command=self.add_expense).grid(row=3, column=3, padx=3)

        self.expense_listbox = tk.Listbox(root, width=45)
        self.expense_listbox.grid(row=4, column=0, columnspan=4, padx=10, pady=2, sticky="ew")
        tk.Button(root, text="Удалить расход", command=self.delete_expense).grid(row=5, column=0, columnspan=4, padx=10, pady=4, sticky="ew")

        tk.Button(root, text="Рассчитать", command=self.calculate).grid(row=6, column=0, columnspan=4, pady=8, sticky="ew")
        self.result_label = tk.Label(root, text="")
        self.result_label.grid(row=7, column=0, columnspan=4, pady=3)

        self.export_btn = tk.Button(root, text="Экспорт", command=self.export_data)
        self.import_btn = tk.Button(root, text="Импорт", command=self.import_data)
        self.export_btn.grid(row=8, column=1, padx=10, pady=15, sticky="ew")
        self.import_btn.grid(row=8, column=2, padx=10, pady=15, sticky="ew")

        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)

    def add_income(self):
        try:
            value = float(self.income_entry.get())
            category = self.income_type_var.get()
            self.incomes.append((value, category))
            self.income_listbox.insert(tk.END, f"{value:.2f} руб. ({category})")
            self.income_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для дохода!")

    def add_expense(self):
        try:
            value = float(self.expense_entry.get())
            category = self.expense_type_var.get()
            self.expenses.append((value, category))
            self.expense_listbox.insert(tk.END, f"{value:.2f} руб. ({category})")
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
        total_income = sum(income[0] for income in self.incomes)
        total_expense = sum(expense[0] for expense in self.expenses)
        balance = total_income - total_expense

        income_cat = {}
        for amount, cat in self.incomes:
            income_cat[cat] = income_cat.get(cat, 0) + amount

        expense_cat = {}
        for amount, cat in self.expenses:
            expense_cat[cat] = expense_cat.get(cat, 0) + amount

        message = (f"Доходы: {total_income:.2f} руб.\n"
                   f"Расходы: {total_expense:.2f} руб.\n"
                   f"Баланс: {balance:.2f} руб.\n\n"
                   f"Доходы по категориям:\n")
        for cat, amount in income_cat.items():
            message += f"  {cat}: {amount:.2f} руб.\n"
        message += "Расходы по категориям:\n"
        for cat, amount in expense_cat.items():
            message += f"  {cat}: {amount:.2f} руб.\n"

        if balance > 0:
            message += "Поздравляем! У вас положительный баланс."
        elif balance < 0:
            message += "Внимание! Расходы превышают доходы."
        else:
            message += "Баланс равен нулю."
        self.result_label.config(text=message)

    def export_data(self):
        data = {
            "incomes": [list(item) for item in self.incomes],
            "expenses": [list(item) for item in self.expenses]
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")], title="Сохранить как")
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Экспорт завершён", f"Данные успешно сохранены в: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", str(e))

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")], title="Открыть данные")
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.incomes = [tuple(item) for item in data.get("incomes", [])]
            self.expenses = [tuple(item) for item in data.get("expenses", [])]

            self.income_listbox.delete(0, tk.END)
            for value, category in self.incomes:
                self.income_listbox.insert(tk.END, f"{float(value):.2f} руб. ({category})")
            self.expense_listbox.delete(0, tk.END)
            for value, category in self.expenses:
                self.expense_listbox.insert(tk.END, f"{float(value):.2f} руб. ({category})")
            messagebox.showinfo("Импорт завершён", f"Данные успешно загружены из: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка импорта", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()