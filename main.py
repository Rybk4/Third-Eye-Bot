import os
import telebot
from telebot import types
from scripts.detect_obj import detect_objects_f
import sys
from scripts.train_model import train_model_f

bot = telebot.TeleBot("token")

data_dir = "asd"

def load_classes(filename):
    with open(filename, 'r') as file:
        classes = file.read().splitlines()
    return classes

# Путь к файлу с классами
classes_file = "data\class_names.txt"
# Загрузка списка классов из файла
existing_classes = load_classes(classes_file)




# Список доступных команд
available_commands = [
    "/start - начать диалог с ботом",
    "/help - отобразить список доступных команд",
    "/detect - определить объект на фотографии",
    "/train - обучить модель чему-то новому"
]

# Dictionary to store the class name chosen by each user for training
user_train_classes = {}

# Создание кастомной клавиатуры с кнопками для готовых команд
def create_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
 
    help_button = types.KeyboardButton("Помощь")
    detect_button = types.KeyboardButton("Определить объект")
    train_button = types.KeyboardButton("Тренировка")
    keyboard.add(  help_button)
    keyboard.add(detect_button, train_button)
    return keyboard





# Обработчик нажатия кнопки "Тренировка"
@bot.message_handler(func=lambda message: message.text == "Тренировка")
def train_model_command(message):
    bot.send_message(message.chat.id, "Чему вы хотите обучить бота? (Введите название животного или объекта)")
    bot.register_next_step_handler(message, handle_train_input)

 


# Обработчик нажатия кнопки "Начать"
@bot.message_handler(func=lambda message: message.text == "Начать")
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет, я бот, который поможет тебе определить объект на фотографии",
                     reply_markup=create_keyboard())



# Обработчик нажатия кнопки "Помощь"
@bot.message_handler(func=lambda message: message.text == "Помощь")
def send_help(message):
    bot.send_message(message.chat.id, "\n".join(available_commands), reply_markup=create_keyboard())




# Обработчик нажатия кнопки "Определить объект"
@bot.message_handler(func=lambda message: message.text == "Определить объект")
def detect_objects(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию, чтобы определить объекты на ней.",
                     reply_markup=create_keyboard())





# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет, я бот, который поможет тебе определить объект на фотографии",
                     reply_markup=create_keyboard())


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "\n".join(available_commands), reply_markup=create_keyboard())


# Обработчик команды /detect
@bot.message_handler(commands=['detect'])
def detect_objects(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте фотографию, чтобы определить объекты на ней.",
                     reply_markup=create_keyboard())





# Обработчик пустой команды
@bot.message_handler(commands=[])
def show_available_commands(message):
    bot.send_message(message.chat.id, "\n".join(available_commands), reply_markup=create_keyboard())






# Обработчик команды /train
@bot.message_handler(commands=['train'])
def train_model_command(message):
    bot.send_message(message.chat.id, "Чему вы хотите обучить бота? (Введите название животного или объекта)")
    bot.register_next_step_handler(message, handle_train_input)




def handle_train_input(message):
    class_name = message.text.lower().capitalize()
    user_train_classes[message.chat.id] = class_name
    # Проверяем, существует ли уже такой класс
    if class_name in existing_classes:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        cancel_button = types.KeyboardButton("Отмена")
        add_photo_button = types.KeyboardButton("Добавить фото")
        markup.add(cancel_button, add_photo_button)
        bot.send_message(message.chat.id, f"Модель уже обучена на классе '{class_name}'.", reply_markup=markup)
    else:
        # Если класса нет, добавляем его в список и создаем папку
       
        class_dir = os.path.join(data_dir, class_name)
        os.makedirs(class_dir)
        bot.send_message(message.chat.id, f"Создана новая папка для обучения на классе '{class_name}'. ")
        bot.send_message(message.chat.id, "Отправьте фотографии для обучения.")
        bot.register_next_step_handler(message, lambda m: handle_photos_for_training(m, class_name))





# Обработчик нажатия кнопки "Добавить фото"
@bot.message_handler(func=lambda message: message.text == "Добавить фото")
def add_photos(message):
  
    class_name = user_train_classes.get(message.chat.id)
    if class_name:

        new_keyboard = types.ReplyKeyboardMarkup(row_width=2 , resize_keyboard=True, one_time_keyboard=True)
        cancel_button = types.KeyboardButton("Отмена")
        train_btn = types.KeyboardButton("Обучить")
        new_keyboard.add(cancel_button, train_btn)

        bot.send_message(message.chat.id, "Отправьте фотографии для обучения. Когда закончите, нажмите кнопку 'Обучить'." ,reply_markup=new_keyboard)

        bot.register_next_step_handler(message, lambda m: handle_photos_for_training(m, class_name))
    else:
        bot.send_message(message.chat.id, "Ошибка: Не удалось найти класс для обучения.")

def handle_photos_for_training(message, class_name):
    # Создаем папку для данного класса, если она еще не существует

    new_keyboard = types.ReplyKeyboardMarkup(row_width=2 , resize_keyboard=True, one_time_keyboard=True)
    cancel_button = types.KeyboardButton("Отмена")
    train_btn = types.KeyboardButton("Обучить")
    new_keyboard.add(cancel_button, train_btn)
     
    class_dir = os.path.join(data_dir, class_name)
    if not os.path.exists(class_dir):
        os.makedirs(class_dir)
    
    # Проверяем, есть ли в сообщении фото
    if message.photo:
        # Берем только первое фото из сообщения
        photo = message.photo[-1]
        
        file_id = photo.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        downloaded_file = bot.download_file(file_path)
        file_extension = file_path.split('.')[-1]

        # Генерируем уникальное имя файла
        filename = f"{file_id}.{file_extension}"
        photo_path = os.path.join(class_dir, filename)
        
        # Сохраняем фото в папку класса
        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        bot.send_message(message.chat.id, "Фотография добавлена для обучения. Отправьте еще фотографию или нажмите 'Обучить'.",reply_markup=new_keyboard)
        bot.register_next_step_handler(message, lambda m: handle_photos_for_training(m, class_name))  
    elif message.text == "Обучить":
        train_model(message) 
    elif message.text == "Отмена":
        cancel(message)




def train_model(message):
     
    bot.send_message(message.chat.id, "Начато обучение модели.")
    
    train_model_f()

    bot.send_message(message.chat.id, "Модель обучена на предоставленных фотографиях.")
    restart_program()






# Обработчик нажатия кнопки "Отмена"
@bot.message_handler(func=lambda message: message.text == "Отмена")
def cancel(message):
    bot.send_message(message.chat.id, "Действие отменено.", reply_markup=types.ReplyKeyboardRemove())





# Обработчик фотографий для определения объектов
@bot.message_handler(content_types=['photo'])
def handle_photo_for_detection(message):
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_path = file_info.file_path

    downloaded_file = bot.download_file(file_path)

    photo_dir = "photos"
    if not os.path.exists(photo_dir):
        os.makedirs(photo_dir)

    file_extension = file_path.split('.')[-1]

    # Полный путь к сохраняемой фотографии
    photo_path = os.path.join(photo_dir, f"{file_id}.{file_extension}")
    with open(photo_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    object_name, confidence1 = detect_objects_f(photo_path)
    
    confidence = round(confidence1 , 1)
    print(confidence)
    if(confidence<=0.5):
        os.remove(photo_path)
        bot.send_message(message.chat.id, f"Могу предположить что объект на фото {object_name}",
                     reply_markup=create_keyboard())
    else:
        os.remove(photo_path)
        bot.send_message(message.chat.id, f"Объект на фото {object_name} с вероятностью: {confidence}",
                        reply_markup=create_keyboard())


def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)


bot.infinity_polling()
