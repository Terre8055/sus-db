"""CLI Module for SusDB, specifically IRs.

Currently, support is provided for the following commands

@store_user_string_command
@deserialize_data_command
@verify_user_command
@display_user_db_command

"""
import argparse, argon2
from user_db_manager import UserDBManager
from main import parse_accept_init  # Import the new function


parser = argparse.ArgumentParser(
    prog='susdb',
    description='Welcome to SusDB Command Line Interface \
        =================================================\
        =================================================\
        SusDB CLI to store strings, key client credentials \
        on Top of Linux File System using underlying systems \
        such as native Python dbm tech and Redis',
    epilog='Thanks for using %(prog)s, contributions welcome at \
        https://github.com/Terre8055/sus-db :)'
)

subparsers = parser.add_subparsers(dest="command", help="Available commands")

store_parser = subparsers.add_parser("store", help="Store a user string")
store_parser.add_argument("--string", required=True, help="User string to store")
store_parser.add_argument("--accept-init", action="store_true", help="Accept initialization if needed")

verify_user_parser = subparsers.add_parser("verify", help="Verify user credentials")
verify_user_parser.add_argument("--uid", required=True, help="Unique ID to locate db")
verify_user_parser.add_argument("--string", required=True, help="User string")
verify_user_parser.add_argument("--accept-init", action="store_true", help="Accept initialization if needed")


display_db_parser = subparsers.add_parser("view", help="View user db store")
display_db_parser.add_argument("--uid", required=True, help="Unique user id to locate db")
display_db_parser.add_argument("--accept-init", action="store_true", help="Accept initialization if needed")

deserialize_parser = subparsers.add_parser("retrieve", help="Retrieve user data from store")
deserialize_parser.add_argument("--uid", required=True, help="Unique user id to locate db")
deserialize_parser.add_argument("--key", required=True, help="Data to deserialize from db")
deserialize_parser.add_argument("--accept-init", action="store_true", help="Accept initialization if needed")

account_removal = subparsers.add_parser("close", help="Close user account from store")
account_removal.add_argument("--uid", required=True, help="Unique user id to locate db")
account_removal.add_argument("--sus", required=True, help="Secure User String to verify integrity")
account_removal.add_argument("--accept-init", action="store_true", help="Accept initialization if needed")


###########################################################
###############         METHODS     #######################
###########################################################

def store_user_string_command(args):
    """Store User Strings in db

    Args:
        args (_type_): Positional Arguments/subcommands - u_str
    """
    user_string = args.string
    req = {'request_string': user_string}
    uid = UserDBManager(accept_init=args.accept_init).store_user_string(req).get('id')
    print(uid)


def deserialize_data_command(args):
    """Display User db

    Args:
        args (_type_): Positional Arguments/subcommands - uid
    """
    user_id = args.uid
    user_key = args.key
    user_data = UserDBManager(user_id, accept_init=args.accept_init).deserialize_data(user_id, user_key)
    print(user_data)
    

def verify_user_command(args):
    """Store User Strings in db

    Args:
        args (_type_): Positional Arguments/subcommands - u_str
    """
    user_string = args.string
    user_id = args.uid
    req = {'request_string': user_string, 'uid': user_id}
    try:
        msg = UserDBManager(user_id, accept_init=args.accept_init).verify_user(req)
        print(msg)
    except argon2.exceptions.InvalidHashError:
        print('Invalid parameters passed to CLI, Check uid or string')
    

def display_user_db_command(args):
    """Display User db

    Args:
        args (_type_): Positional Arguments/subcommands - uid
    """
    user_id = args.uid
    user_db_view = UserDBManager(user_id, accept_init=args.accept_init).display_user_db(user_id)
    print(user_db_view)
    
    
def remove_user_account(args):
    """Remove User db

    Args:
        args (_type_): Positional Arguments/subcommands - uid / sus
    """
    user_id = args.uid
    secured_user_string = args.sus
    req = {'uid': user_id, 'sus': secured_user_string}
    response = UserDBManager(user_id, accept_init=args.accept_init).close_account(req)
    print(response)
    

if __name__ == "__main__":
    args = parser.parse_args()
    match args.command:
        case "store":
            store_user_string_command(args)
        case "view":
            display_user_db_command(args)
        case "retrieve":
            deserialize_data_command(args)
        case "verify":
            verify_user_command(args)
        case "close":
            remove_user_account(args)
