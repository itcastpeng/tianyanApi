



# 替换中文符号
def replace_chinese_character(string):
    table = {ord(f): ord(t) for f, t in zip(
        '，。！？【】（）％＃＠＆１２３４５６７８９０“”；：',
        ',.!?[]()%#@&1234567890"";:')}

    new_string = string.translate(table)
    return new_string
