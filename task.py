from dataclasses import dataclass
import json
import datetime
# Объявляем все допустимые статусы
task_status = ["новая", "выполняется", "ревью", "выполнено", "отменено"]

# Создаем класс задач
@dataclass
class Task:
    name: str
    description: str
    status: str
    date_create: str
    date_change: str



# Создаем класс таск-менеджера
class TaskManager():

    # Создаем список, который будет хранить и обрабатывать задачи
    def __init__(self):
        self._tasks = []

    # Функция добавления задачи
    def add_task(self, task: Task):
        while True:
            if task.status in task_status:
                self._tasks.append(task)
                break
            else:
                task.status = input("Такого статуса нет, введите еще раз: ")

    # Функция сохранения списка задач в json файл как список словарей
    def save_tasks_to_file(self, filename: str):
        task_dict = [task.__dict__ for task in self._tasks]
        with open(filename, 'w') as file:
            json.dump(task_dict, file)

    # Функция получения списка задач из файла
    def load_tasks_from_file(self, filename: str):
        with open(filename, 'r') as file:
            task_dict = json.load(file)
        self._tasks = [Task(**task) for task in task_dict]

    # Функция просмотра истории изменения статуса выбранной задачи
    def view_task_history(self, name: str):
        for task in self._tasks:
            if task.name == name:
                print(f"История задачи'{task.name}':")
                status_history = task.status.split(',')
                date_history = task.date_change.split(',')
                print(f" - Текущий статус: {status_history[0]}; Последняя дата изменения: {date_history[0]}")
                for i in range(1, len(status_history)):
                    print(f" - Статус: {status_history[i]}; Дата изменения: {date_history[i]}")
                break
        else:
            print(f"Задача с названием '{name}' не найдена")

    # Функция изменения статуса выбранной задачи
    def update_task_status(self, name: str, filename: str):
            for task in self._tasks:
                if task.name == name:
                    new_status = input("Введите:\n1. Для переноса статуса задачи в предыдущий\n2. Для переноса в следующий\n3. Для переноса в статус отменено\n4. Для переноса из статуса отменено в новая\nДействие: ")
                    date_now = str(datetime.date.today())
                    status_date = str(date_now)
                    now_status = task.status.split(',')[0]
                    if new_status == "1" and  now_status != "новая":
                        new_status = task_status[task_status.index(now_status)-1]
                    elif new_status == "1" and now_status == "новая":
                        print("Статус не может быть перенесен в предыдущий")
                        new_status = ''
                    elif new_status == "2" and now_status != "выполнено":
                        new_status = task_status[task_status.index(now_status)+1]
                    elif new_status == "2" and now_status == "выполнено":
                        print("Статус не может быть перенесен в следующий")
                        new_status = ''
                    elif new_status == "3":
                        new_status = task_status[4]
                    elif new_status == "4" and now_status == "отменено":
                        new_status = task_status[0]
                    else:
                        print("Такой команды нет")
                        new_status = task.status
                    if new_status == '':
                        task.status = task.status
                        task.date_change = task.date_change
                    else:
                        task.status = new_status + ',' + task.status
                        task.date_change = status_date + ',' + task.date_change
                    self.save_tasks_to_file(filename)
                    print(f"Статус: '{task.name}' обновлен. Новый статус: '{new_status}'")
                    break
            else:
                print(f"Задача с названием '{name}' не найдена")