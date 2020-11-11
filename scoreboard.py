
instructions_file = 'data.txt'

class FunctionalUnit:

    def __init__(self, name, instructions, ex_time, Fi, Fj, Fk):
        self.name = name
        self.instructions = instructions
        self.busy = False
        self.ex_time = ex_time
        self.time_left = ex_time
        self.Fi = Fi
        self.Fj = Fj
        self.Fk = Fk
        self.Read = True
        self.Ex = True
        self.inst_counter = 0


    def issue(self, inst, count):

        self.busy = True
        self.time_left = self.ex_time
        self.Fi = inst.location
        self.Fj = inst.reg_a
        self.Fk = inst.reg_b
        self.inst_counter = count 


    def execute(self):

        self.time_left -= 1


class instruction: 

    def __init__(self, inst, location, offset, reg_a, reg_b):
        self.inst = inst
        self.location = location
        self.offset = offset
        self.reg_a = reg_a
        self.reg_b = reg_b
        self.issue = 0
        self.read_op = 0
        self.execute = 0
        self.write = 0

        
class Scoreboard:

    def __init__(self):
        
        self.FU = []
        self.instructions = []
        self.registers = {}
        self.curr_registers = {}
        self.inst_counter = 0
        self.clk = 1
        

    def done(self):

        no_inst = True
        no_FU = True

        if(self.inst_counter < len(self.instructions)):
            no_inst = False
        if no_inst == True:
            for fu in self.FU:
                if fu.busy == True:
                    no_FU = False
                    break
        
        return no_inst and no_FU


    def parse_instructions(self, inst_file):
        with open(inst_file) as fp:
            line = fp.readline()
            while line:
                nc_line = line.replace(',','')
                inst_arr = nc_line.split()
                print(inst_arr)
                if(len(inst_arr) == 3):
                    off_loc = inst_arr[2].split('(')
                    loc = off_loc[1].replace(')', '')
                    off = off_loc[0]
                    ii = instruction(inst_arr[0], inst_arr[1], off, loc, None)
                    self.instructions.append(ii)
                    line = fp.readline()
                elif(len(inst_arr) == 4):
                    ai = instruction(inst_arr[0], inst_arr[1], None, inst_arr[2], inst_arr[3])
                    self.instructions.append(ai)
                    line = fp.readline()

                else:
                    raise SyntaxError('Invalid Input instruction')

    def init_fu(self):
        
        add_fu = FunctionalUnit('Add', ['ADD', 'ADD.D', 'ADDI', 'SUB.D', 'SUB'], 2, None, None, None)
        mul_fu = FunctionalUnit('Multiply', ['MUL.D'], 10, None, None, None)
        div_fu = FunctionalUnit('Divide', ['DIV.D'], 40, None, None, None)
        int_fu = FunctionalUnit('Integer', ['L.D', 'S.D'], 1, None, None, None)

        self.FU.append(add_fu)
        self.FU.append(mul_fu)
        self.FU.append(div_fu)
        self.FU.append(int_fu)


    def issue(self, inst, fu):
       
        fu.issue(inst, self.inst_counter)
        self.instructions[self.inst_counter].issue = self.clk
 

    def can_read(self, fu):
        
        print("checking if ", fu.name, "can read")
        
        if not bool(self.curr_registers):
            print(fu.name, "ok to read with registers ", fu.Fj, fu.Fk)
            return True
        elif fu.Read == False:
            print('Instruction already read')
            return False
        else:  
            for reg_fu in self.curr_registers:
                if fu.Fj == reg_fu.Fi or fu.Fk == reg_fu.Fi:
                    print("cannot read, register being used")
                    return False 

        
        return True

    def read(self, fu):
        
        self.curr_registers[fu] = fu
        fu.Read = False
        self.instructions[fu.inst_counter].read_op = self.clk

    def can_execute(self, fu):
        
        return not fu.Read

    def can_write(self, fu):
    
        return not fu.Ex

    def write(self, fu):
       
        del self.curr_registers[fu]
        fu.busy = False
        fu.Read = True
        fu.Ex = True
        self.instructions[fu.inst_counter].write = self.clk

    def execute(self, fu):
        
        fu.execute()
        print("Execute time left: ", fu.time_left)
        if fu.time_left == 0:
            print('Execution Complete')
            fu.Ex = False
            fu.time_left = fu.ex_time
            self.instructions[fu.inst_counter].execute = self.clk 

    def start(self):
        
        RAN_ALL_INSTRUCTIONS = False
       # while self.done() == False:
        while self.clk < 100:
            if(self.inst_counter < len(self.instructions)):     
                curr_inst = self.instructions[self.inst_counter]
            else:
                RAN_ALL_INSTRUCTIONS = True
            for fu in self.FU:
                print('\n\nCLOCK CYCLE: ', self.clk)

                #checks if issue is allowed
                if curr_inst.inst in fu.instructions and not fu.busy and not RAN_ALL_INSTRUCTIONS:

                    print(curr_inst.inst, 'is being entered into FU', fu.name)

                    self.issue(curr_inst, fu)
                    self.inst_counter += 1

                    print("count: ", self.inst_counter)

                elif fu.busy:
                    can_read = self.can_read(fu)
                    can_execute = self.can_execute(fu)
                    can_write = self.can_write(fu)
                    
                    if can_read:
                        print(fu.name, "allowed to read")
                        self.read(fu)
                    
                    elif can_execute and not can_write:
                        self.execute(fu)

                    elif can_write:
                        self.write(fu)

            self.clk += 1






if __name__ == '__main__':
    
    instructions = []

    sb = Scoreboard()

    sb.parse_instructions(instructions_file)

    sb.init_fu()

    for instruction in sb.instructions:
        
        print(instruction.inst, instruction.location, instruction.offset, instruction.reg_a, instruction.reg_b)

    sb.start()

    for instruction in sb.instructions:
        print(instruction.issue, instruction.read_op, instruction.execute, instruction.write)