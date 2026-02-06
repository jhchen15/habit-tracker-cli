import os
import json
import time
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
    time.sleep(1)
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
        "MAIN MENU",
        "[1] Log Mission",
        "[2] View Mission Log"
    ]

    while True:
        print("\n################################\n"
              "MISSION CONTROL\n"
              "################################\n")

        for line in menu:
            print(line)

        select = input("\nEnter your [selection], or 'b' to exit:\n>> ")
        if select == "1":
            run_log_mission()
        if select == "2":
            read_log_activity()
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
    with open(DIFFICULTY_LEVELS, "r") as f:
        difficulty_presets = json.load(f)["difficulty_presets"]

    with open(USER_FILE, "r") as f:
        user_data = json.load(f)

    # Collect user's name
    name = screen_get_name()

    # Difficulty selection loop
    while True:
        user_difficulty = screen_choose_difficulty(difficulty_presets)
        time.sleep(0.5)
        confirm = screen_confirm_difficulty(user_difficulty)
        time.sleep(0.5)

        if confirm:
            write_user_data(name, user_difficulty, user_data)
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


def screen_choose_difficulty(presets):
    """
    User difficulty selection screen
    :return:
    """
    while True:
        print("\nSelect a difficulty level for your mission:")
        menu_index = 0
        for preset in presets:
            print(f"[{menu_index+1}] {preset['id'].upper()}")
            goals = preset["goals"]
            print(f"\t- Sleep: {goals['sleep']['target']}+ {goals['sleep']['unit']} per day\n"
                  f"\t- Fitness: {goals['fitness']['target']} {goals['fitness']['unit']} per week\n"
                  f"\t- Screen Time: <{goals['screen_time']['limit']} {goals['screen_time']['unit']} per day\n")
            menu_index += 1

        choice = input("Enter the [number] corresponding to your mission choice\n>> ")
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
              f"\t- Screen Time: <{goals['screen_time']['limit']} {goals['screen_time']['unit']} per day\n")

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
# Data Layer
# =============================

def write_user_data(name, preset, user_data):
    """
    Writes user data to the user data file
    :param name: User's name
    :param preset: User difficulty ID
    :param user_data: User data from JSON
    """
    user_data["user_name"] = name
    user_data["difficulty_id"] = preset["id"]
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

    print(f"###### FLIGHT LOGS FOR {name.upper()} [{difficulty_id.upper()}] ######\n")
    for log in flight_logs:
        print(f"[{log['timestamp']}] {log['activity'].title().replace("_", " ")} - {log['quantity']} {log['units']}")

    input("\nPress [enter] to return to mission control.")
    return


if __name__ == "__main__":
    start()
