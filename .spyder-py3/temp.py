import telebot
from telebot import types
import pandas as pd
import config
#import http.client
import json
from sklearn.model_selection import train_test_split
import conf
import matplotlib.pyplot as plt
import os

bot = telebot.TeleBot(conf.token)

df_subset = None

# ПРИВЕТСВИЕ 
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Правила пользования", callback_data="terms&conditions"))
    lastname = message.from_user.last_name
    if lastname is None:
        bot.send_message(message.chat.id,
                         f"{message.chat.first_name} 👋 \n"
                         , reply_markup=markup)
    else:
        bot.send_message(message.chat.id,
                         f"{message.chat.first_name} {lastname} 👋 \n"
                         , reply_markup=markup)
        
@bot.message_handler(commands=['csv'])
def csv_fail(message):
    bot.send_message(message.chat.id, "Тестовый файл:")
    bot.send_document(message.chat.id, open("C:/Users/vikto/Downloads/titanic.csv", "rb"))
                     
    bot.send_message(message.chat.id,
                         "Тестовый файл можно скачать и использовать для тестирования возможностей бота.\n !Данный бот не осуществляет сбор и хранение данных пользователей!\n Если у вас имеется свой собственный датасет, присылайте файл в чат бота.")
    bot.register_next_step_handler(message, lambda msg: handle_document(msg))
    
def is_csv_file(file_name):
    # Проверяем расширение файла
    return file_name.endswith('.csv')
    
def handle_document(message):
    if message.document:
        file_name = message.document.file_name
        
        # Проверяем, что файл имеет расширение .csv
        if is_csv_file(file_name):
            # Здесь вы можете продолжить обработку CSV файла
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Обработка CSV файла
            try:
                df = pd.read_csv(file_name)
                bot.send_message(message.chat.id,"CSV файл успешно загружен!")
                header = list(df.columns)
                types_element = list(df.dtypes)
                print(df.columns)
                bot.send_message(message.chat.id, "В вашем файле есть параметры:")
                for i in range(len(header)):
                    bot.send_message(message.chat.id, f"\n{i+1}) {header[i]}, {types_element[i]}")
                bot.send_message(message.chat.id, "Введите номера параметров, которые хотите исследовать (Пример: 1 2 3)")
                bot.register_next_step_handler(message, lambda msg: parametr(msg, df))
            except Exception as e:
                print("Ошибка при загрузке CSV файла:", e)
                bot.send_message(message.chat.id, f"Ошибка при загрузке файла: {e}")
        else:
            bot.send_message(message.chat.id, "Пожалуйста, загрузите файл в формате CSV.")
            bot.register_next_step_handler(message, lambda msg: handle_document(msg))
    else:
        bot.send_message(message.chat.id, "Пожалуйста, загрузите документ.")
        bot.register_next_step_handler(message, lambda msg: handle_document(msg))
        
        
def parametr(message, df):
    # Проверяем, что текст сообщения не пуст
    text = message.text.split()
    print(text)
    if text:
        try:
            # Преобразуем введенные номера в целые числа
            indices = [int(i) - 1 for i in text] 
            
            if all(0 <= index < df.shape[1] for index in indices):
                subset = df.iloc[:, indices]  # Извлекаем столбцы по индексам
                print(subset)
            
                if len(subset)> 500:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                    btn1 = types.KeyboardButton("Простая случайная выборка")
                    btn2 = types.KeyboardButton("Систематическая выборка")
                    btn3 = types.KeyboardButton("Стратифицированная (расслоённая) выборка")
                    btn4 = types.KeyboardButton("Кластерная выборка")
                    markup.add(btn1, btn2, btn3, btn4)
                    bot.send_message(message.chat.id, "\n\nКакую выборку сформировать?", reply_markup=markup)
                    bot.register_next_step_handler(message, lambda msg: btn(msg, subset, indices, df))
                else:
                    bot.send_message(message.chat.id, f"{subset}\n\nВаш сабсет готов.\n")
            else:
                bot.send_message(message.chat.id, "Некоторые номера параметров вне допустимого диапазона.")
        
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите корректные номера параметров.")
    else:
        bot.send_message(message.chat.id, "Вы не ввели никаких параметров.")
        
        
def btn(message, subset, indices, df):
    global df_subset
    if (message.text == "Простая случайная выборка"):
        df_subset = subset.sample(n=100)
        print(df_subset)
        bot.send_message(message.chat.id, f"{df_subset}\nМы выбрали 100 случайных строк")
    elif (message.text == "Систематическая выборка"):
        df_subset = subset.iloc[range(0, len(subset), 10)]
        bot.send_message(message.chat.id, f"{df_subset}\nМы выбрали каждую 10-ю строку")
        print(df_subset)
    elif (message.text == "Стратифицированная (расслоённая) выборка"):
        bot.send_message(message.chat.id, "Выберите переменную по которой будет проходить стратификация:")
        header = list(subset.columns)
        types_element = list(subset.dtypes)
        for i in range(len(header)):
            bot.send_message(message.chat.id, f"\n{i+1}) {header[i]}, {types_element[i]}")
            bot.register_next_step_handler(message, lambda msg:  stratificic(msg, subset))
    elif (message.text == "Кластерная выборка"):
        pass
    
    
def stratificic(message, subset):
    global df_subset
    text = message.text.split()      
    if text:
        try:
            # Преобразуем введенные номера в целые числа
            indices = [int(i) - 1 for i in text] 
             
            if all(0 <= index < subset.shape[1] for index in indices):
                df_subset = subset.iloc[:, indices]  # Извлекаем столбцы по индексам
                print(df_subset)
                bot.send_message(message.chat.id, f"{df_subset
        }")
                
        
        finally:
            print(Exception())
                
@bot.message_handler(commands=['clean'])
def clean(message):
    null_subset = df_subset.isnull().sum() #Пропуски
    duplic = df_subset.duplicated().sum() #Дубли
    NA_subset = df_subset.isna().sum() #NA
    
    
    bot.send_message(message.chat.id, f"Пропуски:/n/n{null_subset}")     
    bot.send_message(message.chat.id, f"Повторения:/n/n{duplic}")
    
      
            
            
            
@bot.message_handler(commands=['Descriptive_statistics'])
def opisatelnaya_statistica(message):
    # Вычисление статистик
    mode = df_subset.mode()  # Мода
    median = df_subset.median()  # Медиана
    mean = df_subset.mean()  # Среднее
    std_dev = df_subset.std()  # Стандартное отклонение
    min_value = df_subset.min()  # Минимум
    max_value = df_subset.max()  # Максимум
    
    #ОПИСАТЕЛЬНАЯ СТАТИСТИКА ВЫВОД
    bot.send_message(message.chat.id, f"Мода:\n{mode}")
    bot.send_message(message.chat.id, f"\nМедиана:\n{median}")
    bot.send_message(message.chat.id, f"\nСреднее:\n{mean}")
    bot.send_message(message.chat.id, f"\nСтандартное отклонение:\n{std_dev}")
    bot.send_message(message.chat.id, f"\nМинимум:\n{min_value}")
    bot.send_message(message.chat.id, f"\nМаксимум:\n{max_value}")
            





    
@bot.message_handler(commands=['scatter'])
def scatter_plot(message):
    #ДИАГРАММА РАССЕЯНИЯ
    plt.figure(figsize=(10, 6))
    colors = {'male': 'blue', 'female': 'red'}
    df_subset['Цвет'] = df['Sex'].map(colors)
    subset.dropna()
    plt.scatter(subset[subset.columns[1]], subset[subset.columns[0]], alpha=0.6, c=subset['Цвет'])
    plt.title('Диаграмма рассеяния: ')
    plt.xlabel('')
    plt.ylabel('')
    plt.grid()
    plt.savefig('plot.png')
    with open('plot.png', 'rb') as file:
        bot.send_photo(message.chat.id, photo=file)
    plt.show()
    os.remove('plot.png')

                    
            
        
        

        
        
        
        
        
bot.polling(none_stop=True)