import math
import pickle

class Assembler(object):
    """docstring for Assembly"""

    def __init__(self):
        super(Assembler, self).__init__()
        self.file = None
        self.lines = []
        self.sections = {}
        self.assembly = {}
        self.labels = {}
        self.R_address = 0

    # parse file
    def parse_file(self):
        with open(self.file)as file:
            for line in file:
                self.lines.append(line)
            pass
        pass
    # remove comments

    def remove_comments(self):
        for x in range(len(self.lines)):
            self.lines[x] = (self.lines[x].split("//")[0])
            pass
        pass

    # remove /n & /r
    def remove_NL(self):
        for x in range(len(self.lines)):
            self.lines[x] = self.lines[x].strip("\n")
            self.lines[x] = self.lines[x].strip("\r")
        pass

    # remove leading whitespaces
    def remove_outer_whitespaces(self):
        for x in range(len(self.lines)):
            while self.lines[x].startswith(' '):
                self.lines[x] = self.lines[x][1:]
            while self.lines[x].endswith(' '):
                self.lines[x] = self.lines[x][:-1]
        pass

    # remove empty lines
    def remove_empty_lines(self):
        try:
            while True:
                self.lines.remove('')
        except ValueError:
            pass
        pass

    # create sections
    def create_sections(self):
        section = None
        for line in self.lines:
            if line.startswith("."):
                section = line
                self.sections[line] = []
            else:
                self.sections[section].append(line)
        pass

    def address(self):
        self.clean()
        self.clean_asm = str(self.file).split(".")[0] + "_.asm"
        with open(self.clean_asm)as file:
            for line in file:
                if line.endswith(":\n"):
                    self.labels[line.strip(":\n")] = self.R_address
                else:
                    self.assembly[self.R_address] = line.strip("\n")
                    self.R_address += 4

        for data in self.sections[".data"]:
            data = data.replace(",", " ").split(" ")
            self.labels[data[0]] = self.R_address
            self.assembly[self.R_address] = f"{data[1]} {data[2]}"
            self.R_address += int(data[1])

        for data in self.sections[".bss"]:
            data = data.replace(",", " ").split(" ")
            self.labels[data[0]] = self.R_address
            self.assembly[self.R_address] = f"{data[1]} {data[2]}"
            self.R_address += int(data[1])

        for address1, line in self.assembly.items():
            for label, address2 in self.labels.items():
                if label in line:
                    self.assembly[address1] = line.replace(
                        label, str(address2))

        out = str(self.file).split(".")[0] + "_.asm"
        with open(out, mode='w')as file:
            for x, y in self.assembly.items():
                file.write(str(x) + " " + str(y) + "\n")
            pass

    def temp(self):
        string = ""
        for line in self.sections[".text"]:
            # print(line)
            string += line + "\n"
        return string

    # Override the print method
    def __str__(self):
        # string = ""
        # for section in self.sections:
        #     # print(section,end=" --> ")
        #     # string += section + " --> "
        #     # print(sections[section])
        #     # string += self.sections[section]
        #     for line in self.sections[section]:
        #         # print(line)
        #         string += line + "\n"
        # return string
        string = ""
        for x, y in self.assembly.items():
            string += (str(x) + " " + str(y) + "\n")
        return string
        pass

    # write to abinary file
    def writebin(self, file, b):
        binary_file = open(file, "ab")
        binary_file.write(b'{}')
        binary_file.close()
        print(b)
    pass

    def clean(self):
        self.parse_file()
        self.remove_comments()
        self.remove_NL()
        self.remove_outer_whitespaces()
        self.remove_empty_lines()
        self.create_sections()
        out = str(self.file).split(".")[0] + "_.asm"
        with open(out, mode='w')as file:
            file.write(self.temp())
            pass
        pass

    def assemble(self, file):
        self.registers = {"AX":0X0,"BX":0X1,"CX":0X2,"DX":0X3,"BP":0X4,"FG":0X5,"IP":0X6,"SP":0X7}
        self.file = file
        asm = str(self.file).split(".")[0] + "_.asm"
        out = str(self.file).split(".")[0] + "_.bin"
        # self.writebin(out, )
        self.file = file
        self.address()
        with open(asm) as file:
            for line in file:
                line = line.strip("\n").split(" ")[1:]
                print(line)
                if type(line[0]) == int:
                    size = math.ceil(int(line[1]).bit_length()/8)
                    length = int(line[0])
                    for x in range(length-size):
                        self.writebin(out, 0X00)
                    self.writebin(out, (int(line[1].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "LDR":
                    if line[2].endswith("X"):
                        self.writebin(out,0X01) #opcode
                        self.writebin(out, self.registers[line[1]])#R1
                        self.writebin(out,self.registers[line[2]])#R2
                    elif line[2].startswith("$"):
                        self.writebin(out,0X02) #opcode
                        self.writebin(out, self.registers[line[1]])#R1
                        self.writebin(out,(int(line[2].strip("$"))))#$0xABCD
                    else:
                        self.writebin(out, 0X00)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, (int(line[2])))  # 0xABCD
                elif line[0].upper() == "STR":
                    self.writebin(out, 0X10)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out,(int(line[2].strip("$"))))#$0xABCD
                    pass
                elif line[0].upper() == "STL":
                    self.writebin(out, 0X12)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, (int(line[2].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "STH":
                    self.writebin(out, 0X13)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, (int(line[2].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "CMP":
                    if line[2].endswith("X"):
                        self.writebin(out, 0X21)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, self.registers[line[2]])  # R2
                    else:
                        self.writebin(out, 0X20)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, (int(line[2])))  # 0xABCD
                    pass
                elif line[0].upper() == "JEQ":
                    self.writebin(out, 0X30)  # opcode
                    self.writebin(out, 0x00)  # R1
                    self.writebin(out, (int(line[1].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "JLT":
                    self.writebin(out, 0X31)  # opcode
                    self.writebin(out, 0x00)  # R1
                    self.writebin(out, (int(line[1].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "JGT":
                    self.writebin(out, 0X32)  # opcode
                    self.writebin(out, 0x00)  # R1
                    self.writebin(out, (int(line[1].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "JMP":
                    self.writebin(out, 0X33)  # opcode
                    self.writebin(out, 0x00)  # R1
                    self.writebin(out, (int(line[1].strip("$"))))  # $0xABCD
                    pass
                elif line[0].upper() == "ADD":
                    if line[2].endswith("X"):
                        self.writebin(out,0X40) #opcode
                        self.writebin(out, self.registers[line[1]])#R1
                        self.writebin(out,self.registers[line[2]])#R2
                    else:
                        self.writebin(out, 0X41)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, (int(line[2])))  # 0xABCD
                    pass
                elif line[0].upper() == "SUB":
                    if line[2].endswith("X"):
                        self.writebin(out,0X42) #opcode
                        self.writebin(out, self.registers[line[1]])#R1
                        self.writebin(out,self.registers[line[2]])#R2
                    else:
                        self.writebin(out, 0X43)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, (int(line[2])))  # 0xABCD
                    pass
                elif line[0].upper() == "RSH":
                    if line[2].endswith("X"):
                        self.writebin(out,0X50) #opcode
                        self.writebin(out, self.registers[line[1]])#R1
                        self.writebin(out,self.registers[line[2]])#R2
                    else:
                        self.writebin(out, 0X51)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, (int(line[2])))  # 0xABCD
                    pass
                elif line[0].upper() == "LSH":
                    if line[2].endswith("X"):
                        self.writebin(out,0X52) #opcode
                        self.writebin(out, self.registers[line[1]])#R1
                        self.writebin(out,self.registers[line[2]])#R2
                    else:
                        self.writebin(out,0X53)  # opcode
                        self.writebin(out, self.registers[line[1]])  # R1
                        self.writebin(out, (int(line[2])))  # 0xABCD
                    pass
                elif line[0].upper() == "NOT":
                    self.writebin(out, 0X54)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, 0X0000)  # 0xABCD
                    pass
                elif line[0].upper() == "AND":
                    self.writebin(out, 0X55)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, self.registers[line[2]])  # R2
                    pass
                elif line[0].upper() == "OR":
                    self.writebin(out, 0X56)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, self.registers[line[2]])  # R2
                    pass
                elif line[0].upper() == "XOR":
                    self.writebin(out, 0X57)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, self.registers[line[2]])  # R2
                    pass
                elif line[0].upper() == "PUSH":
                    self.writebin(out, 0X60)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, 0X0000)  # 0xABCD
                    pass
                elif line[0].upper() == "POP":
                    self.writebin(out, 0X61)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, 0X0000)  # 0xABCD
                    pass
                elif line[0].upper() == "BIC":
                    self.writebin(out, 0X62)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, self.registers[line[2]])  # R2
                    pass
                elif line[0].upper() == "BIS":
                    self.writebin(out, 0X63)  # opcode
                    self.writebin(out, self.registers[line[1]])  # R1
                    self.writebin(out, self.registers[line[2]])  # R2
                    pass
                elif line[0].upper() == "HLT":
                    self.writebin(out, 0XFF)  # opcode
                    self.writebin(out, 0XFF)  # R1
                    self.writebin(out, 0XFF)  # H_BYTE
                    self.writebin(out, 0XFF)  # R2
                    pass
                elif line[0].upper() == "NOP":
                    self.writebin(out, 0XFF)  # opcode
                    self.writebin(out, 0XFE)  # R1
                    self.writebin(out, 0XFF)  # H_BYTE
                    self.writebin(out, 0XFE)  # R2
                    pass
                else:
                    return ValueError(f"{line[0]} is not a valid Token")
                    pass
            pass


def main():
    A1 = Assembler()
    A1.assemble('fib.txt')
    # print(A1)
    pass


if __name__ == '__main__':
    main()
