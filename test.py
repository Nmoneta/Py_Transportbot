import telebot
import json
from telebot import types
import parse
bot = telebot.TeleBot('5701694088:AAGmCXCuS0ZLutCiyyrqN_Z90HolscmT71o')

def markup_Reply_transport_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    bus_button = types.KeyboardButton("Автобус")
    tramway_button = types.KeyboardButton("Трамвай")
    trolleybus_button = types.KeyboardButton("Троллейбус")
    button_back = types.KeyboardButton("Назад")
    markup.add(button_back)
    markup.row(bus_button, trolleybus_button, tramway_button)
    return markup

def markup_Reply_num_transport_button(type_transport):
    with open(f"data/{type_transport}.json") as file:
        data = json.load(file)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_back = types.KeyboardButton("Назад")
    markup.add(button_back)
    button_list = []
    for i in data['response']:
        button = types.KeyboardButton(i)
        button_list.append(button)
    markup.row(*button_list)
    return markup

def text_data_transport_position(dict):
    if(len(dict)>0):
        output_str = []
        for item in dict:
            if(item["Position"] == "Between_Stops"):
                str_data = f'✅️Транспорт находится между остановками {item["Stops"][0]} и {item["Stops"][1]}. Маршрут едет до остановки {item["Ending_Stops"]}.'
            elif (item["Position"] == "Stops"): str_data = f'✅️Транспорт находится на остановке {item["Stops"]}. Маршрут едет {item["Ending_Stops"]}.'
            output_str.append(str_data)
        output_str = ' \n'.join(output_str)
        return output_str
    else: return 'На данный момент этот вид транспорта недоступен.'

#стартовая команда, создает одну кнопку для активации основного кода
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    route = types.KeyboardButton("Тип транспорта")
    markup.add(route)
    bot.send_message(message.chat.id,"Начало работы с ботом",reply_markup=markup)

#Исходя из json файла выводит вид доступного транспорта и создает для них кнопки
@bot.message_handler(content_types=['text'])
def choiсe_transport_type(message):
    message_b = ''
    with open('all_categories_dict.json', 'r') as file:
        data = json.load(file)
    str_output = ', \n'.join(data.keys())
    mess_text = message.text
    if(mess_text == 'Тип транспорта'):
        markup = markup_Reply_transport_button()
        bot.send_message(message.chat.id,f"Вид транспорта:\n{str_output}",reply_markup=markup)

    if(mess_text in"Автобус" or mess_text in "Троллейбус" or mess_text in "Трамвай"):
        for i in str_output.split(","):
            i = i.replace('\n', '').strip()
            if i.lower() == mess_text.lower():
                str=f'data/{i}.json'
                with open(str, "r") as file:
                    data = json.load(file)
                str_output_number = ', '.join(data['response'].keys())
                markup = markup_Reply_num_transport_button(i)
                message_b = mess_text
                bot.send_message(message.chat.id,f"Все номера({mess_text}):\n{str_output_number}\nВыберите необходимый\nНеобходимо подождать несколько секунд",reply_markup=markup)
                with open('background_message.json',"w") as file:
                    json.dump(message.json,file,indent=4,ensure_ascii=False)
                break

    if(message.text.isdigit()):
        with open('background_message.json', "r") as file:
            data = json.load(file)
        if (data['text'] in"Автобус" or data['text'] in "Троллейбус" or data['text'] in "Трамвай"):
            dict = parse.position(message.text, data['text'])
            text = text_data_transport_position(dict)
            markup = markup_Reply_transport_button()
            bot.send_message(message.chat.id, f"Список доступного транспорта:\n {text}", reply_markup=markup)
        else:
            markup = markup_Reply_transport_button()
            bot.send_message(message.chat.id, f"Введите необходимый вид транспорта:\n{str_output}",reply_markup=markup)


bot.polling(none_stop=True)