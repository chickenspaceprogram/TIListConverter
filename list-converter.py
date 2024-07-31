import csv
import decimal
import math

# general usage functions

def unpack_word(word: int) -> list[int]:
    if len(hex(word)) > 6:
        raise Exception(f"The data inputted {(word)} was too large to be stored as a word.")
    
    nibble_list: list[str] = [i for i in hex(word)[2:]]
    nibble_list += ['0'] * (4 - len(nibble_list))
    
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
    def __init__(self, data_length: int, comment: str):
        self.__get_sig_1()
        self.__get_sig_2()
        self.comment: list[int] = convert_ASCII(comment)
        self.data_length: list = unpack_word(data_length)
        self.header: list = self.sig_1 + self.sig_2 + self.comment + self.data_length

    def __get_sig_1(self):
        self.sig_1: list = [ord(i) for i in "**TI83F*"]
    
    def __get_sig_2(self):
        self.sig_2: list = [0x1a, 0x0a, 0x00]
    
    def __get_comment(self):
        self.comment: list = [ord(i) for i in "Made by chickenspaceprogram's ConverTI app"]

class Data():
    def __init__(self, name_on_calc: str, filename: str, is_complex: bool, is_archived: bool):
        self.raw_data: list = self.__import_data(filename)
        self.get_tupled_data(is_complex)
        self.variable_data_length: list[int] = unpack_word(len(self.tupled_data) * 9)
        self.start = [0x0d, 0x00]
        self.get_type_ID()


    def __import_data(self, filename: str) -> list:
        imported_data: list = []
        with open(filename, 'r') as imported_file:
            csv_reader = csv.reader(imported_file)
            for line in csv_reader:
                imported_data.append(line)
        
        if len(imported_data) != 1:
            raise Exception("Multiple rows provided in CSV, can only process one row.")
        
        return imported_data[0]
    
    def format_num(self, number: decimal.Decimal, is_complex: bool) -> tuple[int, int]:
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
    
    def get_tupled_data(self, is_complex: bool):
        '''
        Uses format_num to convert data into a list of tuples of form (flag, exponent, coefficient).
        '''
        self.tupled_data: list[tuple[int, int, int]] = [self.format_num(decimal.Decimal(i), is_complex) for i in self.raw_data]
    
    def get_type_ID(self, is_complex):
        if is_complex:
            self.type_ID: list[int] = [0x0d]
        else:
            self.type_ID: list[int] = [0x01]
    
    def get_var_name(self, var_name: str):


name_on_calc: str = "ALIST"
filename: str = "example.csv"
is_complex: bool = True
# input the list as just a list of real numbers, if is_complex is True they will be paired automatically
# yes this is jank, no i will not fix it



imported_data: list[list] = []


if len(imported_data) > 1:
    raise Exception("Multiple rows provided in CSV, can only process one row.")

formatted_data: list[tuple[int, int]] = [format_num(decimal.Decimal(i), is_complex) for i in imported_data[0]]
num_elements: int = len(formatted_data)

