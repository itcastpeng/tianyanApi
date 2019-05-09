


from publicFunc.base64_encryption import b64encode, b64decode




# 向下小手四个
xiajiantou = b64decode('8J+Rhw==') + b64decode('8J+Rhw==') + b64decode('8J+Rhw==') + b64decode('8J+Rhw==')

# 难受表情 一个
nanshou = b64decode('8J+Ynw==')

# 彩带 🎉
caidai = b64decode('8J+OiQ==')
















if __name__ == '__main__':
    encode =  b64encode('🎉')
    print('encode----> ', encode)
    print(b64decode(encode))