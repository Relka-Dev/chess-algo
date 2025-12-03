
CHESS_BOT_LIST = {}

def register_chess_bot(name, function):
    global CHESS_BOT_LIST
    if name in CHESS_BOT_LIST:
        register_chess_bot(name+"_", function)
    else:
        CHESS_BOT_LIST[name] = function