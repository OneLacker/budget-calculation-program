import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import json

class EditDialog(tk.Toplevel):
    def __init__(self, master, value, category, categories, callback):
        super().__init__(master)
        self.title("Редактировать запись")
        self.resizable(False, False)
        self.callback = callback

        tk.Label(self, text="Сумма:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.value_entry = tk.Entry(self)
        self.value_entry.grid(row=0, column=1, padx=8, pady=8)
        self.value_entry.insert(0, str(value))

        tk.Label(self, text="Категория:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.category_var = tk.StringVar(value=category)
        self.category_menu = ttk.Combobox(self, textvariable=self.category_var, values=categories, state="readonly")
        self.category_menu.grid(row=1, column=1, padx=8, pady=8)

        tk.Button(self, text="Сохранить", command=self.save).grid(row=2, column=0, columnspan=2, pady=12, sticky="ew")

        self.value_entry.focus()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def save(self):
        try:
            value = float(self.value_entry.get())
            if value < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")
            return
        category = self.category_var.get()
        self.callback(value, category)
        self.destroy()

class LimitDialog(tk.Toplevel):
    """Окно для установки лимитов по категориям расходов"""
    def __init__(self, master, expense_types, limits, callback):
        super().__init__(master)
        self.title("Лимиты расходов")
        self.resizable(False, False)
        self.callback = callback
        self.entries = {}

        row = 0
        for cat in expense_types:
            tk.Label(self, text=cat).grid(row=row, column=0, padx=8, pady=5, sticky="w")
            var = tk.StringVar(value=str(limits.get(cat, "")))
            entry = tk.Entry(self, textvariable=var, width=12)
            entry.grid(row=row, column=1, padx=8, pady=5)
            self.entries[cat] = entry
            row += 1

        tk.Button(self, text="Сохранить лимиты", command=self.save).grid(row=row, column=0, columnspan=2, pady=12, sticky="ew")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def save(self):
        new_limits = {}
        for cat, entry in self.entries.items():
            val = entry.get().strip()
            if val:
                try:
                    lim = float(val)
                    if lim < 0:
                        raise ValueError
                    new_limits[cat] = lim
                except ValueError:
                    messagebox.showerror("Ошибка", f"Некорректный лимит для категории '{cat}'!")
                    return
        self.callback(new_limits)
        self.destroy()

class BudgetApp:
    def __init__(self, root):
        self.root = root
        root.title("Калькулятор бюджета")

        self.incomes = []
        self.expenses = []

        self.income_types = ["Зарплата", "Подарки", "Дополнительный доход", "Другое"]
        self.expense_types = ["Транспорт", "Супермаркет", "Развлечения", "Кафе", "Коммуналка", "Другое"]
        self.limits = {}

        tk.Label(root, text="Доходы").grid(row=0, column=0, padx=8, pady=5, sticky="w")
        self.income_entry = tk.Entry(root)
        self.income_entry.grid(row=0, column=1, padx=8)
        self.income_type_var = tk.StringVar(value=self.income_types[0])
        self.income_type_menu = ttk.Combobox(root, textvariable=self.income_type_var, values=self.income_types, state="readonly", width=20)
        self.income_type_menu.grid(row=0, column=2)
        tk.Button(root, text="Добавить", command=self.add_income).grid(row=0, column=3, padx=3)

        self.income_listbox = tk.Listbox(root, width=45)
        self.income_listbox.grid(row=1, column=0, columnspan=4, padx=10, pady=2, sticky="ew")
        tk.Button(root, text="Редактировать доход", command=self.edit_income).grid(row=2, column=0, columnspan=2, padx=10, pady=4, sticky="ew")
        tk.Button(root, text="Удалить доход", command=self.delete_income).grid(row=2, column=2, columnspan=2, padx=10, pady=4, sticky="ew")

        tk.Label(root, text="Расходы").grid(row=3, column=0, padx=8, pady=5, sticky="w")
        self.expense_entry = tk.Entry(root)
        self.expense_entry.grid(row=3, column=1, padx=8)
        self.expense_type_var = tk.StringVar(value=self.expense_types[0])
        self.expense_type_menu = ttk.Combobox(root, textvariable=self.expense_type_var, values=self.expense_types, state="readonly", width=20)
        self.expense_type_menu.grid(row=3, column=2)
        tk.Button(root, text="Добавить", command=self.add_expense).grid(row=3, column=3, padx=3)

        self.expense_listbox = tk.Listbox(root, width=45)
        self.expense_listbox.grid(row=4, column=0, columnspan=4, padx=10, pady=2, sticky="ew")
        tk.Button(root, text="Редактировать расход", command=self.edit_expense).grid(row=5, column=0, columnspan=2, padx=10, pady=4, sticky="ew")
        tk.Button(root, text="Удалить расход", command=self.delete_expense).grid(row=5, column=2, columnspan=2, padx=10, pady=4, sticky="ew")

        tk.Button(root, text="Рассчитать", command=self.calculate).grid(row=6, column=0, columnspan=4, pady=8, sticky="ew")
        self.result_label = tk.Label(root, text="")
        self.result_label.grid(row=7, column=0, columnspan=4, pady=3)

        self.export_btn = tk.Button(root, text="Экспорт", command=self.export_data)
        self.import_btn = tk.Button(root, text="Импорт", command=self.import_data)
        self.export_btn.grid(row=8, column=1, padx=10, pady=15, sticky="ew")
        self.import_btn.grid(row=8, column=2, padx=10, pady=15, sticky="ew")

        self.limits_btn = tk.Button(root, text="Установить лимиты", command=self.set_limits)
        self.limits_btn.grid(row=8, column=0, padx=10, pady=15, sticky="ew")

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
            self.check_limit_for_category(category)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число для расхода!")

    def edit_income(self):
        selected = self.income_listbox.curselection()
        if not selected:
            messagebox.showwarning("Редактирование", "Выберите запись для редактирования!")
            return
        idx = selected[0]
        value, category = self.incomes[idx]
        def callback(new_value, new_category):
            self.incomes[idx] = (new_value, new_category)
            self.income_listbox.delete(idx)
            self.income_listbox.insert(idx, f"{new_value:.2f} руб. ({new_category})")
        EditDialog(self.root, value, category, self.income_types, callback)

    def edit_expense(self):
        selected = self.expense_listbox.curselection()
        if not selected:
            messagebox.showwarning("Редактирование", "Выберите запись для редактирования!")
            return
        idx = selected[0]
        value, category = self.expenses[idx]
        old_category = category
        def callback(new_value, new_category):
            self.expenses[idx] = (new_value, new_category)
            self.expense_listbox.delete(idx)
            self.expense_listbox.insert(idx, f"{new_value:.2f} руб. ({new_category})")
            self.check_limit_for_category(new_category)
            if new_category != old_category:
                self.check_limit_for_category(old_category)
        EditDialog(self.root, value, category, self.expense_types, callback)

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
            cat = self.expenses[idx][1]
            self.expense_listbox.delete(idx)
            del self.expenses[idx]
            self.check_limit_for_category(cat)

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

        warnings = self.check_all_limits(return_messages=True)

        message = (f"Доходы: {total_income:.2f} руб.\n"
                   f"Расходы: {total_expense:.2f} руб.\n"
                   f"Баланс: {balance:.2f} руб.\n\n"
                   f"Доходы по категориям:\n")
        for cat, amount in income_cat.items():
            message += f"  {cat}: {amount:.2f} руб.\n"
        message += "Расходы по категориям:\n"
        for cat, amount in expense_cat.items():
            message += f"  {cat}: {amount:.2f} руб.\n"
        if warnings:
            message += "\n".join(warnings) + "\n"
        if balance > 0:
            message += "Поздравляем! У вас положительный баланс."
        elif balance < 0:
            message += "Внимание! Расходы превышают доходы."
        else:
            message += "Баланс равен нулю."
        self.result_label.config(text=message)

    def set_limits(self):
        LimitDialog(self.root, self.expense_types, self.limits, self.save_limits)

    def save_limits(self, limits_dict):
        self.limits = limits_dict
        messagebox.showinfo("Лимиты", "Лимиты расходов обновлены.")

    def check_all_limits(self, return_messages=False):
        """Проверяет все лимиты расходов, оповещает; возвращает сообщения если надо"""
        cat_sums = {}
        messages = []
        for value, cat in self.expenses:
            cat_sums[cat] = cat_sums.get(cat, 0) + value

        for cat, limit in self.limits.items():
            spent = cat_sums.get(cat, 0)
            if spent >= limit:
                msg = f"Переполнение лимита по '{cat}': потрачено {spent:.2f} из {limit:.2f} руб.!"
                if return_messages:
                    messages.append("ВНИМАНИЕ. " + msg)
                else:
                    messagebox.showwarning("Лимит превышен", msg)
            elif spent >= 0.9 * limit:
                msg = f"Внимание: почти израсходован лимит по '{cat}' ({spent:.2f} из {limit:.2f} руб.)"
                if return_messages:
                    messages.append(msg)
                else:
                    messagebox.showinfo("Лимит бюджета", msg)
        return messages

    def check_limit_for_category(self, cat):
        """Проверяет лимит только для одной категории и оповещает"""
        if cat not in self.limits:
            return
        spent = sum(v for v, c in self.expenses if c == cat)
        limit = self.limits[cat]
        if spent >= limit:
            messagebox.showwarning(
                "Лимит превышен",
                f"Переполнение лимита по '{cat}': потрачено {spent:.2f} из {limit:.2f} руб.!"
            )
        elif spent >= 0.9 * limit:
            messagebox.showinfo(
                "Лимит бюджета",
                f"Внимание: почти израсходован лимит по '{cat}' ({spent:.2f} из {limit:.2f} руб.)"
            )

    def export_data(self):
        data = {
            "incomes": [list(item) for item in self.incomes],
            "expenses": [list(item) for item in self.expenses],
            "limits": self.limits
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

def export_data(self):
        data = {
            "incomes": [list(item) for item in self.incomes],
            "expenses": [list(item) for item in self.expenses],
            "limits": self.limits
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
    
            self.incomes = []
            for item in data.get("incomes", []):
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    value, category = item
                    try:
                        value = float(value)
                        category = str(category)
                        self.incomes.append((value, category))
                    except (ValueError, TypeError):
                        continue 
                    
            self.expenses = []
            for item in data.get("expenses", []):
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    value, category = item
                    try:
                        value = float(value)
                        category = str(category)
                        self.expenses.append((value, category))
                    except (ValueError, TypeError):
                        continue
                    
            self.limits = {}
            for cat, val in data.get("limits", {}).items():
                try:
                    self.limits[str(cat)] = float(val)
                except (ValueError, TypeError):
                    continue
                
            self.income_listbox.delete(0, tk.END)
            for value, category in self.incomes:
                self.income_listbox.insert(tk.END, f"{value:.2f} руб. ({category})")
    
            self.expense_listbox.delete(0, tk.END)
            for value, category in self.expenses:
                self.expense_listbox.insert(tk.END, f"{value:.2f} руб. ({category})")
    
            messagebox.showinfo("Импорт завершён", f"Данные успешно загружены из: {file_path}")
    
            warnings = self.check_all_limits(return_messages=True)
            if warnings:
                messagebox.showinfo("Лимиты", "\n".join(warnings))
        except Exception as e:
            messagebox.showerror("Ошибка импорта", f"Ошибка при импорте данных: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()
