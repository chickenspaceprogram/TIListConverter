import csv
import decimal
import math

# general usage functions

def unpack_word(word: int) -> list[int]:
    if len(hex(word)) > 6:
        raise Exception(f"The data inputted {(word)} was too large to be stored as a word.")
    
    nibble_list: list[str] = [i for i in hex(word)[2:]]
    nibble_list = ['0'] * (4 - len(nibble_list)) + nibble_list

    return_list: list = []
    for i in range(0, 4, 2):
        return_list.append(nibble_list[i] + nibble_list[i + 1])
    
    for index, byte in enumerate(return_list):
        return_list[index] = int(byte, 16)
    
    return_list.reverse()
    return return_list

def convert_ASCII(text: str) -> list[int]:
    return [ord(i) for i in text]

class Header():
    def __init__(self, data_length: int, comment: str, data_section: list[int]):
        self.__get_sig_1()
        self.__get_sig_2()
        self.comment: list[int] = convert_ASCII(comment)
        self.data_length: list = unpack_word(data_length)
        self.header: list = self.sig_1 + self.sig_2 + self.comment + self.data_length
        self.__get_checksum(data_section)

    def __get_sig_1(self):
        self.sig_1: list = [ord(i) for i in "**TI83F*"]
    
    def __get_sig_2(self):
        self.sig_2: list = [0x1a, 0x0a, 0x00]
    
    def __get_checksum(self, data_section):
        self.checksum: list = unpack_word(sum(data_section))

class Data():
    def __init__(self, name_on_calc: str, filename: str, is_complex: bool, is_archived: bool):
        self.raw_data: list = self.__import_data(filename)
        self.__get_tupled_data(is_complex)
        self.__combine_tupled_data()
        self.variable_data_length: list[int] = unpack_word(len(self.tupled_data) * 9 + 2)
        self.list_length: list[int] = unpack_word(len(self.tupled_data))
        self.start = [0x0d, 0x00]
        self.__get_type_ID(is_complex)
        self.__get_var_name(']' + name_on_calc)
        self.version = [0x00]
        self.__set_flag(is_archived)
        self.formatted_data: list = self.start + self.variable_data_length + self.type_ID + self.var_name + self.version + self.flag + self.variable_data_length + self.list_length + self.var_data

    def __import_data(self, filename: str) -> list:
        imported_data: list = []
        with open(filename, 'r') as imported_file:
            csv_reader = csv.reader(imported_file)
            for line in csv_reader:
                imported_data.append(line)
        
        if len(imported_data) != 1:
            raise Exception("Multiple rows provided in CSV, can only process one row.")
        
        return imported_data[0]
    
    def __format_num(self, number: decimal.Decimal, is_complex: bool) -> tuple[int, int]:
        '''
        Takes a decimal as input and returns a tuple containing the flag byte, the exponent, and the coefficient, all as integers.
        '''
        exponent: int = math.floor(decimal.Decimal(abs(number).log10()))
        coefficient: decimal.Decimal = number / decimal.Decimal(10 ** exponent)
        coefficient *= decimal.Decimal(10 ** 13)
        coefficient = int(round(coefficient))
        if is_complex:
            flagstr: str = '0110000'
        else:
            flagstr: str = '0000000'
        if coefficient < 0:
            flagstr += '1'
        else:
            flagstr += '0'
        flag: int = int(flagstr, 2)
        return (flag, exponent + 0x80, abs(coefficient))
    
    def __get_tupled_data(self, is_complex: bool):
        '''
        Uses format_num to convert data into a list of tuples of form (flag, exponent, coefficient).
        '''
        self.tupled_data: list[tuple[int, int, int]] = [self.__format_num(decimal.Decimal(i), is_complex) for i in self.raw_data]
    
    def __combine_tupled_data(self):
        self.var_data: list = []
        for flag, exponent, coefficient in self.tupled_data:
            self.var_data.append(flag)
            self.var_data.append(exponent)
            for byte_index in range(0, 14, 2):
                self.var_data.append(int(str(coefficient)[byte_index:byte_index + 2], 16))
    
    def __get_type_ID(self, is_complex):
        if is_complex:
            self.type_ID: list[int] = [0x0d]
        else:
            self.type_ID: list[int] = [0x01]
    
    def __get_var_name(self, var_name: str):
        var_name = var_name.upper()
        if len(var_name) > 6:
            raise SyntaxError(f"List name '{var_name[1:]}' was too long, maximum is 5 characters.")
        if not(var_name[1:].isalnum()):
            raise SyntaxError(f"List name '{var_name[1:]}' contained non-alphanumeric characters.")
        if not(var_name[1:].isalpha()):
            raise SyntaxError(f"The first character in list name '{var_name[1:]}' is not alphabetic.")
        self.var_name = convert_ASCII(var_name)
        self.var_name += [0] * (8 - len(self.var_name))
    
    def __set_flag(self, is_archived):
        if is_archived:
            self.flag = [0x80]
        else:
            self.flag = [0x00]


name_on_calc: str = "ALIST"
filename: str = "example.csv"
is_complex: bool = False
is_archived: bool = False
# input the list as just a list of real numbers, if is_complex is True they will be paired automatically
# yes this is jank, no i will not fix it

data = Data(name_on_calc, filename, is_complex, is_archived)
header = Header(len(data.formatted_data), "Made by chickenspaceprogram's ConverTI app", data.formatted_data)

file: bytes = bytes(header.header + data.formatted_data + header.checksum)

with open(f"{name_on_calc.upper()}.8xl", 'wb') as binaryfile:
    binaryfile.write(file)