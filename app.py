import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from dataclasses import dataclass
import json
import datetime

# Объявляем все допустимые статусы
TASK_STATUSES = ["новая", "выполняется", "ревью", "выполнено", "отменено"]


@dataclass
class Task:
    name: str
    description: str
    status: str
    date_create: str
    date_change: str


class TaskManager:
    def __init__(self):
        self._tasks = []

    def add_task(self, task: Task):
        if task.status in TASK_STATUSES:
            self._tasks.append(task)
            return True
        return False

    def save_tasks_to_file(self, filename: str):
        task_dict = [task.__dict__ for task in self._tasks]
        with open(filename, 'w') as file:
            json.dump(task_dict, file)

    def load_tasks_from_file(self, filename: str):
        try:
            with open(filename, 'r') as file:
                task_dict = json.load(file)
            self._tasks = [Task(**task) for task in task_dict]
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def get_task_names(self):
        return [task.name for task in self._tasks]

    def get_task_by_name(self, name: str):
        for task in self._tasks:
            if task.name == name:
                return task
        return None

    def update_task_status(self, task_name: str, new_status: str):
        task = self.get_task_by_name(task_name)
        if task:
            date_now = str(datetime.date.today())
            task.status = new_status + ',' + task.status
            task.date_change = date_now + ',' + task.date_change
            return True
        return False


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.root.geometry("800x600")

        self.task_manager = TaskManager()
        self.current_file = "tasks.json"

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель (список задач)
        left_frame = ttk.Frame(main_frame, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.task_listbox = tk.Listbox(left_frame)
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        self.task_listbox.bind('<<ListboxSelect>>', self.show_task_details)

        # Кнопки управления задачами
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Добавить", command=self.add_task_dialog).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_task).pack(side=tk.LEFT, fill=tk.X, expand=True,
                                                                             padx=5)

        # Правая панель (детали задачи)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Информация о задаче
        ttk.Label(right_frame, text="Детали задачи", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)

        self.details_text = tk.Text(right_frame, height=10, state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # История статусов
        ttk.Label(right_frame, text="История статусов", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)

        self.history_text = tk.Text(right_frame, height=10, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Кнопки изменения статуса
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(status_frame, text="← Предыдущий", command=lambda: self.change_task_status("prev")).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(status_frame, text="Следующий →", command=lambda: self.change_task_status("next")).pack(side=tk.LEFT,
                                                                                                           fill=tk.X,
                                                                                                           expand=True,
                                                                                                           padx=5)
        ttk.Button(status_frame, text="Отменить", command=lambda: self.change_task_status("cancel")).pack(side=tk.LEFT,
                                                                                                          fill=tk.X,
                                                                                                          expand=True)

    def load_tasks(self):
        if self.task_manager.load_tasks_from_file(self.current_file):
            self.update_task_list()
        else:
            messagebox.showinfo("Информация", "Файл с задачами не найден или пуст")

    def update_task_list(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.task_manager.get_task_names():
            self.task_listbox.insert(tk.END, task)

    def show_task_details(self, event):
        selection = self.task_listbox.curselection()
        if not selection:
            return

        task_name = self.task_listbox.get(selection[0])
        task = self.task_manager.get_task_by_name(task_name)

        if task:
            # Отображаем детали задачи
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END,
                                     f"Название: {task.name}\n\n"
                                     f"Описание: {task.description}\n\n"
                                     f"Дата создания: {task.date_create}\n"
                                     f"Последнее изменение: {task.date_change.split(',')[0]}")
            self.details_text.config(state=tk.DISABLED)

            # Отображаем историю статусов
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)

            status_history = task.status.split(',')
            date_history = task.date_change.split(',')

            for i in range(min(len(status_history), len(date_history))):
                self.history_text.insert(tk.END, f"{date_history[i]}: {status_history[i]}\n")

            self.history_text.config(state=tk.DISABLED)

    def add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить новую задачу")
        dialog.geometry("400x300")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Название задачи:").pack(pady=(10, 0))
        name_entry = ttk.Entry(dialog)
        name_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(dialog, text="Описание:").pack()
        desc_text = tk.Text(dialog, height=5)
        desc_text.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(dialog, text="Статус:").pack()
        status_var = tk.StringVar(value=TASK_STATUSES[0])
        status_menu = ttk.OptionMenu(dialog, status_var, *TASK_STATUSES)
        status_menu.pack(fill=tk.X, padx=10, pady=(0, 10))

        def save_task():
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()

            if not name:
                messagebox.showerror("Ошибка", "Название задачи не может быть пустым")
                return

            date_now = str(datetime.date.today())
            new_task = Task(
                name=name,
                description=description,
                status=status_var.get(),
                date_create=date_now,
                date_change=date_now
            )

            if self.task_manager.add_task(new_task):
                self.task_manager.save_tasks_to_file(self.current_file)
                self.update_task_list()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Неверный статус задачи")

        ttk.Button(dialog, text="Сохранить", command=save_task).pack(pady=10)

    def delete_task(self):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления")
            return

        task_name = self.task_listbox.get(selection[0])
        if messagebox.askyesno("Подтверждение", f"Удалить задачу '{task_name}'?"):
            task = self.task_manager.get_task_by_name(task_name)
            if task:
                self.task_manager._tasks.remove(task)
                self.task_manager.save_tasks_to_file(self.current_file)
                self.update_task_list()
                self.details_text.config(state=tk.NORMAL)
                self.details_text.delete(1.0, tk.END)
                self.details_text.config(state=tk.DISABLED)
                self.history_text.config(state=tk.NORMAL)
                self.history_text.delete(1.0, tk.END)
                self.history_text.config(state=tk.DISABLED)

    def change_task_status(self, direction):
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для изменения статуса")
            return

        task_name = self.task_listbox.get(selection[0])
        task = self.task_manager.get_task_by_name(task_name)

        if not task:
            return

        current_status = task.status.split(',')[0]
        new_status = None

        if direction == "prev":
            if current_status == "новая":
                messagebox.showinfo("Информация", "Статус не может быть перенесен в предыдущий")
                return
            new_status = TASK_STATUSES[TASK_STATUSES.index(current_status) - 1]
        elif direction == "next":
            if current_status == "выполнено":
                messagebox.showinfo("Информация", "Статус не может быть перенесен в следующий")
                return
            new_status = TASK_STATUSES[TASK_STATUSES.index(current_status) + 1]
        elif direction == "cancel":
            new_status = "отменено"

        if new_status:
            if self.task_manager.update_task_status(task_name, new_status):
                self.task_manager.save_tasks_to_file(self.current_file)
                self.show_task_details(None)  # Обновляем отображение
                messagebox.showinfo("Успех", f"Статус задачи изменен на '{new_status}'")


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()