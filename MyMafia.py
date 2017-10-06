import re
import sys
import random
import time
import telepot
from pprint import pprint


global games_list
games_list = []

class game(object):
    def __init__(self):
        self.__started__ = 0
        self.__current_round__ = 0
        self.__game_id__ = 0
        self.__players__ = {}
        self.__player_num__ = 0
        self.__host__ = ''
        self.__roles__ = {
            'maf_num':0,
            'cit_num':0,
            'doc_num':0,
            'com_num':0,
            'bum_num':0
        }
        self.__round_time__ = 5
    def add_player(self, adr):
        self.__players__[self.__player_num__ + 1] = {
                                        'adr': adr,
                                        'name': 'Player_' + str(self.__player_num__+1),
                                        'alive': 1,
                                        'pointer': 0,
                                        'acted': 0,
                                        'last_vote': 0,
                                        'role': None
                                      }
        self.__player_num__ += 1

    # выбор адресов соответствующих подгрупп
    def everybody(self):
        return [self.__players__[i]['adr'] for i in self.__players__]

    def alive(self):
        arr = []
        for i in self.__players__:
            if self.__players__[i]['alive']:
                arr.append(self.__players__[i]['adr'])
        return arr

    def mafs(self):
        arr = []
        for i in self.__players__:
            if (self.__players__[i]['role'] == 'maf'):
                arr.append(self.__players__[i]['adr'])
        return arr

    def cits(self):
        arr = []
        for i in self.__players__:
            if (self.__players__[i]['role'] == 'cit'):
                arr.append(self.__players__[i]['adr'])
        return arr

    def coms(self):
        arr = []
        for i in self.__players__:
            if (self.__players__[i]['role'] == 'com'):
                arr.append(self.__players__[i]['adr'])
        return arr

    def docs(self):
        arr = []
        for i in self.__players__:
            if (self.__players__[i]['role'] == 'doc'):
                arr.append(self.__players__[i]['adr'])
        return arr

    def bums(self):
        arr = []
        for i in self.__players__:
            if (self.__players__[i]['role'] == 'bum'):
                arr.append(self.__players__[i]['adr'])
        return arr

    def say(self, players, message):
        for id in players:
            bot.sendMessage(id, message)

    def report_status(self, players):
        message = ''
        for player_id in self.__players__:
            if (self.__players__[player_id]['alive']):
                message += str(player_id) + ' - ' + self.__players__[player_id]['name'] + ' \n'
        for id in players:
            bot.sendMessage(id, message)

    def countdown(self, sec, verbose, players):
        for i in range(sec):
            for addr in players:
                if verbose:
                    bot.sendMessage(addr, str(sec - i))
            time.sleep(1)

    def get_id(self, adr):
        for id in self.__players__:
            if (adr == self.__players__[id]['adr']):
                return id
        return 0

    def reload_abilities(self):
        for i in self.__players__:
            self.__players__[i]['acted'] = 0

    def reset_pointers(self):
        for i in self.__players__:
            self.__players__[i]['pointer'] = 0

    # функция обновления игры
    def refresh(self, ):
        # Голосование добра
        # =======================================================
        if (g.__roles__['cit_num'] != 0): # если мафия существует вообще
            vote_cit = {id:0 for id in g.__players__ if g.__players__[id]['alive']} # пустой словарь распр. голосов
            for id in g.__players__: # по всем игрокам
                # кторые живы и горожане и указывают не на пустоту и у которых перезаряжена абилка
                if ((g.__players__[id]['alive']) &
                    (g.__players__[id]['role'] == 'cit') &
                    (g.__players__[id]['pointer'] != 0) &
                    (g.__players__[id]['acted'] == 0)):
                    pntr = g.__players__[id]['pointer']
                    if (g.__players__[pntr]['alive']): # если указывает на живого
                        vote_cit[pntr] += 1
            # Принятие решения по голосованию
            for id in vote_cit:
                # успешное голосование
                if vote_cit[id] > (g.__roles__['cit_num'])/2: # простое большинство добра (попытка казни)

                    # спас ли доктор
                    vote_doc = {doc_id:[] for doc_id in g.__players__ if g.__players__[id]['alive']} # пустой словарь распр. голосов
                    for doc_id in g.__players__:  # по всем игрокам
                        # кторые живы и доктора и указывают не на пустоту и у которых перезаряжена абилка
                        if ((g.__players__[doc_id]['alive']) &
                                (g.__players__[doc_id]['role'] == 'doc') &
                                (g.__players__[doc_id]['pointer'] != 0) &
                                (g.__players__[doc_id]['acted'] == 0)):
                            pntr_d = g.__players__[doc_id]['pointer']
                            vote_doc[pntr_d].append(doc_id)
                    if vote_doc[id] != []:
                        # доктор спас
                        doc = random.choice(vote_doc[id])
                        g.say(g.alive(), 'CITIZENS FAILED \n' + g.__players__[id]['name'] + ' WAS SAVED BY DOCTOR')
                        # доктор отлечился сегодня
                        g.__players__[doc]['acted'] = 1
                        # горожане отстрелялись сегодня
                        for id in g.__players__: # по всем игрокам
                            # кторые живы и горожане
                            if ((g.__players__[id]['alive']) &
                                (g.__players__[id]['role'] == 'cit')):
                                g.__players__[id]['acted'] = 1
                    else:
                        # не спас
                        g.__players__[id]['alive'] = 0 # умерщвление
                        g.say([g.__players__[id]['adr']], 'YOU WERE KILLED AT DAY VOTING')
                        g.say(g.alive(), g.__players__[id]['name'] + ' WAS KILLED AT DAY VOTING')
                        # горожане отстрелялись сегодня
                        for id in g.__players__: # по всем игрокам
                            # кторые живы и горожане
                            if ((g.__players__[id]['alive']) &
                                (g.__players__[id]['role'] == 'cit')):
                                g.__players__[id]['acted'] = 1
        #  =======================================================
        # Убийство МАФИИ (лечение доктора)
        # =======================================================
        if (g.__roles__['maf_num'] != 0): # если мафия существует вообще
            vote_maf = {id:0 for id in g.__players__ if g.__players__[id]['alive']} # пустой словарь распр. голосов
            for id in g.__players__: # по всем игрокам
                # кторые живы и мафы и указывают не на пустоту и у которых перезаряжена абилка
                if ((g.__players__[id]['alive']) &
                    (g.__players__[id]['role'] == 'maf') &
                    (g.__players__[id]['pointer'] != 0) &
                    (g.__players__[id]['acted'] == 0)):
                    pntr_maf = g.__players__[id]['pointer']
                    if (g.__players__[pntr_maf]['alive']): # если указывает на живого
                        vote_maf[pntr_maf] += 1
            # Принятие решения по голосованию
            for id in vote_maf:
                # успешное голосование
                if vote_maf[id] == (g.__roles__['maf_num']): # единогласное голосование зла (попытка убийства)

                    # спас ли доктор
                    vote_doc = {doc_id:[] for doc_id in g.__players__ if g.__players__[id]['alive']} # пустой словарь распр. голосов
                    for doc_id in g.__players__:  # по всем игрокам
                        # кторые живы и доктора и указывают не на пустоту и у которых перезаряжена абилка
                        if ((g.__players__[doc_id]['alive']) &
                                (g.__players__[doc_id]['role'] == 'doc') &
                                (g.__players__[doc_id]['pointer'] != 0) &
                                (g.__players__[doc_id]['acted'] == 0)):
                            pntr_d = g.__players__[doc_id]['pointer']
                            vote_doc[pntr_d].append(doc_id)
                    if vote_doc[id] != []:
                        # доктор спас
                        doc = random.choice(vote_doc[id])
                        g.say(g.alive(), 'MAFS FAILED \n' + g.__players__[id]['name'] + ' WAS SAVED BY DOCTOR')
                        # доктор отлечился сегодня
                        g.__players__[doc]['acted'] = 1
                        # мафы отстрелялись сегодня
                        for id in g.__players__: # по всем игрокам
                            # кторые живы и мафы
                            if ((g.__players__[id]['alive']) &
                                (g.__players__[id]['role'] == 'maf')):
                                g.__players__[id]['acted'] = 1
                    else:
                        # не спас
                        g.__players__[id]['alive'] = 0 # умерщвление
                        g.say([g.__players__[id]['adr']], 'YOU WERE KILLED BY MAFIOZI')
                        g.say(g.alive(), g.__players__[id]['name'] + ' WAS KILLED BY MAFIOZI')
                        # мафы отстрелялись сегодня
                        for id in g.__players__: # по всем игрокам
                            # кторые живы и мафы
                            if ((g.__players__[id]['alive']) &
                                (g.__players__[id]['role'] == 'maf')):
                                g.__players__[id]['acted'] = 1
        #  =======================================================
        # Проверка коммисара
        if (g.__roles__['com_num'] != 0): # если коммисар существует вообще
            for id in g.__players__: # по всем игрокам
                # кторые живы и коммисары и указывают не на пустоту и у которых перезаряжена абилка
                if ((g.__players__[id]['alive']) &
                    (g.__players__[id]['role'] == 'com') &
                    (g.__players__[id]['pointer'] != 0) &
                    (g.__players__[id]['acted'] == 0)):
                    pntr_com = g.__players__[id]['pointer']
                    if (g.__players__[pntr_com]['alive']): # если указывает на живого
                        # коммисар получает информацию
                        if g.__players__[pntr_com]['role'] == 'maf':
                            g.say([g.__players__[id]['adr']], g.__players__[pntr_com]['name'] + ' IS MAF')
                        else:
                            g.say([g.__players__[id]['adr']], g.__players__[pntr_com]['name'] + ' IS NOT MAF')
                        # коммисар отстрелялся
                        g.__players__[id]['acted'] = 1
        #  =======================================================
        # Бомж бухает
        if (g.__roles__['bum_num'] != 0): # если бомж существует вообще
            for id in g.__players__: # по всем игрокам
                # кторые живы и бомжи и указывают не на пустоту и у которых перезаряжена абилка
                if ((g.__players__[id]['alive']) &
                    (g.__players__[id]['role'] == 'bum') &
                    (g.__players__[id]['pointer'] != 0) &
                    (g.__players__[id]['acted'] == 0)):
                    pntr_bum = g.__players__[id]['pointer']
                    if (g.__players__[pntr_bum]['alive']): # если указывает на живого
                        if (g.__players__[id]['last_vote'] != pntr_bum): # если не указывает второй раз подряд
                            # бомж лишает абилки
                            g.say(g.alive(), g.__players__[pntr_bum]['name'] + ' WAS DRINKING WITH BUM')
                            g.__players__[id]['last_vote'] = pntr_bum
                            g.__players__[pntr_bum]['acted'] = 1
                            # бомж отбомжился
                            g.__players__[id]['acted'] = 1
        #  =======================================================
        # Корректировка списка ролей
        g.__roles__['maf_num'] = 0
        g.__roles__['cit_num'] = 0
        g.__roles__['doc_num'] = 0
        g.__roles__['com_num'] = 0
        g.__roles__['bum_num'] = 0
        for id in g.__players__: # по всем игрокам
            # кторые живы
            if ((g.__players__[id]['alive'])):
                if (g.__players__[id]['role'] == 'maf'):
                    g.__roles__['maf_num'] += 1
                if (g.__players__[id]['role'] == 'cit'):
                    g.__roles__['cit_num'] += 1
                if (g.__players__[id]['role'] == 'doc'):
                    g.__roles__['doc_num'] += 1
                if (g.__players__[id]['role'] == 'com'):
                    g.__roles__['com_num'] += 1
                if (g.__players__[id]['role'] == 'bum'):
                    g.__roles__['bum_num'] += 1
        #  =======================================================
        # Проверка игры на завершение
        if g.__roles__['maf_num'] == 0:
            g.say(g.everybody(), '======================\n==== good triumphed ====\n======================')
            for adr in g.everybody():
                bot.sendPhoto(adr, 'https://pp.vk.me/c836322/v836322101/1f9ef/SC378yiNt_s.jpg')
            exit()
        if (g.__roles__['cit_num'] == 0) & (g.__roles__['doc_num'] == 0) & (g.__roles__['com_num'] == 0) & (g.__roles__['bum_num'] == 0):
            g.say(g.everybody(), '======================\n==== mafia triumphed ====\n======================')
            for adr in g.everybody():
                bot.sendPhoto(adr, 'https://pp.vk.me/c836322/v836322101/1f9ef/SC378yiNt_s.jpg')
            exit()

def msg_handler(adr, msg):
    if (msg == '/start_game'):  # Хостится игра
        host = adr
        game_id = random.randrange(0,100)
        print('game ' + str(game_id) + ' starting...')
        global g
        g = game()
        g.__game_id__ = game_id
        g.__host__ = host
        g.add_player(host)
        games_list.append((game_id))
        bot.sendMessage(adr, 'game ' + str(game_id) + ' starting')

    if (msg == '/go'):  # Комплектуется и запускается игра
        if ('g' in globals()):
            if adr == g.__host__:
                # Укомплектовка состава
                if (len(g.__players__) >= g.__roles__['maf_num'] + g.__roles__['doc_num'] + g.__roles__['com_num']):
                    everybody = [i+1 for i in range(len(g.__players__))]
                    mafs = random.sample(everybody, g.__roles__['maf_num'])
                    rest = [i for i in everybody if i not in mafs]
                    docs = random.sample(rest, g.__roles__['doc_num'])
                    rest = [i for i in rest if i not in docs]
                    coms = random.sample(rest, g.__roles__['com_num'])
                    rest = [i for i in rest if i not in coms]
                    bums = random.sample(rest, g.__roles__['bum_num'])
                    cits = [i for i in rest if i not in bums]
                    g.__roles__['cit_num'] = len(cits)
                    # присвоение ролей
                    for i in mafs:
                        g.__players__[i]['role'] = 'maf'
                    for i in docs:
                        g.__players__[i]['role'] = 'doc'
                    for i in coms:
                        g.__players__[i]['role'] = 'com'
                    for i in bums:
                        g.__players__[i]['role'] = 'bum'
                    for i in cits:
                        g.__players__[i]['role'] = 'cit'
                    g.say(g.everybody(), '======================\n=== REAL TIME MAFIA ===\n======================')
                    for adr in g.everybody():
                        bot.sendPhoto(adr, 'https://pp.vk.me/c626816/v626816101/32bfd/rAu5rfFEGJg.jpg')
                    # Объявление ролей
                    g.say(g.mafs(), '======================\n==== YOU ARE MAFIA =====\n======================')
                    g.say(g.cits(), '======================\n=== YOU ARE CITIZEN ====\n======================')
                    g.say(g.coms(), '======================\n== YOU ARE COMMISAIRE ==\n======================')
                    g.say(g.docs(), '======================\n==== YOU ARE DOCTOR ====\n======================')
                    g.say(g.bums(), '======================\n====== YOU ARE BUM =====\n======================')
                    # Знакомство мафии
                    maf_list_msg = ''
                    for player_id in g.__players__:
                        if g.__players__[player_id]['role'] == 'maf':
                            maf_list_msg += str(player_id) + ' - ' + g.__players__[player_id]['name'] + ' \n'
                    g.say(g.mafs(), 'ALL MAFS: \n' + maf_list_msg)
                    # Начало игры
                    g.__started__ = 1
                    g.__current_round__ = 1
                    g.reload_abilities()
                    g.reset_pointers()
                    g.say(g.everybody(), 'ROUND 1')
                    g.report_status(g.everybody())
                    g.refresh()

    if (msg == '/game_list'):  # Проверка списка игр
        bot.sendMessage(adr, str(games_list))

    if (msg == '/players_adr'):  # Проверка айдишников игроков
        if ('g' in globals()):
            bot.sendMessage(adr, g.everybody())

    if (msg == '/player_names'):  # Проверка списка игроков
        if ('g' in globals()):
            g.report_status([adr])

    if (msg == '/countdown'):  # Всем 3-х секундное ожидание
        if ('g' in globals()):
            g.countdown(3, 1, g.everybody())

    if (msg == '/h'):  # Всем 3-х секундное ожидание
        if ('g' in globals()):
            if adr == g.__host__:
                bot.sendMessage(adr, '/countdown\n/player_names\n/players_adr\n/change_name\n/mafs\n/docs\n/coms\n/bums\n/go')
            else:
                bot.sendMessage(adr, '/player_names\n/change_name\n/connect')
        else:
            bot.sendMessage(adr, '/start_game')

    m = re.search('/mafs ', msg) # Число мафов
    if (m != None):
        maf_num = int(msg[m.span()[1]: ])
        g.__roles__['maf_num'] = maf_num

    m = re.search('/docs ', msg) # Число докторов
    if (m != None):
        doc_num = int(msg[m.span()[1]: ])
        g.__roles__['doc_num'] = doc_num

    m = re.search('/coms ', msg) # Число коммисаров
    if (m != None):
        com_num = int(msg[m.span()[1]: ])
        g.__roles__['com_num'] = com_num

    m = re.search('/bums ', msg) # Число коммисаров
    if (m != None):
        bum_num = int(msg[m.span()[1]: ])
        g.__roles__['bum_num'] = bum_num

    m = re.search('/change_name ', msg)  # Смена имени
    if (m != None):
        new_name = (msg[m.span()[1]:])
        if ('g' in globals()):
            g.__players__[g.get_id(adr)]['name'] = new_name

    m = re.search('/connect ', msg) # Коннект к игре
    if (m != None):
        connect_to = int(msg[m.span()[1]: ])
        if (connect_to in games_list):
            if (g.__players__ == {}):
                bot.sendMessage(adr, 'connected')
                g.add_player(adr) # добавляем игрока
            elif (adr not in list(g.everybody())):
                bot.sendMessage(adr, 'connected')
                g.add_player(adr) # добавляем игрока
            else:
                bot.sendMessage(adr, 'you are already connected')

    # смена указателя
    if (msg.isdigit()): # пришло число
        if ('g' in globals()): # игра существует
            if (int(msg) in [i for i in range(len(g.__players__) + 1)]): # на существующего игрока
                g.__players__[g.get_id(adr)]['pointer'] = int(msg) # меняем указатель
                if int(msg) == 0:
                    point_msg = 'nobody'
                else:
                    point_msg = msg + ' - ' + g.__players__[int(msg)]['name']
                bot.sendMessage(adr, 'You point at \n' + point_msg)
                g.refresh()




def time_handler(time_stamp):
    if ('g' in globals()):
        if g.__started__:
            time_stamp += 1
        if (time_stamp == int(g.__round_time__ * 30)): # половина времени прошло
            mins = int(time_stamp/60)
            secs = time_stamp - mins*60
            g.say(g.everybody(), str(mins) + ' Min ' + str(secs) + ' Sec left...')
        if (int(g.__round_time__ * 60) - time_stamp == 60): # осталась минута
            g.say(g.everybody(), 'One minute left...')
        if (time_stamp == g.__round_time__ * 60): # время раунда вышло
            g.reload_abilities()
            g.reset_pointers()
            time_stamp = 0
            g.countdown(3, 1, g.everybody())
            g.refresh()
            g.__current_round__ += 1
            g.say(g.everybody(),'ROUND ' + str(g.__current_round__))
            g.report_status(g.everybody())
    return time_stamp


token = '371150676:AAFNeZ7lPfeuftBxUaXuc_Drrj6jgzvW4rA'
bot = telepot.Bot(token)
# Очистка кэша
onstart_update = bot.getUpdates()
if (onstart_update != []):
    update_id = int(onstart_update[-1].get('update_id')) + 1
    bot.getUpdates(offset=update_id)

# Основной луп
#bot.message_loop(main)
#print('waiting for game ...')
offset = 0
time_stamp = 0

# Basic loop
while 1:
    time_stamp = time_handler(time_stamp)
    print(time_stamp)
    pkgs = bot.getUpdates(offset = offset)
    if pkgs != []: # сообщение/я пришло... обрабатываем
        msg_num = len(pkgs) # число пришедших пакетов
        for pkg in pkgs:    # обрабатываем последовательно
            adr = pkg['message']['from']['id']
            msg = pkg['message']['text']
            msg_handler(adr, msg)
        offset = int(pkgs[-1].get('update_id')) + 1

    # проверка на окончание кона
    # в случае если все ЖИВЫЕ сделали свои дела
    cont = 0
    if('g' in globals()):
        if g.__started__:
            for i in g.__players__:
                if (g.__players__[i]['alive']):
                    if (g.__players__[i]['acted'] == 0):
                        cont = 1
            if not cont:
                time_stamp = g.__round_time__*60-1



    time.sleep(1)
