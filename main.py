import os
import json
import time
import sys
from datetime import datetime


USER_FILE = "user_data.json"
DIFFICULTY_LEVELS = "levels.json"
TEMP_USER_FILE = "temp_user_data.json"

# =============================
# Launch Sequence + Main Menu
# =============================


def start():
    """
    Launch point for the program
    :return:
    """
    print("LIFE FLIGHT SIMULATOR (v0.1)")
    print("Taking flight...")
    time.sleep(1)

    user_data = None
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            user_data = json.load(f)

    if not user_data or not user_data["user_name"]:
        run_user_setup()

    main_menu()


def main_menu():
    """
    Main menu, controller for all other screens and flows
    :return:
    """
    menu = [
        "\n################################\n"
        "MISSION CONTROL\n"
        "################################\n",
        "MAIN MENU",
        "[1] Log Mission",
        "[2] View Mission Log",
        "[3] Adjust Difficulty",
        "[4] Reset Account",
        "\nTip: Power users can skip menus!\nTry typing: 'log sleep 7'",
        "\nEnter your [selection], or 'b' to exit:"
    ]

    while True:
        for line in menu:
            time.sleep(0.125)
            print(line)

        select = input(">> ")
        if select.startswith("log"):
            power_log(select)
        if select == "1":
            run_log_mission()
        if select == "2":
            read_log_activity()
        if select == "3":
            run_adjust_difficulty()
        if select == "4":
            run_reset_account()
        if select == "b":
            print("\nPowering down, over and out.")
            break


# =============================
# New User Flow
# =============================

def run_user_setup():
    """
    Controller for the user setup flow
    :return:
    """

    # Collect user's name
    name = screen_get_name()

    # Difficulty selection loop
    while True:
        user_difficulty = screen_choose_difficulty()
        time.sleep(0.5)
        confirm = screen_confirm_difficulty(user_difficulty)
        time.sleep(0.5)

        if confirm:
            write_user_data(name, user_difficulty)
            break
        else:
            continue

    # End sequence, return to main menu
    print("\nMISSION IS A GO\n"
          "Navigating to mission control...")
    time.sleep(1)

    return


def screen_get_name():
    """
    User name entry screen
    :return:
    """
    name = input("\nWelcome recruit, please state your name:\n>> ")
    return name


def screen_choose_difficulty():
    """
    User difficulty selection screen
    :return:
    """
    with open(DIFFICULTY_LEVELS, "r") as f:
        presets = json.load(f)["difficulty_presets"]

    while True:
        print("\nSelect a difficulty level for your mission:")
        menu_index = 0
        for preset in presets:
            print(f"[{menu_index+1}] {preset['id'].upper()}")
            goals = preset["goals"]
            print(f"\t- Sleep: {goals['sleep']['target']}+ {goals['sleep']['unit']} per day\n"
                  f"\t- Fitness: {goals['fitness']['target']} {goals['fitness']['unit']} per week\n"
                  f"\t- Screen Time: <{goals['screen_time']['target']} {goals['screen_time']['unit']} per day\n")
            menu_index += 1

        choice = input("Enter the [number] corresponding to your mission choice, or 'help' "
                       "for advice on how to choose an appropriate level.\n>> ")
        if choice == 'help':
            screen_difficulty_help()
        else:
            try:
                choice_index = int(choice) - 1
                return presets[choice_index]
            except ValueError:
                print("Invalid selection")
                continue


def screen_confirm_difficulty(preset):
    """
    Confirmation of user difficulty selection
    :return:
    """
    while True:
        print(f"\nYou selected [{preset['id'].upper()}].\n")
        # Loop through selected level challenges and display
        goals = preset["goals"]
        print(f"\t- Sleep: {goals['sleep']['target']}+ {goals['sleep']['unit']} per day\n"
              f"\t- Fitness: {goals['fitness']['target']} {goals['fitness']['unit']} per week\n"
              f"\t- Screen Time: <{goals['screen_time']['target']} {goals['screen_time']['unit']} per day\n")

        print("Please confirm your mission difficulty:\n"
              "(Enter 'y' to confirm, or 'b' to return to selection page)")

        select = input(">> ")
        if select == "y":
            return True
        elif select == "b":
            return False
        else:
            print("Invalid selection")
            continue


def screen_difficulty_help():
    """Assistance screen for choosing difficulty preset"""
    print("This training program was designed not just to track habits, but to build and reinforce them.\n"
          "Whether it is sleep, fitness, or screen time, lifestyle adjustments are hard to make, and even "
          "harder to turn into habits.\n"
          "To maximize your chances at success, the starting point for your goals should be attainable.\n"
          "It is recommended to choose the starting difficulty level for this program that most closely "
          "resembles your current lifestyle.\n"
          "If you are unsure, start at the [Cadet] difficulty preset.\n"
          )

    input("Press [enter] to return to difficulty selection")
    return

# =============================
# Log Mission Flow
# =============================


def run_log_mission():
    """
    Controller for the log mission flow
    :return:
    """

    with open(USER_FILE, "r") as f:
        user_difficulty = json.load(f)["difficulty_id"]

    with open(DIFFICULTY_LEVELS, "r") as f:
        presets = json.load(f)["difficulty_presets"]

    for preset in presets:
        if preset["id"] == user_difficulty:
            user_goals = preset["goals"]

    while True:
        activity = screen_select_activity(user_goals)

        # Return to main menu
        if not activity:
            return

        units = user_goals[activity]["unit"]

        # Log activity loop
        while True:
            # Capture log data
            log_entry = screen_log_activity(activity, units)

            # Return to activity select
            if not log_entry:
                break

            # Confirm selection
            else:
                confirm = screen_confirm_activity(activity, log_entry, units)

            # Write data to log
            if confirm:
                write_log_activity(activity, log_entry, units)
                print("Entry confirmed.")
                break


def screen_select_activity(user_goals):
    """
    Activity selection screen for logging data
    :return: String containing goal name selected
    """
    goals = list(enumerate(user_goals, start=1))

    while True:
        print("\nSelect activity to log:")
        for goal in goals:
            print(f"[{goal[0]}] {goal[1].title()}")

        choice = input("\nEnter a [number] to select, or 'b' to return to Mission Control\n>> ")

        # Return to menu
        if choice == "b":
            return False

        try:
            # *** Validation microservice ***
            choice = int(choice) - 1
            return goals[choice][1]
        except ValueError:
            print("Invalid selection")
            continue


def screen_log_activity(activity, units):
    """
    Data entry screen for activity
    :return: Log entry data, or return command to activity selection screen
    """
    while True:
        print(f"\nEnter {activity} {units}, or 'b' to return to previous page:")
        data = input(">> ")

        if data.isnumeric():
            return float(data)
        elif data == "b":
            return False
        else:
            print("Invalid selection, please enter a number or 'b' to return to goal selection.")
            continue


def screen_confirm_activity(activity, log_entry, units):
    """
    Confirmation screen for data entry
    :return:
    """
    while True:
        print(f"\nYou entered {log_entry} {activity} {units}:")
        confirm = input("Enter 'y' to confirm, or 'b' to edit\n>> ")
        if confirm == "y":
            return True
        elif confirm == "b":
            return False
        else:
            print("Invalid selection")


# =============================
# Adjust Difficulty Flow
# =============================

def run_adjust_difficulty():
    """
    Controller for difficulty adjust flow
    :return:
    """
    with open(USER_FILE, 'r') as f:
        user_data = json.load(f)

    with open(DIFFICULTY_LEVELS, 'r') as f:
        levels = json.load(f)

    difficulty_id = user_data["difficulty_id"]
    levels = levels["difficulty_presets"]

    # Retrieve current difficulty
    for preset in levels:
        if preset["id"] == difficulty_id:
            current_difficulty = preset

    # Top level for difficulty flow
    while True:

        # Display current difficulty
        while True:
            proceed = screen_current_difficulty(current_difficulty)
            ### Data validation
            if proceed:
                break
            if not proceed:
                return

        # Warning for difficulty change
        while True:
            proceed = screen_difficulty_warning()
            ### Data validation
            if proceed:
                break
            if not proceed:
                return

        # Difficulty selection
        while True:
            user_difficulty = screen_choose_difficulty()
            while True:
                confirm = screen_confirm_difficulty(user_difficulty)

                if confirm:
                    user_data["difficulty_id"] = user_difficulty["id"]
                    with open(USER_FILE, "w") as f:
                        json.dump(user_data, f)
                    print("\nNew difficulty level confirmed.")
                    print("Navigating to Mission Control...")
                    return
                else:
                    break


def screen_current_difficulty(current_difficulty):
    """
    Start screen for difficulty adjustment, shows current level and goals
    :param current_difficulty: Details pertaining to current preset
    :return:
    """
    while True:
        print(f"\nYour current difficulty level: {current_difficulty["id"].upper()}")
        for goal, params in current_difficulty["goals"].items():
            print(f"\t - {goal.replace("_"," ").title()}: {params["target"]} {params["unit"]}")
        print("\nEnter 'y' if you want to edit mission difficulty, or 'b' to return to Mission Control.")
        choice = input(">> ")

        if choice == "y":
            return True
        elif choice == "b":
            return False
        else:
            print("Invalid selection")
            continue


def screen_difficulty_warning():
    """
    Warning screen for difficulty adjustment
    :return:
    """
    while True:
        print("\n*** Are you sure you want to adjust your difficulty level? ***")
        print("\nWARNING: Changing difficulty will reset your currently weekly streak.")
        print("\nEnter 'y' to proceed, or 'b' to return to Mission Control")
        choice = input(">> ")
        if choice == "y":
            return True
        elif choice == "b":
            return False
        else:
            print("Invalid selection")
            continue


# =============================
# Reset Account
# =============================
def run_reset_account():
    """
    Saves archived user file and resets account
    :return:
    """
    proceed = screen_start_reset()
    if not proceed:
        return

    proceed = screen_archive_file()
    if not proceed:
        return

    delete_user_file()


def screen_start_reset():
    """Entry screen for account reset flow"""
    while True:
        print(f"\nAre you sure you want to reset your account?"
              f"\nWARNING: Resetting your account will remove all logs and streaks."
              f"\nHowever, your user data will be archived for future use."
              f"\nEnter 'y' to proceed, or 'b' to return to Mission Control")
        entry = input(f"\n>> ")

        if entry == "y":
            return True
        elif entry == "b":
            return False
        else:
            print("Invalid selection")
            continue


def screen_archive_file():
    """Collects filename and archives user file"""
    with open(USER_FILE, "r") as f:
        user_data = json.load(f)

    while True:
        filename = input(f"\nPlease enter a unique filename to archive your data to, or 'b' to exit: ")
        if filename == "b":
            return False
        try:
            with open(f"user_archive/{filename}.json", 'w') as f:
                json.dump(user_data, f)
            return True
        except FileExistsError:
            print("Invalid filename")
        except Exception as e:
            print(f"Error creating file: {e}")
            return False


# =============================
# Data Layer
# =============================

def write_user_data(name, preset):
    """
    Writes user data to the user data file
    :param name: User's name
    :param preset: User difficulty ID
    :param user_data: User data from JSON
    """
    user_data = dict()

    user_data["user_name"] = name
    user_data["difficulty_id"] = preset["id"]
    user_data["flight_logs"] = []
    with open(USER_FILE, "w") as f:
        json.dump(user_data, f)

    return


def write_log_activity(activity, log_entry, units):
    """
    Writes log entry to the user data file
    :param activity: Log activity ID
    :param log_entry: Log entry data
    :return:
    """
    with open(USER_FILE, "r") as f:
        user_data = json.load(f)

    log_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
            "timestamp": log_timestamp,
            "activity": activity,
            "quantity": log_entry,
            "units": units
             }
    user_data["flight_logs"].append(entry)

    with open(TEMP_USER_FILE, "w") as f:
        json.dump(user_data, f)

    os.replace(TEMP_USER_FILE, USER_FILE)

    return


def read_log_activity():
    """
    Reads logged activity from the user data file
    :return:
    """
    with open(USER_FILE, "r") as f:
        user_data = json.load(f)

    name = user_data["user_name"]
    difficulty_id = user_data["difficulty_id"]
    flight_logs = user_data["flight_logs"]

    print(f"\n###### FLIGHT LOGS FOR {name.upper()} [{difficulty_id.upper()}] ######")
    for log in flight_logs:
        print(f"[{log['timestamp']}] {log['activity'].title().replace("_", " ")} - {log['quantity']} {log['units']}")

    input("\nPress [enter] to return to mission control.")
    return


def delete_user_file():
    """Deletes user data file"""
    print(f"\nAre you sure you want to delete the user data file?"
          f"\nWARNING: Deleting user data will remove all logs and streaks."
          f"\nEnter 'CONFIRM' to proceed, or 'b' to return to Mission Control")

    while True:
        entry = input(f"\n>> ")
        if entry == "CONFIRM":
            os.remove("user_data.json")
            print(f"User file moved to archive.")
            print(f"Quitting program, user setup will initiate upon restart.")
            sys.exit(0)
        elif entry == "b":
            return
        else:
            print("Invalid selection")
            continue


def power_log(command):
    """
    Adds data to mission log from main menu command
    :param command: Power command string
    :return:
    """
    with open(DIFFICULTY_LEVELS, 'r') as f:
        difficulty_levels = json.load(f)["difficulty_presets"]

    with open(USER_FILE, "r") as f:
        user_data = json.load(f)

    try:
        # Power command parameters
        params = command.split()
        activity = params[1]
        num = float(params[2])

        # Retrieve user goals
        user_level = user_data["difficulty_id"]
        for level in difficulty_levels:
            if level["id"] == user_level:
                goals = level["goals"]

        # Retrieve units for activity
        units = goals[activity]["unit"]
        write_log_activity(activity, num, units)

        # Print confirmation
        print(f"\n{num} {activity} {units} logged.")

    except Exception as e:
        print(f"Invalid command: {e}")
        return


if __name__ == "__main__":
    start()
