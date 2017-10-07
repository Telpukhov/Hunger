import re
import random
import copy
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
        self.__host__ = 0
        self.__ppz__ = []
        self.__timer__ = 0
        self.__raund__ = 0
        self.__votes__ = {}
    def add_player(self, adr, name, chat_id, message_id):
        self.__players__[adr] = (name, chat_id, message_id)

    def say2all(self):
        for player in self.__players__:
            main_window(hosts[self.__host__], player)


    def say2ppz(self, text, keyboard):
        for player in self.__players__:
            name = self.__players__[player][0]
            chat_id = self.__players__[player][1]
            message_id = self.__players__[player][2]
            if player in self.__ppz__:
                bot.editMessageText((chat_id, message_id), text,
                                reply_markup=keyboard)

    def say2citizen(self, text, keyboard):
        for player in self.__players__:
            name = self.__players__[player][0]
            chat_id = self.__players__[player][1]
            message_id = self.__players__[player][2]
            if player not in self.__ppz__:
                bot.editMessageText((chat_id, message_id), text,
                                reply_markup=keyboard)

    def end_round(self):
        self.__raund__ += 1
        self.__timer__ = 0

        for player in self.__players__:
            self.__votes__[player] = None
        self.say2all()

    def end_game(self):
        # перекидываем людей из игры в лобби
        for player in self.__players__:
            tmp = in_game.pop(player)
            in_lobby[player] = (None, tmp[1], tmp[2])
        finished_games.append(hosts.pop(self.__host__))
        # обновляем лобби
        for player in in_lobby:
            if player not in hosts:
                first_menu(player)

    def process(self):
        if self.__started__ == 1:
            self.__timer__ += 1
            if self.__timer__ > 10:
                self.end_round()
            if self.__raund__ > 10:
                self.end_game()
    def __str__(self):
        pprint(self.__players__)
        return("open: " + str(self.__open__) + "\nstarted: " + str(self.__started__) + "\nhost: " + str(self.__host__))




def msg_handler(adr, msg, name, chat_id, message_id):
    if adr not in in_lobby:
        bot.sendMessage(adr, 'Добро пожаловать в ППЦ!!!', reply_markup=welcome_keybord())



def keyboard_handler(query_id, adr, name, msg, chat_id, message_id):

    # =====================================================
    #                 ОБРАБОТЧИК МЕНЮ
    # =====================================================

    # _____________________________________
    #            ПЕРВЫЙ ВХОД
    if msg == 'enter':
        in_lobby[adr] = (None, chat_id, message_id)
        first_menu(adr)

    #_____________________________________
    #        СОЗДАНИЕ НОВОЙ ИГРЫ
    if msg == 'new_game':
        host = adr
        games[name] = game()
        games[name].__host__ = host
        games[name].add_player(host, name, chat_id, message_id)
        in_lobby[host] = (name, chat_id, message_id)
        hosts[host] = name

        bot.editMessageText((chat_id, message_id), 'Поздравляю! Вы создали игру! Теперь вы можете проверить подключенных игроков и начать!', reply_markup=host_keyboard())
        for player in in_lobby: # обновляем лобби
            if player not in hosts:
                first_menu(player)

    #_____________________________________
    #    ПРОВЕРКА ПОДКЛЮЧЕННЫХ ИГРОКОВ
    if msg == 'check_players':
        if adr in hosts:
            g = hosts[adr]
            pl = ''
            for adr in games[g].__players__:
                pl += games[g].__players__[adr][0] + '   '
            bot.answerCallbackQuery(query_id, pl, True)

    # _____________________________________
    #    ВОЗВРАТ В НАЧАЛЬНОЕ МЕНЮ
    if msg == 'back2main_menu':
        if adr in hosts:
            hosts.pop(adr) # убираем из хостов
            games.pop(name) # удаляем игру
            in_lobby[adr] = (None, chat_id, message_id) # обновляем состояние
            for player in in_lobby: # убираем игру у всех кто в главном меню
                if player not in hosts:
                    if in_lobby[player][0] == name: # у тех кто в этой игре - кикаем
                        in_lobby[player] = (None, in_lobby[player][1], in_lobby[player][2])
                    first_menu(player)


    # _____________________________________
    #      ПОДКЛЮЧЕНИЕ К ИГРЕ
    print(msg)
    if 'connect_' in msg:
        gm2connect = msg[8:]
        if in_lobby[adr][0] != None: # если уже был в чьей-то игре
            games[in_lobby[adr][0]].__players__.pop(adr) # кикаем из нее
        in_lobby[adr] = (gm2connect,chat_id, message_id) # меняем состояние

        games[gm2connect].add_player(adr, name, chat_id, message_id) # добавляем в игру

        first_menu(adr)

    # _____________________________________
    #              СТАРТ ИГРЫ
    if msg == 'start_game':
        # перекидываем людей из лоби в игру
        for player in in_lobby:
            if in_lobby[player][0] == name:
                in_game[player] = in_lobby[player]
        for player in games[name].__players__:
            in_lobby.pop(player)
        # закрываем игру
        games[name].__open__ = 0
        # начинаем игру
        games[name].__started__ = 1
        # выбираем ppz
        games[name].__ppz__ = random.sample(sorted(games[name].__players__),2)
        # первый раунд
        games[name].__raund__ = 1
        for player in games[name].__players__:
            games[name].__votes__[player] = None
        # обновляем лобби
        for player in in_lobby:
            if player not in hosts:
                first_menu(player)
        games[name].say2all()


    # =====================================================
    #                 ОБРАБОТЧИК ИГРЫ
    # =====================================================

    if 'vote_' in msg:
        vote = int(msg[5:])
        g = in_game[adr][0]
        games[g].__votes__[adr] = vote
        games[g].say2all()

# =====================================================
#                      КЛАВИАТУРЫ
# =====================================================
def first_menu(player):
    buttons = list()
    buttons.append([InlineKeyboardButton(text='НАЧАТЬ НОВУЮ ИГРУ', callback_data='new_game')])
    buttons.append([InlineKeyboardButton(text='ПРИСОЕДИНИТЬСЯ К ИГРЕ:', callback_data='ignore')])
    for game in sorted(games):
        if games[game].__open__ == 1:
            buttons.append([InlineKeyboardButton(text='  ', callback_data='ignore'), InlineKeyboardButton(text=game, callback_data='connect_'+game)])

    if in_lobby[player][0] == None:
        text = 'Подключитесь к созданной игре, или создайте сами'
    else:
        text = 'Вы присоединились к игре ' + in_lobby[player][0]
    bot.editMessageText((in_lobby[player][1], in_lobby[player][2]), text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

def host_keyboard():
    buttons = list()
    buttons.append([InlineKeyboardButton(text='ИГРОКИ В ЛОББИ', callback_data='check_players')])
    buttons.append([InlineKeyboardButton(text='СТАРТ', callback_data='start_game')])
    buttons.append([InlineKeyboardButton(text='ОБРАТНО', callback_data='back2main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def welcome_keybord():
    buttons = list()
    buttons.append([InlineKeyboardButton(text='ВОЙТИ', callback_data='enter')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def main_window(game_id, player_id):
    buttons = list()
    buttons.append([InlineKeyboardButton(text='РАУНД', callback_data='ignore'), InlineKeyboardButton(text='  ', callback_data='ignore'), InlineKeyboardButton(text=str(games[game_id].__raund__), callback_data='ignore') ])
    buttons.append([InlineKeyboardButton(text='ВРЕМЯ:', callback_data='ignore'), InlineKeyboardButton(text='  ', callback_data='ignore'), InlineKeyboardButton(text=str(games[game_id].__timer__), callback_data='ignore')])
    buttons.append([InlineKeyboardButton(text='ГОЛОСОВАТЬ:', callback_data='ignore')])
    for player in games[game_id].__players__:
        if player != player_id:
            buttons.append([InlineKeyboardButton(text='  ', callback_data='ignore'), InlineKeyboardButton(text=str(games[game_id].__players__[player][0]), callback_data='vote_'+str(player))])
    point2 = games[game_id].__votes__[player_id]
    if point2 == None:
        buttons.append([InlineKeyboardButton(text='  ', callback_data='ignore')])
    else:
        his_name = games[game_id].__players__[point2][0]
        buttons.append([InlineKeyboardButton(text=his_name, callback_data='ignore')])

    if player_id in games[game_id].__ppz__:
        text = 'Вы ППЦ! Кодовое слово ПЕРЕЦ! Для победы укажите второго ППЦ!'
    else:
        text = 'Вы гражданин! Найдите одного из ППЦ!'
    bot.editMessageText((games[game_id].__players__[player_id][1], games[game_id].__players__[player_id][2]), text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

# =====================================================
#                 ИНИЦИАЛИЗАЦИЯ БОТА
# =====================================================

global games
global hosts
global in_lobby
global in_game
global finished_games
games = {}
finished_games = []
in_lobby = {}
in_game = {}
hosts = {}

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

while 1:
    for g in games:
        games[g].process()
    for g in finished_games:
        games.pop(g)
    finished_games = []
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
    print('========')
    print('games')
    pprint(games)
    print('in_lobby')
    pprint(in_lobby)
    print('in_game')
    pprint(in_game)
    print('hosts')
    pprint(hosts)
    #print(k)
    #if k % 13 == 0:
    #    for add in in_lobby:
    #        chat_id = in_lobby[add][1]
    #        message_id = in_lobby[add][2]
    #        bot.deleteMessage((chat_id, message_id))
    time.sleep(1)