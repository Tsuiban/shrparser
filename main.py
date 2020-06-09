import getopt
import sys

outfile = None

"""
A lot of this parsing is fragile.  It could have been done much more elegantly.  The whole program is basically hacked
together quickly so that I can get on with the data analysis.  You're welcome to make the code more elgant if you truly
wish to.  It did what I needed at the moment, so was 'good enough' right now.

Suggestions:
    make the parsing table driven instead of hard coded.
    
    -- KNK --
"""


class Victim:
    def __init__(self, age=0, gender='', race='', ethnic=''):
        self.age = age
        self.gender = gender
        self.race = race
        self.ethnic = ethnic

    def __repr__(self):
        return f'{self.age},{self.gender},{self.race},{self.ethnic}'

    def parse(self, string):
        if string[0:2] == "NB":
            self.age = -2
        elif string[0:2] == "BB":
            self.age = -1
        elif string[0:2] == "NN":
            self.age = -3
        elif string[0:2] == '  ':
            self.age = -4
        else:
            self.age = int(string[0:2])
        self.gender = string[2]
        self.race = string[3]
        self.ethnic = string[4]

    @staticmethod
    def fromString(line):
        v = Victim()
        v.parse(line)
        return v


class Offender(Victim):
    def __init__(self, age=0, gender='', race='', ethnic='', weapon=0, relationship='', circumstances=0,
                 sub_circumstances=''):
        super().__init__(age, gender, race, ethnic)
        self.weapon = weapon
        self.relationship = relationship
        self.circumstances = circumstances
        self.sub_circumstances = sub_circumstances

    def __repr__(self):
        return f'{super().__repr__()},{self.weapon},{self.circumstances},{self.sub_circumstances}'

    def parse(self, string):
        super().parse(string)
        self.weapon = int(string[5:7])
        self.relationship = string[7:9]
        self.circumstances = int(string[9:11])
        self.sub_circumstances = string[11]

    @staticmethod
    def fromString(string):
        o = Offender()
        o.parse(string)
        return o


class Record:
    def __init__(self, line):
        self.indicator = line[0]
        self.state_code = int(line[1:3])
        self.ori_code = line[3:10]
        self.group = line[10:12]
        self.division = int(line[12])
        self.year = int(line[13:15])
        self.population = int(line[15:24])
        self.county = line[24:27]
        self.msa = line[27:30]
        self.msa_indication = int(line[30])
        self.agency = line[31:55]
        self.state_name = line[55:61]
        self.offense_month = int(line[61:63])
        self.last_update = line[63:69]
        self.action_type = int(line[69])
        self.homicide = line[70]
        self.incident_number = int(line[71:74])
        self.situation = line[74]
        self.victim = [Victim.fromString(line[75:80])]
        self.offender = [Offender.fromString(line[80:92])]
        self.victimCount = int(line[92:95])
        self.offenderCount = int(line[95:98])
        for victimNumber in range(1, min(self.victimCount, 11)):
            location = 98 + (victimNumber - 1) * 5
            self.victim.append(Victim.fromString(line[location:location + 5]))
        for victimNumber in range(1, min(self.offenderCount, 11)):
            location = 148 + (victimNumber - 1) * 12
            self.offender.append(Offender.fromString(line[location:location + 12]))

    def __repr__(self):
        outputString = f'{self.indicator},{self.state_code},{self.ori_code},{self.group},{self.division},' + \
                       f'{self.year},{self.population},{self.county},{self.msa},{self.msa_indication},' + \
                       f'{self.agency},{self.state_name},{self.offense_month},{self.last_update},' + \
                       f'{self.action_type},{self.homicide},{self.incident_number},{self.situation},' + \
                       f'{self.victim[0]},{self.offender[0]},{self.victimCount},{self.offenderCount}'
        for victimNumber in range(0, min(self.victimCount, 11)):
            outputString = outputString + self.victim[victimNumber].__repr__()
        v = Victim()
        for victimNumber in range(self.victimCount, 11):
            outputString = outputString + v.__repr__()
        for offenderNumber in range(1, min(self.offenderCount, 11)):
            outputString = outputString + self.offender[offenderNumber].__repr__()
        o = Offender()
        for offenderNumber in range(self.offenderCount, 11):
            outputString = outputString + o.__repr__()

        return outputString


# noinspection PyUnresolvedReferences
def output(string):
    if outfile is None:
        print(string)
    else:
        outfile.write(string)
        outfile.write('\n')


def processFile(file):
    while True:
        line = file.readline()
        if not line:
            break
        r = Record(line)
        output(r.__repr__())


def processFileName(fileName):
    with open(fileName, 'r') as f:
        processFile(f)


if __name__ == "__main__":
    def main(argv):
        global outfile
        mode = 'w'
        try:
            opts, args = getopt.getopt(argv, "i:o:", ["in=", "out="])
        except getopt.GetoptError:
            print("""shrparser options
            where options are one or more of the following:
                -a, --append    append to the output file instead of overwriting it.  This remains in effect until
                                cancelled by -n or --noappend
                -i, --in        specify the name of the input file.  May be repeated to specify multiple input files.
                                input files will be processed in the order specified on the input line.  Each -i/--in
                                option processes that input file immediately using the options that have already been
                                set on the command line.
                -n, --noappend  Overwrite the output file instead of appending to it.  This remains in effect until
                                cancelled by -a or --append
                                --noappend is the default mode.
                -o, --out       specify the name of the outout file.  This remains in effect for all future input files
                                until a new output file is defined.  May be repeated.  The output file will be used
                                for all input files that appear AFTER this option on the command line.

            The order of the options is important!!!!

            Because each option (other than -i/--in) affects only options that appear after it on the command line, the
            following command line might not do what you expect:

                shrparser --in inputfile --out outputfile

            It will send the processed output to the console and nothing will be in the output file.  If you wanted
            the processed output to be in outputfile, then the command line should have looked like:

                shrparser --out outputfile --in inputfile
                
            By the same token:
            
                shrparser --out outputfile --in inputfile --append
                
            will OVERWRITE the output file instead of append to it because the output file was specified before
            the --append
            """)
            sys.exit(2)

        for opt, arg in opts:
            if opt == "-i" or opt == "--in":
                if outfile is not None:
                    print(f'Processing {arg}...')
                processFileName(arg)
            elif opt == "-o" or opt == "--out":
                if arg == '-':
                    if outfile is not None:
                        outfile.close()
                        outfile = None
                else:
                    if outfile is not None:
                        outfile.close()
                    outfile = open(arg, mode)
            elif opt == "-n" or opt == "--noappend":
                mode = 'w'
            elif opt == "-a" or opt == "--append":
                mode = 'a'
        if outfile is not None:
            outfile.close()


    main(sys.argv[1:])
