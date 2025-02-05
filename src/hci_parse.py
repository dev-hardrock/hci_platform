import json
from src.utils import *


def hci_parse_with_json(json_file, json_data):
    message =''
    with open(json_file, 'r', encoding='utf-8') as fp:
        hci_schema = json.load(fp)
    for indentifier in hci_schema['hci_commands']:
        for command in indentifier['command']:
            if command['name'] in json_data:
                message += convert_hex_string(command['opcode'])
                if 'parameters' in command:
                    for argument in command['parameters']:
                        if argument['name'] in json_data[command['name']]:
                            type = argument['type']
                            data = json_data[command['name']][argument['name']]
                            message += convert_hex_string_with_type(data, type)
                else:
                    print(message)
            else:
                continue
            return message
