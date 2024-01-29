from task import *
import argparse
import datetime
from colorama import init, Fore, Back, Style
init()


# Получение имени файла
parser = argparse.ArgumentParser(description="Имя файла с задачами")
parser.add_argument('filename', type=str)
args = parser.parse_args()

# Объявляем таск-менеджер и загружаем введёный файл
task_manager = TaskManager()
task_manager.load_tasks_from_file(args.filename)

while True:
    # Начальное меню
    print(Fore.YELLOW + "------------------------------------")
    print("""1. Просмотреть задачу\n2. Обновить статус задачи\n3. Сохранить новую задачу в файл\n4. Выйти""")

    flag = input("Выберите действие: ")
    print("------------------------------------")

    # Просмотр истории
    if flag == "1":
        name = input("Введите название задачи: ")
        task_manager.view_task_history(name)

    # Обновление статуса
    elif flag == "2":
        name = input("Введите название задачи: ")

        task_manager.update_task_status(name, args.filename)

    # Создание новой задачи
    elif flag == "3":
        date_now = str(datetime.date.today())
        new_task = Task(input("Введите название новой задачи: "),
                        input("Введите описание задачи: "),
                        input("Введите статус новой задачи (новая, выполняется, ревью, выполнено или отменено): "),
                        date_now,
                        date_now)
        task_manager.add_task(new_task)
        task_manager.save_tasks_to_file(args.filename)
    # Выход из программы
    elif flag == "4":
        break

    else:
        print("Неизвестная команда")
