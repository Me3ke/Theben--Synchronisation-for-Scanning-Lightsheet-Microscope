"""

"""
# -*- coding: utf-8 -*-
import os
import subprocess
from initialize.verification import Verification


def manual():
    print("The manual")


def select_mode(command, mode):
    if len(command) == 1:
        print(mode)
        return mode
    elif len(command) == 2:
        mode = command[1]
        if mode == 'running':
            return 'running'
        elif mode == 'calibration':
            return 'calibration'
        else:
            print("mode not recognized")
            return ""


def select_sequence(command, mode, sequence):
    if len(command) == 1:
        print(sequence)
        return sequence
    elif len(command) == 2:
        new_sequence = command[1]
        if new_sequence == 'continuous':
            return 'continuous'
        elif new_sequence == 'iterativ':
            if mode == 'running':
                print("cannot change sequence in running mode. Change mode first")
                return 'continuous'
            else:
                return 'iterativ'
        else:
            print("sequence not recognized")
            return 'continuous'


def select_file(command, file):
    # über command als alternative
    if len(command) == 1:
        print(file)
        return file
    elif len(command) == 2:
        if command[1] == 'new':
            process = subprocess.Popen(["powershell.exe", ".\\src\\util\\path_select.ps1"], stdout=subprocess.PIPE)
            p_out, p_err = process.communicate()
            path_to_file = p_out.decode()
            return path_to_file
        else:
            print("flag not recognized")


def run(mode, sequence, setup, param):
    verificator = Verification(mode, sequence, setup, param)
    try:
        result = verificator.verify()
    except:
        print("Theben")
        # -> show error from verification
    # -> main window


def main():
    running = True
    mode = ""
    sequence = "continuous"
    setup = ""
    param = ""

    while running:
        try:
            line = str(input("> Type in any command. Type help for manual\n"))
            os.system('cls')
            command = line.split(' ')
            if command[0] == 'quit':
                print("terminating....")
                running = False
            elif command[0] == 'help':
                manual()
            elif command[0] == 'mode':
                mode = select_mode(command, mode)
            elif command[0] == 'sequence':
                sequence = select_sequence(command, mode, sequence)
            elif command[0] == 'setup':
                setup = select_file(command, setup)
            elif command[0] == 'param':
                if mode == 'running':
                    param = select_file(command, param)
                else:
                    print("parameter cannot be selected in calibration mode")
            elif command[0] == 'run':
                if mode == "":
                    print("select a mode before running")
                elif setup == "":
                    print("select a setup before running")
                else:
                    run(mode, sequence, setup, param)
            else:
                print("command unknown")
        except KeyboardInterrupt:
            print("terminating....")
            running = False


if __name__ == "__main__":
    main()
# TODO das meiste wird nachher in die GUI ausgelagert so dass hier nur noch die angaben prozessiert und weiter
# TODO gegeben werden!
