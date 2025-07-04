import tkinter as tk
from tkinter import messagebox, ttk, filedialog, simpledialog
import json
from datetime import datetime

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

class SavingsGoalDialog(tk.Toplevel):
    def __init__(self, master, goals, callback):
        super().__init__(master)
        self.title("Копилки и цели накопления")
        self.resizable(False, False)
        self.callback = callback
        self.goals = goals.copy()  # словарь: {название: {target, deadline_str, saved}}

        self.tree = ttk.Treeview(self, columns=("target", "deadline", "saved"), show="headings", height=8)
        self.tree.heading("target", text="Цель (руб.)")
        self.tree.heading("deadline", text="Срок (ДД.ММ.ГГГГ)")
        self.tree.heading("saved", text="Накоплено (руб.)")
        self.tree.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        self.update_tree()

        tk.Button(self, text="Добавить цель", command=self.add_goal).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        tk.Button(self, text="Редактировать цель", command=self.edit_goal).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self, text="Удалить цель", command=self.delete_goal).grid(row=1, column=2, padx=5, pady=5, sticky="ew")
        tk.Button(self, text="Закрыть", command=self.close).grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.close)

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for name, info in self.goals.items():
            self.tree.insert("", tk.END, iid=name, values=(
                f"{info['target']:.2f}",
                info['deadline_str'],
                f"{info['saved']:.2f}"
            ))

    def add_goal(self):
        dlg = GoalEditDialog(self, "", 0.0, "", 0.0)
        self.wait_window(dlg)
        if dlg.result:
            name, target, deadline_str, saved = dlg.result
            if name in self.goals:
                messagebox.showerror("Ошибка", "Копилка с таким именем уже существует!")
                return
            self.goals[name] = {"target": target, "deadline_str": deadline_str, "saved": saved}
            self.update_tree()

    def edit_goal(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Редактирование", "Выберите цель для редактирования!")
            return
        name = selected[0]
        info = self.goals[name]
        dlg = GoalEditDialog(self, name, info["target"], info["deadline_str"], info["saved"])
        self.wait_window(dlg)
        if dlg.result:
            new_name, target, deadline_str, saved = dlg.result
            if new_name != name and new_name in self.goals:
                messagebox.showerror("Ошибка", "Копилка с таким именем уже существует!")
                return
            del self.goals[name]
            self.goals[new_name] = {"target": target, "deadline_str": deadline_str, "saved": saved}
            self.update_tree()

    def delete_goal(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Удаление", "Выберите цель для удаления!")
            return
        for name in selected:
            del self.goals[name]
        self.update_tree()

    def close(self):
        self.callback(self.goals)
        self.destroy()

class GoalEditDialog(tk.Toplevel):
    def __init__(self, master, name, target, deadline_str, saved):
        super().__init__(master)
        self.title("Редактирование цели")
        self.resizable(False, False)
        self.result = None

        tk.Label(self, text="Название цели:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=8, pady=8)
        self.name_entry.insert(0, name)

        tk.Label(self, text="Сумма для накопления (руб.):").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.target_entry = tk.Entry(self)
        self.target_entry.grid(row=1, column=1, padx=8, pady=8)
        self.target_entry.insert(0, f"{target:.2f}" if target else "")

        tk.Label(self, text="Крайний срок (ДД.ММ.ГГГГ):").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        self.deadline_entry = tk.Entry(self)
        self.deadline_entry.grid(row=2, column=1, padx=8, pady=8)
        self.deadline_entry.insert(0, deadline_str)

        tk.Label(self, text="Накоплено (руб.):").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        self.saved_entry = tk.Entry(self)
        self.saved_entry.grid(row=3, column=1, padx=8, pady=8)
        self.saved_entry.insert(0, f"{saved:.2f}" if saved else "0.00")

        tk.Button(self, text="Сохранить", command=self.save).grid(row=4, column=0, columnspan=2, pady=12, sticky="ew")

        self.name_entry.focus()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def save(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название цели!")
            return
        try:
            target = float(self.target_entry.get())
            if target <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму для накопления (больше 0)!")
            return
        deadline_str = self.deadline_entry.get().strip()
        try:
            datetime.strptime(deadline_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную дату в формате ДД.ММ.ГГГГ!")
            return
        try:
            saved = float(self.saved_entry.get())
            if saved < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму накопления (0 или больше)!")
            return
        if saved > target:
            messagebox.showerror("Ошибка", "Накоплено не может быть больше цели!")
            return
        self.result = (name, target, deadline_str, saved)
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

        # Копилки и цели накопления — словарь {название: {target, deadline_str, saved}}
        self.savings_goals = {}

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

        self.savings_btn = tk.Button(root, text="Копилки и цели", command=self.set_savings_goals)
        self.savings_btn.grid(row=8, column=3, padx=10, pady=15, sticky="ew")

        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)

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
            warnings = []
            for cat in {new_category, old_category}:
                msg = self.check_limit_for_category(cat, return_message=True)
                if msg:
                    warnings.append(msg)
            if warnings:
                messagebox.showinfo("Лимиты", "\n".join(warnings))

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
        affected_cats = set()
        for idx in selected:
            affected_cats.add(self.expenses[idx][1])
        for idx in reversed(selected):
            self.expense_listbox.delete(idx)
            del self.expenses[idx]
        warnings = []
        for cat in affected_cats:
            msg = self.check_limit_for_category(cat, return_message=True)
            if msg:
                warnings.append(msg)
        if warnings:
            messagebox.showinfo("Лимиты", "\n".join(warnings))

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

        if self.savings_goals:
            message += "\nЦели накопления:\n"
            now = datetime.now()
            for name, info in self.savings_goals.items():
                target = info['target']
                saved = info['saved']
                try:
                    deadline = datetime.strptime(info['deadline_str'], "%d.%m.%Y")
                    days_left = (deadline - now).days
                except Exception:
                    days_left = "неизвестно"
                progress_percent = (saved / target) * 100 if target > 0 else 0
                status = "Выполнено!" if saved >= target else "В процессе"
                time_warning = ""
                if isinstance(days_left, int):
                    if days_left < 0:
                        time_warning = "Просрочено!"
                    elif 0 <= days_left <= 7:
                        time_warning = "Срок близко!"

                message += f"  {name}: {saved:.2f} / {target:.2f} руб., срок: {info['deadline_str']} ({days_left} дн.) {status}"
                if time_warning:
                    message += f" - {time_warning}"
                message += f" ({progress_percent:.1f}%)\n"

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

    def check_limit_for_category(self, cat, return_message=False):
        if cat not in self.limits:
            return None
        spent = sum(v for v, c in self.expenses if c == cat)
        limit = self.limits[cat]
        if spent >= limit:
            msg = f"Переполнение лимита по '{cat}': потрачено {spent:.2f} из {limit:.2f} руб.!"
            if return_message:
                return "ВНИМАНИЕ. " + msg
            else:
                messagebox.showwarning("Лимит превышен", msg)
        elif spent >= 0.9 * limit:
            msg = f"Внимание: почти израсходован лимит по '{cat}' ({spent:.2f} из {limit:.2f} руб.)"
            if return_message:
                return msg
            else:
                messagebox.showinfo("Лимит бюджета", msg)
        return None

    def export_data(self):
        data = {
            "incomes": [list(item) for item in self.incomes],
            "expenses": [list(item) for item in self.expenses],
            "limits": self.limits,
            "savings_goals": self.savings_goals,
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

            self.savings_goals = {}
            for name, info in data.get("savings_goals", {}).items():
                try:
                    target = float(info["target"])
                    saved = float(info.get("saved", 0))
                    deadline_str = str(info["deadline_str"])
                    self.savings_goals[str(name)] = {"target": target, "deadline_str": deadline_str, "saved": saved}
                except (ValueError, KeyError, TypeError):
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

    def set_savings_goals(self):
        SavingsGoalDialog(self.root, self.savings_goals, self.save_savings_goals)

    def save_savings_goals(self, goals_dict):
        self.savings_goals = goals_dict
        messagebox.showinfo("Копилки и цели", "Данные копилок и целей обновлены.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()