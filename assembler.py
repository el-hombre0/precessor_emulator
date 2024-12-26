instruction_set = { # Набор инструкций
    "HLT": 0x00, # Переводит процессор в состояние останова
    "MOV": 0x01, # MOV ПРИЕМНИК, ИСТОЧНИК Перемещение значения из ИСТОЧНИКА в ПРИЁМНИК
    "ADD": 0x02, # Целочисленное сложение двух операндов
    "ADC": 0x03, # Производит суммирование операндов и значения флага CF для больших чисел, не помещающихся в указанные размеры операндов
    "DEC": 0x04, # Декремент, уменьшение числа на единицу
    "JNZ": 0x05, # Выполняет переход к метке, если флаг нуля не установлен
}

register_set = { # Набор регистров
    "EAX": 0x00, # Регистр общего назначения, аккумулятор
    "EBX": 0x01, # Указатель на данные, base
    "ECX": 0x02, # Хранит счетчик цикла, counter
    "EDX": 0x03, # Для арифметических операций и операций ввода-вывода
}


def main():
    raw_code = open('example.txt', 'r') # Получение кода в ассемблерных командах
    output = open('output.txt', 'w') # Вывод в двоичную сс
    is_data = False # Флаг для отслеживания того, что считывается секция данных
    instruction_count=0 # Счетчик инструкций для спуска вниз по файлу
    section_dict={} # Словарь секций
    for line in raw_code: # Перебор ассемблерного кода по строкам
        line = line.strip() # Обрезаем перенос строки 
        if "section" in line: # Считали секцию
                if ".data" in line: # Если считываем данные
                    is_data = True # Флаг данные
                    continue
                else:
                    is_data = False #Флаг данные
                    section_dict.update({line.split(".")[1]: instruction_count} ) # Записали тип секции в словарь
                    continue
                                    
        if is_data == True: # Если получили массив, то режем его на числа
            number = line.split()
            for i in range (int(number[0])+1): # Первое число в строке - длина массива
                output.write(bin(i)[2:].zfill(8) + ' ' + bin(int(number[i]))[2:].zfill(8) + '\n') # Перевод в двоичную запись, удаление 0b и дополнение до 8 бит, позиция и само значение
        elif is_data == False: # Если это инструкция, а не данные или пустая строка
            if line != "":
                instruction_count+=1 # Подсчитываем инструкции
        is_data = False # Закончили обработку строки
    print(section_dict)
    instruction_count=0
    output.write('\n')
    raw_code.close()
    raw_code = open('example.txt', 'r') # Перемещение в начало файла
    counter=0 # Порядковый номер инструкции
    for line in raw_code:
        opr_1=bin(0)[2:].zfill(8) # Сбрасываем значения операндов и адресаций для установки новых (default EAX, 01)
        adr_1=bin(1)[2:].zfill(2)
        opr_2=bin(0)[2:].zfill(8)
        adr_2=bin(1)[2:].zfill(2)
        line = line.strip() # Обрезаем перенос строки и пробелы
        if line == "": # Если пустая строка
            continue
        if "section" in line: # Если рассматриваем секцию
            is_data = False # То это не массив данных
            if "section .data" in line: # Если получаем тип секции
                is_data = True
            continue
        if is_data == True: # Если над текущей строкой было обозначение секции с массивом, то будет флаг true, пропускаем считывание
            continue # Если это секция не массива
        com_line=line.split() # Разбиваем строку на команды
        com_len=len(com_line) # Длина строки с командой
        print(com_line) # Печатаем команду
        num=bin(counter)[2:].zfill(8) # Номер строки с командами в 2 сс
        command=bin(instruction_set[com_line[0]])[2:].zfill(4) # Описываем команду в 2 сс на 4 бита
        if com_len > 1: # 2 и более элементов
            if com_line[1].strip("[]") in register_set: # есть ли 2й элемент в наборе регистров (выбор работы с числом или регистром)
                opr_1=bin(register_set[com_line[1].strip("[]")])[2:].zfill(8) # Операнд 1 в 2 сс
                if "[" in com_line[1]: # Адресация для регистра
                    adr_1=bin(3)[2:].zfill(2) # Тип адресации загрузка из памяти по значению из регистра
                else:
                    adr_1=bin(2)[2:].zfill(2) # Тип адресации загрузка значения из регистра
            else: # Выбор работы с числом
                opr_1=bin(int(com_line[1].strip("[]")))[2:].zfill(8) # Операнд 1 - число в 2 сс
                if "[" in com_line[1]: # Адресация для числа
                    adr_1=bin(0)[2:].zfill(2) # Тип адресации загрузка из памяти по данному индексу
                else:
                    adr_1=bin(1)[2:].zfill(2) # Тип адресации загрузка данного числа
        if com_len > 2: # 3 и более элементов
            if com_line[2].strip("[]") in register_set:
                opr_2=bin(register_set[com_line[2].strip("[]")])[2:].zfill(8)
                if "[" in com_line[2]: # Адресация для регистра
                    adr_2=bin(3)[2:].zfill(2)
                else:
                    adr_2=bin(2)[2:].zfill(2)
            elif com_line[2] in section_dict: # Обработка секции
                adr_2=bin(1)[2:].zfill(2)
                opr_2=bin(section_dict[com_line[2]])[2:].zfill(8) # Значение из словаря секций
            else: # Обработка числа
                opr_2=bin(int(com_line[2].strip("[]")))[2:].zfill(8)
                if "[" in com_line[2]: # Адресация для числа
                    adr_2=bin(0)[2:].zfill(2)
                else:
                    adr_2=bin(1)[2:].zfill(2)
        counter=counter + 1 
        print(num, command, adr_1, opr_1, adr_2, opr_2)
        output.write(num + ' ' + command + ' ' + adr_1 + ' ' + opr_1 + ' ' + adr_2 + ' ' + opr_2 +  '\n')

import sys
if __name__ == "__main__":
  main()

'''
{'start': 0, 'loop': 1}
['MOV', 'ECX', '[0]']
00000000 0001 10 00000010 00 00000000
['MOV', 'EDX', '[ECX]']
00000001 0001 10 00000011 11 00000010
['ADD', 'EBX', 'EDX']
00000010 0010 10 00000001 10 00000011
['MOV', 'EDX', '0']
00000011 0001 10 00000011 01 00000000
['ADC', 'EAX', 'EDX']
00000100 0011 10 00000000 10 00000011
['DEC', 'ECX']
00000101 0100 10 00000010 01 00000000
['JNZ', 'ECX', 'loop']
00000110 0101 10 00000010 01 00000001
['HLT']
00000111 0000 01 00000000 01 00000000
'''

# Порядковый номер | Команда | Адресация 1 операнда | 1 операнд | Адресация 2 операнда | 2 операнд  
      
# 4 бита              4 бита      2 бита              2 бита            2 бита             2 бита
    
            
                 
