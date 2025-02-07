text = open('output.txt', 'r').read()

instruction_set_r = { # Набор инструкций
  0x00: "HLT", # Переводит процессор в состояние останова
  0x01: "MOV", # MOV ПРИЕМНИК, ИСТОЧНИК Перемещение значения из ИСТОЧНИКА в ПРИЁМНИК
  0x02: "ADD", # Целочисленное сложение двух операндов
  0x03: "ADC", # Производит суммирование операндов и значения флага CF для больших чисел, не помещающихся в указанные размеры операндов
  0x04: "DEC", # Декремент, уменьшение числа на единицу
  0x05: "JNZ", # Выполняет переход к метке, если флаг нуля не установлен
}

reg_set = { # Регистры общего назначения
  0x00: "A",
  0x01: "B",
  0x02: "C",
  0x03: "D",
}

adr_type = {0: "[num]", 1: "num", 2: "reg", 3: "[reg]"} # Типы адресации


def main():
  pc = 0 # Счетчик команд
  mem_inst = [0] * 256 # Память команд (ОЗУ)
  mem_data = [0] * 256 # Память данных
  cf = False # Флаг переноса
  regs = [0] * 4 # Регистры
  data_part, inst_part = text.split("\n\n") # Разделяем секции данных и инструкций
  for line in data_part.split("\n"): # Перебор секции данных
    if line == "":
      continue
    parts = line.split() # Разбиение линии
    mem_data[int(parts[0], 2)] = int("".join(parts[1:]), 2) # Кладем в память данных начальный массив 
  for line in inst_part.split("\n"):
    if line == "":
      continue
    parts = line.split()
    mem_inst[int(parts[0], 2)] = int("".join(parts[1:]),2) # Кладем в память инструкций совмещенную строку в 10 сс
  while True: # Цикл работает, пока не встретит команду о завершении
    inst = mem_inst[pc] # Инструкция в 10 сс, определяемая по счетчику операции
    cmd = (inst >> 20) & 0xF # Всего имеем 24 бита     
    adr1 = (inst >> 18) & 0x3  # Расположение cmd (20-23), addr1 (18-19), op1 (10-17), adr2 (8-9), op2 (0-7)
    op1 = (inst >> 10) & 0xFF      
    adr2 = (inst >> 8) & 0x3       
    op2 = inst & 0xFF              

    instName = instruction_set_r[cmd] # Название инструкции str на основе cmd для вывода
    # adr1 = adr1 # Тип адресации 1 операнда
    # adr2 = adr2 # Тип адресации 2 операнда
    # 
    if adr1 == 2: # Если тип адресации 1го операнда загрузка значения из регистра
      op1_str = reg_set[op1] # Вытаскиваем значение из регистра
    else:
      op1_str = str(op1)
    if adr2 == 2: # Если тип адресации 2го операнда загрузка значения из регистра
      op2_str = reg_set[op2]
    else:
      op2_str = str(op2)

    print(f"PC:{pc}\tCMD:{instName}\tADR1:{adr1}\tOP1:{op1_str}\tADR2:{adr2}\tOP2:{op2_str}\tCF:{cf}\tREGS:{regs}")

    var1 = 0 # Хранение значения первого операнда
    var2 = 0 # Хранение значения второго операнда
    res = None # Хранение вычисления операции
    
    # Получаем значение второго операнда
    if adr2 == 1: # Если тип 2 адресации загрузка числа 
      var2 = op2 # Просто кладем операнд
    elif adr2 == 0: # Если тип 2 адресации загрузка из памяти по индексу
      var2 = mem_data[op2] # Получаем значение из массива данных по индексу
    elif adr2 == 2: # Если тип 2 адресации загрузка значения из регистра
      var2 = regs[op2] # Получаем значение из памяти регистров
    elif adr2 == 3: # Если тип 2 адресации загрузка из памяти по значению регистра
      var2 = mem_data[regs[op2]] # Обращаемся к памяти данных по индексу, равному регистру с индексом операнда2
    else:
      sys.exit("An error occurred")
    
    # Получаем значение первого операнда
    if cmd != 0x00: # Если не прекращаем работу командой HLT
      if adr1 == 1: # Обработка ошибки если адресация операнда 1 - Загрузка числа
        sys.exit("An error occurred")
      elif adr1 == 0: # Если тип 1й адресации загрузка из памяти данных
        var1 = mem_data[op1]
      elif adr1 == 2: # Если тип 1й адресации загрузка значения из регистра
        var1 = regs[op1]
      elif adr1 == 3: # Если тип 1й адресации загрузка из памяти по значению из регистра
        var1 = mem_data[regs[op1]]
      else:
        sys.exit("An error occurred")
    
    # В зависимости от команды производим операции с var1 и var2
    if cmd == 0x00: # Если команда HLT - прекращаем работу
      break
    elif cmd == 0x01: # Если команда MOV, кладем в результат
      res = var2
    elif cmd == 0x02: # Если команда ADD
      res = (var1 + var2) & 0xFF
      cf = (var1 + var2) > 0xFF
    elif cmd == 0x03: # Если команда ADC
      res = (var1 + var2 + cf) & 0xFF
    elif cmd == 0x04: # Если команда DEC
      res = var1 - 1
    elif cmd == 0x05: # Если команда JNZ
      if var1 != 0:
        pc = var2
        continue
        
    # Сохраняем результат операции
    if res is not None: # Если получили результат
      if adr1 == 1: # 
        sys.exit("An error occurred")
      elif adr1 == 0: # Если 1я адресация - загрузка из памяти данных
        mem_data[op1] = res
      elif adr1 == 2: # Если 1я адресация - загрузка значения из регистра
        regs[op1] = res
      elif adr1 == 3: # Если 1я адресация - загрузка из памяти по значению регистра
        mem_data[regs[op1]] = res
      else:
        sys.exit("An error occurred")

    pc += 1


import sys
if __name__ == "__main__":
  main()

'''
00000000 00000101
00000001 00001001
00000010 00000010
00000011 00000011
00000100 00000100
00000101 11111111

00000000 0001 10 00000010 00 00000000
00000001 0001 10 00000011 11 00000010
00000010 0010 10 00000001 10 00000011
00000011 0001 10 00000011 01 00000000
00000100 0011 10 00000000 10 00000011
00000101 0100 10 00000010 01 00000000
00000110 0101 10 00000010 01 00000001
00000111 0000 01 00000000 01 00000000
'''