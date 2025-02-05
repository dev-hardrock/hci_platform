import os


def find_files(directory='', extersion=''):
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(directory)) for f in fn if
            f.endswith(extersion)]


def convert_hex_string(hex_string):
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    if len(hex_string) % 2 != 0:
        hex_string = '0' + hex_string

    # 使用字符串的切片功能分割字符串，每两个字符一组
    split_str = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]

    # 反转各部分的顺序
    reversed_split_str = split_str[::-1]

    # 使用join方法用空格连接这些部分
    result = ' '.join(reversed_split_str) + ' '
    return result


def get_type(type):
    if type == 'uint8':
        return 1
    if type == 'uint16':
        return 2
    if type == 'uint24':
        return 3
    if type == 'uint32':
        return 4


def convert_hex_string_with_type(hex_string, type):
    if isinstance(hex_string, int):
        hex_string = str(hex_string)
    if hex_string.startswith("0x"):
        hex_string = hex_string[2:]
    data_len = get_type(type)
    while len(hex_string) != data_len * 2:
        hex_string = '0' + hex_string

    # 使用字符串的切片功能分割字符串，每两个字符一组
    split_str = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]

    # 反转各部分的顺序
    reversed_split_str = split_str[::-1]

    # 使用join方法用空格连接这些部分
    result = ' '.join(reversed_split_str) + ' '
    return result
