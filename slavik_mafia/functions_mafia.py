#! /usr/bin/env python
# -*- coding: utf-8 -*-


def can_be_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def save_vars(filename, *args):
    import pickle
    vars_to_dump = list()

    with open(filename, 'w') as dumpfile:
        if len(args) == 1:
            pickle.dump(args[0], dumpfile)

        elif len(args) > 1:
            for i in args:
                vars_to_dump.append(i)
            pickle.dump(vars_to_dump, dumpfile)


def load_vars(filename):
    import pickle
    with open(filename) as dumpfile:
        variables_list = pickle.load(dumpfile)
    return variables_list


def create_logger(name, log_level, log_type, *args):  # функция создания логгера
    import logging
    logger = logging.getLogger(name)
    if log_type == 'file':
        handler = logging.FileHandler(args[0])
    elif log_type == 'console':
        handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setLevel(log_level.upper())
    handler.setFormatter(formatter)

    level = logging.getLevelName(log_level.upper())
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def maf(chat_id, storage):
    if chat_id in storage[get_game_id(chat_id, storage)]['mafs']:
        return True
    else:
        return False


def com(chat_id, storage):
    if chat_id == storage[get_game_id(chat_id, storage)]['com']:
        return True
    else:
        return False


def doc(chat_id, storage):
    if chat_id == storage[get_game_id(chat_id, storage)]['doc']:
        return True
    else:
        return False


def cits(chat_id, storage):
    if chat_id in storage[get_game_id(chat_id, storage)]['cits']:
        return True
    else:
        return False


def get_game_id(chat_id, storage):
    game_id = None  # if chat_id not owns game and not in ids -> None
    if chat_id in storage:  # if chat_id owens game (pressed '/create')
        game_id = chat_id
    else:
        for key, value in storage.items():  # if chat_id don't have a game -> find in ids
            if chat_id in value['info']:
                game_id = key
    return game_id


def get_name(game_id, target_chat_id, storage):
    for key, value in storage[game_id]['info'].items():
        if target_chat_id == key:
            return value


def send_all(game_id, text, send_message, storage):
    for key, value in storage[game_id]['info'].items():
        send_message(key, text)


def mafs_acquaintance(game_id, send_message, storage):
    mafs = list()
    for chat_id, name in storage[game_id]['info']:
        if maf(chat_id, storage):
            mafs.append(name)

    for chat_id in storage[game_id]['mafs']:
        send_message(chat_id, 'mafs are %s' % str(mafs))
