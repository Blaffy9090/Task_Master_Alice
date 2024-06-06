import json
import re
import os
import datetime
import locale

locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')

path = ''

def handler(event, context):
    filepath = path
    if "session" in event and "user_id" in event['session']:
        filepath = filepath + event['session']['user_id'] + '-'
    filepath = filepath + 'notes.json'
    endses = 'false'
    stst = 1  # меняет состояние на 1
    temp = 1
    ast = 1
    re_digits = re.compile(r"\b\d+\b")
    tasks = []
    header = ''

    def create_empty_notes_file():
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([], f)

    # Функция для сохранения заметок в JSON файл
    def save_notes(notes):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=4)

    # Функция для чтения заметок из JSON файла
    def read_notes():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Функция для добавления новой заметки
    def add_note(note_text, progress):
        notes = read_notes()
        today = datetime.datetime.now()
        date = datetime.datetime.strftime(today, '%d %B %Y')
        new_note = {"text": note_text, "progress": progress, "created_at": str(date)}
        notes.append(new_note)
        save_notes(notes)
        return f"Заметка с номером {len(notes)} добавлена."

    # Функция для изменения прогресса заметки
    def update_progress(note_id, progress):
        notes = read_notes()
        try:
            note_id = int(note_id)
            if 0 < note_id <= len(notes):
                notes[note_id - 1]["progress"] = int(progress)
                save_notes(notes)
                return f"Прогресс заметки с номером {note_id} обновлен."
            else:
                return "Заметка не найдена."
        except ValueError:
            return "Неправильный формат номера заметки."

    # Функция для изменения текста заметки
    def update_text(note_id, new_text):
        notes = read_notes()
        try:
            note_id = int(note_id)
            if 0 < note_id <= len(notes):
                notes[note_id - 1]["text"] = new_text
                save_notes(notes)
                return f"Текст заметки с номером {note_id} изменен."
            else:
                return "Заметка не найдена."
        except ValueError:
            return "Неправильный формат номера заметки."

    # Функция для удаления заметки
    def delete_note(note_id):
        notes = read_notes()
        try:
            note_id = int(note_id)
            if 0 < note_id <= len(notes):
                del notes[note_id - 1]
                save_notes(notes)
                return f"Заметка с номером {note_id} удалена."
            else:
                return "Заметка не найдена."
        except ValueError:
            return "Неправильный формат номера заметки."

    # Функция для получения всех заметок
    def get_tasks():
        notes = read_notes()
        items = []
        for i, note in enumerate(notes, start=1):
            item = {
                "title": f"{i}. {note['text']}",
                "description": f"{note['created_at']}" + 5 * ' ' + f"{note['progress']}%"
            }
            items.append(item)
        return items

    # Функция для получения списка заметок в строковом формате
    def get_tasks_blind():
        notes = read_notes()
        task_list = []
        for idx, note in enumerate(notes, start=1):
            task_desc = f"{idx}-я заметка. {note['text']}. Текущий прогресс - {note['progress']}%. Создана  {note['created_at']}"
            task_list.append(task_desc)
        return '\n'.join(task_list)

    if 'state' in event and 'session' in event['state'] and 'value1' in event['state']['session']:
        if event['state']['session']['value1'] == 1:  # 1 состояние - ожидание запроса от пользователя
            if 'request' in event and 'command' in event['request'] and len(event['request']['command']) > 0:
                text = event['request']['command']
                text.lower()

                if 'останов' in text or 'стоп' in text or 'закр' in text:
                    text = 'Пока-пока!'
                    endses = 'true'                    
                else:

                    if 'замет' in text:
                        if text == 'все заметки' or text == 'выведи все заметки':
                            temp = 2
                            header = 'Все заметки'
                            text = header + '\n' + get_tasks_blind()
                            tasks = get_tasks()
                            if len(tasks) == 0:
                                text = 'Нет заметок'
                                temp = 1
                            if len(tasks) > 5:
                                text = header + '\n' + get_more_tasks()
                                temp = 1
                        elif 'созд' in text or 'добав' in text:
                            text = 'Введите текст заметки'
                            stst = 2
                        elif ('прогрес' in text) and ('установи' in text or 'измен' in text or 'обнов' in text):
                            ttmp = re_digits.findall(text)
                            text = 'Не удалось распознать команду'
                            if len(ttmp) == 2:
                                j = int(ttmp[1])
                                if 0 <= j <= 100:
                                    text = update_progress(ttmp[0], j)
                            elif len(ttmp) == 1:
                                text = 'Какой поставить прогресс?'
                                ast = int(ttmp[0])
                                stst = 3
                        elif ('измени' in text or 'поменя' in text or 'перепиш' in text or 'обнови' in text) and 'текст' in text:
                            ttmp = re_digits.findall(text)
                            if len(ttmp) == 1:
                                text = 'Какой сделать текст?'
                                ast = int(ttmp[0])
                                stst = 4
                            else:
                                text = 'Не удалось распознать команду'
                        elif 'чита' in text or 'каж' in text or 'каз' in text or 'выведи' in text:
                            temp = 2
                            if 'все' in text:
                                header = 'Все заметки'
                                text = header + '\n' + get_tasks_blind()
                                tasks = get_tasks()
                                if len(tasks) == 0:
                                    text = 'Нет заметок'
                                    temp = 1
                                if len(tasks) > 5:
                                    text = header + '\n' + get_more_tasks()
                                    temp = 1
                            else:
                                ttmp = re_digits.findall(text)
                                if len(ttmp) > 0:
                                    text = read_note_blind(ttmp[0])
                                    header = 'Заметка ' + ttmp[0]
                                    tasks = [read_note(ttmp[0])]
                                else:
                                    text = 'Не удалось распознать команду'
                                    temp = 1
                        elif 'удали' in text:
                            temp = False
                            if 'все' in text:
                                text = 'Все заметки удалены'
                                create_empty_notes_file()
                                temp = 1
                            else:
                                ttmp = re_digits.findall(text)
                                text = delete_note(ttmp[0])
                                header = 'Новый список заметок:'
                                tasks = get_tasks()
                                if len(tasks) == 0:
                                    text = 'Нет заметок'
                                    temp = 1
                                if len(tasks) > 5:
                                    text = header + '\n' + get_more_tasks()
                                    temp = 1
                        else:
                            text = 'Не удалось распознать команду'
                    else:
                        text = 'Не удалось распознать команду'
            else:
                text = 'Не удалось распознать команду'

        elif event['state']['session']['value1'] == 2:  # 2 состояние - ввод текста заметки
            if 'request' in event and 'command' in event['request'] and len(event['request']['command']) > 0:
                text = event['request']['original_utterance']
                text = add_note(text, 0)  # Передаем текущий список заметок
                stst = 1
            else:
                text = 'Назовите корректную фразу!'
                stst = 2            

        elif event['state']['session']['value1'] == 3:  # 3 состояние - изменение прогресса заметки
            if 'request' in event and 'command' in event['request'] and len(event['request']['command']) > 0:
                text = event['request']['command']
                ttmp = re_digits.findall(text)
                if len(ttmp) > 0:
                    j = int(ttmp[0])
                    if 0 <= j <= 100:
                        text = update_progress(event['state']['session']['value2'], j)
                        stst = 1
                    else:
                        text = 'Назовите корректное значение!'
                        ast = event['state']['session']['value2']
                        stst = 3
                else:
                    text = 'Не удалось распознать команду'
            else:
                text = 'Назовите корректное значение!'
                ast = event['state']['session']['value2']
                stst = 3 

        elif event['state']['session']['value1'] == 4:  # 4 состояние - изменение текста заметки
            if 'request' in event and 'command' in event['request'] and len(event['request']['command']) > 0:
                text = event['request']['command']
                if len(text) > 0:
                    new_text = event['request']['original_utterance']
                    text = update_text(event['state']['session']['value2'], new_text)
                    stst = 1
                else:
                    text = 'Не удалось распознать команду'
                    temp = 1
            else:
                text = 'Не удалось распознать команду'
                temp = 1
        else:
            text = 'Не удалось распознать команду'
            temp = 1
    else:
        text = "Добро пожаловать в создателя заметок!"
        temp = 1
        if os.path.exists(filepath):
            pass
        else:
            create_empty_notes_file()

    if temp == 1:
        return {
            'version': event['version'],
            'session': event['session'],
            'response': {
                'text': text,
                'end_session': endses
            },
            "session_state": {
                "value1": stst,
                'value2': ast
            },
        }
    else:
        return {
            'version': event['version'],
            'session': event['session'],
            'response': {
                'text': text,
                "card": {
                    "type": 'ItemsList',
                    "header": {
                        'text': header
                    },
                    'items': tasks
                },
                # Don't finish the session after this response.
                'end_session': endses
            },
            "session_state": {
                "value1": stst,
                'value2': ast
            },
        }
