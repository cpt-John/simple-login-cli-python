import os
import json
import re


class Fore:
    LIGHTGREEN_EX = ''
    LIGHTBLUE_EX = ''
    GREEN = ''
    RED = ''
    YELLOW = ''
    CYAN = ''


class Style:
    RESET_ALL = ''


try:
    from colorama import Fore, Style
    pass
except:
    print("colorama import failed")


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    return False


# Emulate Database table/column names
files = {'users': 'users'}
FIELDS = {'Email': 'Email', 'Password': 'Password'}


def file_operation(file_name, data=None):  # Emulate Database R/W operations
    # don't worry if you don't have the files for initial run
    try:
        if data:
            with open(f"{file_name}.json", 'w') as outfile:
                json.dump(data, outfile)
        else:
            with open(f"{file_name}.json", 'r') as openfile:
                json_object = json.load(openfile)
                return json_object
    except:
        return False


# Load records to memory and Emulate Database tables
users = file_operation(files['users'])
if not users:
    users = {}


username = ''  # Emulate redis cache for tokens


def pretty_print_statement(string, line='.', length=6, color=''):
    print(f"\n{color}{line*length}{string}{line*length}\n{Style.RESET_ALL}")


def pretty_print_dict(dict):
    string = '-'*25+'\n'
    for key in list(dict.keys()):
        spaces = max(14 - len(key), 1)
        string += f"{key}{' '*spaces}: {dict[key]}\n"
    string += '='*25
    print(f'{Fore.LIGHTBLUE_EX}{string}{Style.RESET_ALL}')


def regex_validate(type, test_string):
    switch = {
        "Email": re.compile(r"^[a-zA-Z][\w\d]{2,10}@\w{3,10}.\w{2,5}$"),
        "Password": re.compile(
            r'(?=^.{5,16}$)(?=^[\w0-9-+!@#$%^&*.?]+$)(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[-+_!@#$%^&*.?]).*$')
    }
    return bool(re.search(switch[type], test_string))


def validate(validate_func, function_args):
    return bool(validate_func(*function_args))


def register():
    email = input("enter email(username): ").strip()
    password = input("enter password: ").strip()
    field_args = [[FIELDS["Email"], email], [FIELDS["Password"], password]]
    regex_validation_result = [
        validate(regex_validate, args) for args in field_args]
    if len(regex_validation_result) != sum(regex_validation_result):
        error_field = field_args[regex_validation_result.index(False)][0]
        pretty_print_statement(f"{error_field} is invalid", color=Fore.RED)
        return False
    if email in users:
        pretty_print_statement("Username Already Taken!", color=Fore.RED)
        return False
    selected = input("Confirm details?(y/n): ").strip().lower()
    if selected == 'y':
        users[email] = password
        pretty_print_statement("Registered! Please Login",
                               color=Fore.LIGHTGREEN_EX)
        file_operation(files['users'], users)
        return True
    return False


def login():
    email = input("enter email(username): ").strip()
    password = input("enter password: ").strip()
    response = email in users and password == users[email]
    if response:
        pretty_print_statement(
            "Logged in!", color=Fore.LIGHTGREEN_EX)
        global username
        username = email
        pretty_print_dict({"User name": username})
        return True
    if email not in users:
        pretty_print_statement(
            "User not found! Please register! ", color=Fore.RED)
    else:
        pretty_print_statement(
            "Wrong Password Try again!", color=Fore.RED)
    return False


def forgot_password():
    email = input("enter email(username): ").strip()
    response = email in users
    if response:
        pretty_print_statement(
            f"Your password is: {users[email]}", color=Fore.LIGHTGREEN_EX, length=0)
        return True
    pretty_print_statement(
        "User not found! Please register! ", color=Fore.RED)
    return False


def change_password():
    password = input("enter password: ").strip()
    result = regex_validate(FIELDS["Password"], password)
    if result:
        global username
        users[username] = password
        file_operation(files['users'], users)
        pretty_print_statement(
            "Password Changed! ", color=Fore.GREEN)
        return True
    pretty_print_statement(
        "Invalid Password! Password not changed! ", color=Fore.RED)
    return False


def log_out():
    selected = input("Confirm Logout?(y/n): ").lower()
    global username
    if selected == 'y':
        username = ''
        pretty_print_statement("Logged Out!", color=Fore.LIGHTYELLOW_EX)
        return True
    return False


def quit():
    pretty_print_statement("Quitting!", '*', 8, color=Fore.YELLOW)
    return True


states = {  # Emulate frontend using cli
    1: {
        'query':
        lambda: input(
            "Login, Register, ForgotPassword? (l/r/f)(q/cls): ")
            .strip().lower(),
        'functions': {
            'l': {'f': login, 's': 2},
            'r': {'f': register, 's': 1},
            'f': {'f': forgot_password, 's': 1},
            'q': {'f': quit, 's': 0},
            'cls': {'f': clear_terminal, 's': 1},
        }
    },
    2: {
        'query':
        lambda: input(
            "Logout, Change Password? (l/c)(q/cls): ")
            .strip().lower(),
        'functions': {
            'l': {'f': log_out, 's': 1},
            'c': {'f': change_password, 's': 2},
            'cls': {'f': clear_terminal, 's': 2},
            'q': {'f': quit, 's': 0},
        }
    },


}


def state_manager(state):
    state_obj = states[state]
    response = state_obj['query']()
    if response in state_obj['functions']:
        success = False
        success = state_obj['functions'][response]['f']()
        if success:
            state = state_obj['functions'][response]['s']
    return state


def main():
    pretty_print_statement(
        "STARTING APPLICATION(use cls to clear & q to quit)", '*', 10, Fore.GREEN)
    state = 1
    while state:
        state = state_manager(state)


main()  # Execution starts here
