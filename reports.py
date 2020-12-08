import datetime
import os
import codecs
import requests

# Ссылки на json файлы
MAIN_URL = 'https://json.medrating.org/'
USER_URL = f'{MAIN_URL}users'
TASKS_URL = f'{MAIN_URL}todos'
# Максимальное количество попыток подключения
RETRY_MAX_COUNT = 5


def get_http_data(url):  # Функция получения данных из json
    retry_attempt = 1
    while retry_attempt <= RETRY_MAX_COUNT:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            if 400 <= response.status_code < 500:
                print(
                    f'При получении данных с сервера произошла ошибка c http-кодом={int(response.status_code)}. Повтор запроса не нужен.')
                return None
            raise Exception(
                print(f'При получении данных с сервера произошла ошибка c http-кодом={response.status_code}'))
        except Exception as e:
            print(str(e))
            print(f'Ошибка запроса. Выполняем попытку №{retry_attempt}.')
        finally:
            retry_attempt += 1
    print(f'Политика повторов достигла максимального кол-ва попыток ({RETRY_MAX_COUNT}).')
    return None


def get_file_path(username):  # Генерирование имени для файлов
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


def format_tasks(tasks_list):  # Форматирование списка задач пользователя
    formatted_task_list = []
    for task in tasks_list:
        if len(task) > 48:
            formatted_task_list.append(str(f'{task:.48}...\n'))
        else:
            formatted_task_list.append(str(f'{task}\n'))
    return ''.join(formatted_task_list)


# Помещение данных с API в переменную
users_dict = get_http_data(USER_URL)
to_do_dict = get_http_data(TASKS_URL)

# Проверка наличия директории task и ее создание, если отсутствует
directory = 'tasks'
parent_dir = os.getcwd()
path = os.path.join(parent_dir, directory)
if not os.path.exists(path):
    os.mkdir(path)

if users_dict is None or to_do_dict is None:
    print("Нет необходимых данных для формирования отчётов")
    raise SystemExit(1)

# Формирование данных о пользователе и задачах
for user in users_dict:
    completed_tasks = []
    to_do_tasks = []
    tasks_without_users = []
    # Перебор заданий
    for task in to_do_dict:
        # Проверка на принадлежность задачи пользователю по совпадающему id и userId
        if user.get('id') == task.get('userId'):
            task_title = task.get('title')
            if task.get('completed'):
                completed_tasks.append(task_title)
            else:
                to_do_tasks.append(task_title)
        elif not task.get('userId'):
            tasks_without_users.append(task)
    # Запись данных в отчет о пользователе
    try:
        file_path = get_file_path(user.get('username'))
        formatted_completed_task = format_tasks(completed_tasks)
        formatted_to_do_tasks = format_tasks(to_do_tasks)
        text_buffer = (f"Отчет для {user.get('company').get('name')}.\n"
                       f"{user.get('name')} <{user.get('email')}> {datetime.datetime.now(): %d.%m.%Y %H:%M}\n"
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
    except OSError:
        print('Ошибка записи файлов на диск')

print(f'id задач не принадлежащие пользователям: {tasks_without_users}')
