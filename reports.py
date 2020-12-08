import json
import datetime
import os
import codecs
import requests

# Проверка наличия директории task и ее создание, если отсутствует
directory = 'tasks'
parent_dir = os.getcwd()
path = os.path.join(parent_dir, directory)
if not os.path.exists(path):
    os.mkdir(path)


def get_file_path(username):
    new_file = f'{username}.txt'
    new_file_path = os.path.join(path, new_file)
    # Проверка существования файла с таким именем
    if os.path.isfile(new_file_path):
        # Если существует уже, то переименовать согласно требованиям старый файл
        date_of_creation = os.path.getmtime(new_file_path)
        old_file_prefix = str(
            f'old_{user.get("username")}_{datetime.datetime.fromtimestamp(date_of_creation).strftime("%Y-%m-%dT%H:%M")}')
        name_for_old_file = f'{old_file_prefix}.txt'
        counter = 2
        while os.path.isfile(os.path.join(path, name_for_old_file)):
            name_for_old_file = f'{old_file_prefix}_{counter}.txt'
            counter += 1
        old_file_path = os.path.join(path, name_for_old_file)
        os.rename(new_file_path, old_file_path)
    return new_file_path


def format_tasks(tasksList):
    formatted_task_list = []
    for task in tasksList:
        if len(task) > 48:
            formatted_task_list.append(str(f'{task:.48}...\n'))
        else:
            formatted_task_list.append(str(f'{task}\n'))
    return ''.join(formatted_task_list)

# Получение json-файлов
user_url = 'https://json.medrating.org/users'
tasks_url = 'https://json.medrating.org/todos'
users = requests.get(user_url)
tasks = requests.get(tasks_url)
users_dict = users.json()
to_do_dict = tasks.json()


# Перебор всех пользователей
for user in users_dict:
    completed_tasks = []
    to_do_tasks = []
    date_of_creation = ''
    tasks_without_users = []
    # Перебор заданий
    for task in to_do_dict:
        # Проверка на принадлежность задачи пользователю по совпадающему id и userId
        if user.get('id') == task.get('userId'):
            task_title = task.get('title')
            if len(task_title) > 48:
                task_title = task.get('title')
            if task.get('completed'):
                completed_tasks.append(task_title)
            else:
                to_do_tasks.append(task_title)
        elif not task.get('userId'):
            tasks_without_users.append(task)


    # Проверка на наличие заполненных данных о пользователе
    try:
        file_path = get_file_path(user.get('username'))
        formatted_completed_task = format_tasks(completed_tasks)
        formatted_to_do_tasks = format_tasks(to_do_tasks)
        text_buffer = (f"Отчет для {user.get('company').get('name')}.\n"
                       f"{user.get('name')} <{user.get('email')}> {date_of_creation}\n"
                       f"Всего задач: {len(completed_tasks + to_do_tasks)}\n\n"
                       f"Завершенные задачи({len(completed_tasks)}): \n"
                       f"{formatted_completed_task}\n\n"
                       f"Оставшиеся задачи({len(to_do_tasks)}):\n"
                       f"{formatted_to_do_tasks}")
        report = codecs.open(file_path, 'w', 'utf-8')
        report.write(text_buffer)
        report.close()
    except AttributeError:
        print(f' Пользователь с id = {user.get("id")} не имеет нужных для формирования отчета аттрибутов')
print(tasks_without_users)