import telebot
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, peak_widths
from telebot import types

bot = telebot.TeleBot("7506589144:AAGRizkaoezI-KY0oAztgYjaDROi-scG4sQ")

#задание 1======================================================================================================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот-помощник в физике. Я могу помочь с переводом частоты излучения в длину волны, вычислением резонанса спектра и другими функциями. Просто напиши мне, что тебе нужно!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Спасибо что выбрал меня! Вот все мои команды: \n/start - запуск бота, начальная команада; \n/help - меню помощи с полезными командами; \n/convert  - перевод частоты в длину волны; \n/resonancespectrum - вычисление по спектру в формате .txt положения резонанса и его ширины на полувысоте и вывод пользователю; \n/calculatefluence - вычисление флюенса лазерной системы по средней мощности; \n/otziv - опрос пользователя о том, насколько он доволен опытом использования ассистента и каких функций ему не хватает; \n/calculator - полностью функциональный калькулятор, сделанный с помощью кнопок")

@bot.message_handler(commands=['convert'])
def convert_frequency(message):
    bot.reply_to(message, "Введите частоту излучения (в Гц):")
    bot.register_next_step_handler(message, convert_frequency_step)

#задание 2 ====================================================================================================================================

def convert_frequency_step(message):
    try:
        frequency = float(message.text)
        wavelength = 3e8 / frequency
        bot.reply_to(message, f"Длина волны равна {wavelength} м")
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите число")

#задание 3=======================================================================================================================================

@bot.message_handler(commands=['resonancespectrum'])
def resonance_spectrum(message):
    spectrum = np.loadtxt('your_spectrum.txt') # загрузка спектра из файла

    wavelengths = spectrum[:, 0]
    intensities = spectrum[:, 1]

    peaks, _ = find_peaks(intensities)
    results_half = peak_widths(intensities, peaks, rel_height=0.5)

    peak_index = results_half[2][0]
    peak_height = intensities[peak_index]
    peak_width = results_half[0][0]

    # Построение графика
    plt.plot(wavelengths, intensities)
    plt.scatter(wavelengths[peak_index], peak_height, color='red', label='Resonance Peak')
    plt.hlines(peak_height/2, wavelengths[int(results_half[3][0])], wavelengths[int(results_half[4][0])], color='red', linestyles='dashed', label='Half width at half maximum')
    plt.legend()
    plt.xlabel('Wavelength')
    plt.ylabel('Intensity')
    plt.title('Resonance Spectrum')
    plt.show()

    bot.send_message(message.chat.id, f"Длина волны резонансного пика: {wavelengths[peak_index]}\nШирина резонансного пика при половинном максимуме: {peak_width}")

# задание 4 ====================================================================================================================================

@bot.message_handler(commands=['calculatefluence'])
def calculate_fluence(message):
    bot.send_message(message.chat.id, "Введите среднюю мощность лазерной системы в Вт:")
    bot.register_next_step_handler(message, get_power)

def get_power(message):
    try:
        power = float(message.text)
        fluence = power * 1000 / 1e-3
        bot.send_message(message.chat.id, f"Флюенс лазерной системы равен {fluence} Дж/см^2")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите числовое значение.")

#дополнительно(калькулятор) =====================================================================================================================

value =''
old_value = ''
keyboard = telebot.types.InlineKeyboardMarkup()
keyboard.row(telebot.types.InlineKeyboardButton(' ', callback_data='no'), telebot.types.InlineKeyboardButton('C', callback_data='C'), telebot.types.InlineKeyboardButton('<=', callback_data='<='), telebot.types.InlineKeyboardButton('/', callback_data='/'))
keyboard.row(telebot.types.InlineKeyboardButton('7', callback_data='7'), telebot.types.InlineKeyboardButton('8', callback_data='8'), telebot.types.InlineKeyboardButton('9', callback_data='<='), telebot.types.InlineKeyboardButton('*', callback_data='*'))
keyboard.row(telebot.types.InlineKeyboardButton('4', callback_data='4'), telebot.types.InlineKeyboardButton('5', callback_data='5'), telebot.types.InlineKeyboardButton('6', callback_data='<='), telebot.types.InlineKeyboardButton('-', callback_data='-'))
keyboard.row(telebot.types.InlineKeyboardButton('1', callback_data='1'), telebot.types.InlineKeyboardButton('2', callback_data='2'), telebot.types.InlineKeyboardButton('3', callback_data='3'), telebot.types.InlineKeyboardButton('+', callback_data='+'))
keyboard.row(telebot.types.InlineKeyboardButton(' ', callback_data='no'), telebot.types.InlineKeyboardButton('0', callback_data='0'), telebot.types.InlineKeyboardButton(',', callback_data='.'), telebot.types.InlineKeyboardButton('=', callback_data='='))

@bot.message_handler(commands=['calculator'])
def calc_message(message):
    global value
    if value == '':
        bot.send_message(message.from_user.id, '0', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, value, reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: True)
def callback_func(query):
    global value, old_value
    data = query.data
    if data =='no':
        pass
    elif data == 'C':
        value = ''
    elif data == '<=':
        if value != '':
            value = value[:len(value)-1]
    elif data == '=':
        try:
            value = str(eval(value))
        except:
            value = 'Ошибка!'
    else:
        value += data
        
    if (value != old_value and value != '') or (0 != old_value and value == ''):
        if value == '':
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text = '0', reply_markup=keyboard)
            old_value = 0
        else:
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text = value, reply_markup=keyboard)
            old_value = value
    old_value = value
    if value == 'Ошибка!' : value = ''
#задание 5 =======================================================================================================================================

@bot.message_handler(commands=['otziv'])        
def otz_message(message):
    bot.send_message(message.chat.id, 'Привет! Оставьте ваш отзыв:')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    with open('reviews.txt', 'a') as file:
        file.write(f'{message.chat.id}: {message.text}\n')
    
    bot.send_message(message.chat.id, 'Отзыв успешно отправлен, спасибо!')

    developer_chat_id = '5114615663'#айди моего чата, замените, также отзыв приходит в специальную текстовую папку, которая создаётся автоматически
    bot.send_message(developer_chat_id, f'Новый отзыв от пользователя {message.chat.id}:\n{message.text}')

#==================================================================================================================================================    

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Извини, я пока не могу обрабатывать такие запросы. Но ты всегда можешь обратиться за помощью по физике!")

bot.polling()