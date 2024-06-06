import pyttsx3
from tkinter import *
import speech_recognition as sr
import winsound
from taskmanager import *
from PIL import Image, ImageDraw, ImageFont, ImageTk

user_id = "DA4350E8C3196A22713406CE814631462544ABB63E40E32AFBE59FC75FD1E509"
file_path = "DA4350E8C3196A22713406CE814631462544ABB63E40E32AFBE59FC75FD1E509-notes.json"

from PIL import Image, ImageDraw, ImageFont
import json

def create_image_with_progressbar():
    base_width = 400
    base_height = 200

    with open('DA4350E8C3196A22713406CE814631462544ABB63E40E32AFBE59FC75FD1E509-notes.json', 'r',encoding="utf-8") as file:
        data = json.load(file)
        num_records = len(data)


    dynamic_width = base_width
    dynamic_height = base_height + (num_records - 1) * 160  # Увеличиваем высоту на 30 пикселей за каждую запись


    image = Image.new('RGB', (dynamic_width, dynamic_height), color='white')
   

    font = ImageFont.truetype('arial.ttf', 20)


    draw = ImageDraw.Draw(image)


    for i, item in enumerate(data, start=0):

        j = i*160
        draw.text((20, 20 + j), f'Заметка {i+1}', fill='black', font=font)
        draw.text((20, 60 + j), f'{item["text"]}', fill='black', font=font)

        bar_width = dynamic_width-70
        bar_height = 30
        progress_width = int(bar_width * item["progress"] / 100)
        draw.rectangle([20, 100+ j, 20 + progress_width, 100 + bar_height+ j], fill='lightgreen')
        draw.rectangle([20, 100+ j, 20 + bar_width, 100 + bar_height+ j], outline='black', width=2)
        draw.text((20, 140+j), f'{str(item["progress"])}%', fill='black', font=font)

    # Сохраняем изображение
    image.save('task.png')
   






# Функция для озвучивания текста
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()


# Функция распознавания голоса
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Скажите что-нибудь...")
        winsound.Beep(250, 500)
        r.energy_threshold = 500
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 1
        audio = r.listen(source)

        try:
            print("Распознаю...")
            command = r.recognize_google(audio, language="ru-RU")
            print("Вы сказали: " + command)
            return command.lower()
        except sr.UnknownValueError:

            return ''
        except sr.RequestError as e:
            print("Ошибка в работе сервиса распознавания речи; {0}".format(e))
            return ''


a = None
b = None
flag = True


def send_data_to_handler(user_id):
    # Получаем текущее значение state
    request_data = {
        "version": "1.0",
        "session": {
            "user_id": user_id
        },
        "request": {
            "command": '',
            'original_utterance': ''
        },
        "state": {
            "session": {},
        }
    }
    return handler(request_data, None)


def send_data_to_handler1(note_text, user_id, state1, state2):
    # Получаем текущее значение state

    request_data = {
        "version": "1.0",
        "session": {
            "user_id": user_id
        },
        "request": {
            "command": note_text,
            'original_utterance': note_text
        },
        "state": {
            "session": {
                "value1": state1,
                "value2": state2
            },
        }
    }

    return handler(request_data, None)


# Функция для обработки голосовых команд
def process_command():
    global a
    global b
    text = recognize_speech()
    if "запус" in text or "замет" in text or "прилож" in text:
        response = send_data_to_handler(user_id)
        a = response['session_state']['value1']
        b = response['session_state']['value2']
        print(a, b)
        print(response["response"]["text"])
        speak(response["response"]["text"])


def process_command1():
    global a
    global b
    global flag
    text = recognize_speech()
    if "мои заметки" in text or "все заметки" in text:
        root = Tk()
        create_image_with_progressbar()
        image = Image.open("task.png")
        tk_image = ImageTk.PhotoImage(image)
        label = Label(root, image=tk_image)
        label.pack()

        response = send_data_to_handler1(text, user_id, a, b)
        a = response['session_state']['value1']
        b = response['session_state']['value2']
        print(response['response']['text'])
        speak(response['response']['text'])
        root.mainloop()

    else:
        response = send_data_to_handler1(text, user_id, a, b)
        a = response['session_state']['value1']
        b = response['session_state']['value2']
        print(response['response']['text'])
        speak(response['response']['text'])
        if response['response']['end_session'] == "true":
            flag = False


# Основной цикл программы
if __name__ == "__main__":
    speak("Жорвис готов")
    process_command()
    while flag:
        process_command1()
