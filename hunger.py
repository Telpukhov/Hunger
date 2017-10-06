import re
import random
import time
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint

# =====================================================
#                      КЛАСС ИГРЫ
# (характеризует текущее состояние игры и все возможные
#  переходы и методы..................................)
# =====================================================

class game(object):
    def __init__(self):
        self.__open__ = 1
        self.__started__ = 0
        self.__players__ = {}
        self.__player_num__ = 0
        self.__host__ = 0

    def add_player(self, adr, name):
        self.__players__[self.__player_num__] = {
                                        'adr': adr,
                                        'name': name,
                                      }
        self.__player_num__ += 1

# =====================================================
#                 ОБРАБОТЧИК СООБЩЕНИЙ
# =====================================================

def msg_handler(adr, msg, name, chat_id, message_id):
    if adr not in playing_people:
        bot.sendMessage(adr, 'Добро пожаловать в ППЦ!!!', reply_markup=welcome_keybord())



def keyboard_handler(query_id, adr, name, msg, chat_id, message_id):
    # _____________________________________
    #            ПЕРВЫЙ ВХОД
    if msg == 'enter':
        #bot.deleteMessage((chat_id, message_id))
        #bot.sendMessage(adr, 'Добро пожаловать в ППЦ!!!', reply_markup=first_menu())
        playing_people[adr] = (None, chat_id, message_id)
        bot.editMessageText((chat_id, message_id), 'Подключитесь к созданной игре, или создайте сами', reply_markup=first_menu())

    #_____________________________________
    #        СОЗДАНИЕ НОВОЙ ИГРЫ
    if msg == 'new_game':
        host = adr
        games[name] = game()
        games[name].__host__ = host
        games[name].add_player(host, name)
        playing_people[host] = (name, chat_id, message_id)
        hosts[host] = name
        #bot.deleteMessage((chat_id, message_id))
        #bot.sendMessage(adr, 'Поздравляю! Вы создали игру! Теперь вы можете проверить подключенных игроков и начать!', reply_markup=host_keyboard())
        bot.editMessageText((chat_id, message_id), 'Поздравляю! Вы создали игру! Теперь вы можете проверить подключенных игроков и начать!', reply_markup=host_keyboard())

    #_____________________________________
    #    ПРОВЕРКА ПОДКЛЮЧЕННЫХ ИГРОКОВ
    if msg == 'check_players':
        if adr in hosts:
            g = hosts[adr]
            pl = ''
            for i in range(games[g].__player_num__):
                pl += games[g].__players__[i]['name'] + ' '
            bot.answerCallbackQuery(query_id, pl, True)

    # _____________________________________
    #    ВОЗВРАТ В НАЧАЛЬНОЕ МЕНЮ
    if msg == 'back2main_menu':
        if adr in hosts:
            hosts.pop(adr)
            playing_people[adr] = (None, chat_id, message_id)
            games.pop(name)
            #bot.deleteMessage((chat_id, message_id))
            #bot.sendMessage(adr, 'Добро пожаловать в ППЦ!!!', reply_markup=first_menu())
            bot.editMessageText((chat_id, message_id), 'Добро пожаловать в ППЦ!!!', reply_markup=first_menu())

    # _____________________________________
    #      ПОДКЛЮЧЕНИЕ К ИГРЕ
    print(msg)
    if 'connect_' in msg:
        gm2connect = msg[8:]
        playing_people[adr] = (gm2connect,chat_id, message_id)
        games[gm2connect].add_player(adr, name)
        #bot.deleteMessage((chat_id, message_id))
        #bot.sendMessage(adr, 'Вы присоединились к игре ' + gm2connect, reply_markup=first_menu())
        bot.editMessageText((chat_id, message_id), 'Вы присоединились к игре ' + gm2connect, reply_markup=first_menu())


# =====================================================
#                      КЛАВИАТУРЫ
# =====================================================
def first_menu():
    buttons = list()
    buttons.append([InlineKeyboardButton(text='НАЧАТЬ НОВУЮ ИГРУ', callback_data='new_game')])
    buttons.append([InlineKeyboardButton(text='ПРИСОЕДИНИТЬСЯ К ИГРЕ:', callback_data='ignore')])
    for game in sorted(games):
        if games[game].__open__ == 1:
            buttons.append([InlineKeyboardButton(text='  ', callback_data='ignore'), InlineKeyboardButton(text=game, callback_data='connect_'+game)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def host_keyboard():
    buttons = list()
    buttons.append([InlineKeyboardButton(text='ИГРОКИ В ЛОББИ', callback_data='check_players')])
    buttons.append([InlineKeyboardButton(text='СТАРТ', callback_data='ignore')])
    buttons.append([InlineKeyboardButton(text='ОБРАТНО', callback_data='back2main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def welcome_keybord():
    buttons = list()
    buttons.append([InlineKeyboardButton(text='ВОЙТИ', callback_data='enter')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)



# =====================================================
#                 ИНИЦИАЛИЗАЦИЯ БОТА
# =====================================================

global games
global hosts
global playing_people
games = {}
playing_people = {}
hosts = {}
games['Hello'] = game()
games['Slavik'] = game()
games['Slavik'].__open__ = 0
token = '371150676:AAFNeZ7lPfeuftBxUaXuc_Drrj6jgzvW4rA'
bot = telepot.Bot(token)
# Очистка кэша
onstart_update = bot.getUpdates()
if (onstart_update != []):
    update_id = int(onstart_update[-1].get('update_id')) + 1
    bot.getUpdates(offset=update_id)

# =====================================================
#                   ПРИЕМ ПАКЕТОВ
# =====================================================
offset = 0
k = 0
while 1:
    k+=1
    pkgs = bot.getUpdates(offset = offset)
    if pkgs != []: # сообщение/я пришло... обрабатываем
        for pkg in pkgs:    # обрабатываем последовательно
            pprint(pkg)
            if 'message' in pkg: # пришло текстовое сообщение
                adr = pkg['message']['from']['id']
                msg = pkg['message']['text']
                name = pkg['message']['from']['username']
                chat_id = pkg['message']['chat']['id']
                message_id = pkg['message']['message_id']
                msg_handler(adr, msg, name, chat_id, message_id)
            elif 'callback_query' in pkg: # пришла команда с кнопки
                query_id = pkg['callback_query']['id']
                chat_id = pkg['callback_query']['message']['chat']['id']
                name = pkg['callback_query']['message']['chat']['username']
                message_id = pkg['callback_query']['message']['message_id']
                #bot.deleteMessage((chat_id, message_id))
                adr = pkg['callback_query']['from']['id']
                msg = pkg['callback_query']['data']
                keyboard_handler(query_id, adr, name, msg, chat_id, message_id)
        offset = int(pkgs[-1].get('update_id')) + 1
    print('games')
    pprint(games)
    print('playing_people')
    pprint(playing_people)
    print('hosts')
    pprint(hosts)
    #print(k)
    #if k % 13 == 0:
    #    for add in playing_people:
    #        chat_id = playing_people[add][1]
    #        message_id = playing_people[add][2]
    #        bot.deleteMessage((chat_id, message_id))
    time.sleep(1)