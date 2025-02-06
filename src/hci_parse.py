import json
from src.utils import *


def hci_parse_with_json(json_file, json_data):
    message = ''
    # 打开指令解析文件，转成json格式字符串
    with open(json_file, 'r', encoding='utf-8') as fp:
        hci_schema = json.load(fp)
    for hci_command in hci_schema['hci_commands']:
        for command in hci_command['command']:
            # 输入的数据跟指令文件做匹配检查
            if command['name'] in json_data:
                message += convert_hex_string(command['opcode'])
                if 'parameters' in command:
                    for argument in command['parameters']:
                        if argument['name'] in json_data[command['name']]:
                            unit = argument['unit']
                            unit_len = argument['size']
                            data = json_data[command['name']][argument['name']]
                            message += convert_hex_string_with_type(data, unit, unit_len)
                else:
                    print(message)
            else:
                continue
            return message
