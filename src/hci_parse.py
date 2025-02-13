import json
from src.utils import *

H4_CMD = '01'
H4_ACL = '02'
H4_SCO = '03'
H4_EVT = '04'
H4_ISO = '05'

HCI_CMD = 1
HCI_ACL = 2
HCI_SCO = 3
HCI_EVT = 4
HCI_ISO = 5


def hci_parse_with_json(json_file, json_data):
    message = ''
    hci_type=''
    # 打开指令解析文件，转成json格式字符串
    with open(json_file, 'r', encoding='utf-8') as fp:
        hci_schema = json.load(fp)
    for hci_command in hci_schema['hci_commands']:
        for command in hci_command['command']:
            # 输入的数据跟指令文件做匹配检查
            if command['name'] in json_data:
                hci_type = H4_CMD
                message += convert_hex_string(command['opcode'])
                parameters_total_len = command['parameter_total_len']
                if parameters_total_len != 0 :
                    parameter_data=""
                    for argument in command['parameters']:
                        if argument['name'] in json_data[command['name']]:
                            unit = argument['unit']
                            unit_len = argument['size']
                            data = json_data[command['name']][argument['name']]
                            parameter_data += convert_hex_string_with_type(data, unit, unit_len)
                    parameters_total_len = len(parameter_data) // 2
                    message += ''.join(f"{parameters_total_len:02x}")
                    message += parameter_data
                else:
                    message +=''.join(f"{parameters_total_len:02x}")
            else:
                continue

    return  hci_type + message

def get_packet_type_str(hci_type, issue):
    if issue:
        hex_str = "=> "
    else:
        hex_str = "<= "
    if hci_type == HCI_CMD:
        return "CMD " + hex_str
    elif hci_type == HCI_ACL:
        return "ACL " + hex_str
    elif hci_type == HCI_SCO:
        return "ACL " + hex_str
    elif hci_type == HCI_EVT:
        return "EVT " + hex_str
    elif hci_type == HCI_ISO:
        return "ISO " + hex_str
    else:
        return "Unknown " + hex_str

