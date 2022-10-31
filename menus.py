import time, os, commands.screenshot_scraper

### GLOBAL VARIABLES ###
global_sleep_time = 2 # The amount of seconds the error text will show on a menu, before continuing the loop.


###  END OF GLOBALS  ###

def init_menu_main():
    return_data: tuple
    while True:
        os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
        
        print("Welcome to Steam Detective\nTo start, select one of the options below.")
        print('''Are you entering a Custom Steam ID or a Profile ID
                
                A Custom Steam ID, is one a user has created themselves.
                A Non-Custom Steam is a random set of numbers, generated by Valve when a user creates their Steam account.

                1. Custom Steam ID
                2. Non-Custom Steam ID
                0. Exit
            ''')
    
        choice = input("Please select an option: ")

        if not choice.isnumeric():
            print("Your option should only be a number, please try again.")
            time.sleep(global_sleep_time)
            continue

        if int(choice) == 1:
            return_data = init_menu_custom_id()
            break
        elif int(choice) == 2:
            return_data = init_menu_steam_id()
            break
        elif int(choice) == 0:
            return exit()
            break
        else:
            print(f"'{choice}' isn't a valid option, please try again.")
            time.sleep(global_sleep_time)
            continue

    return return_data

def init_menu_custom_id():
    while True:
        os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
        print("You have selected to use a Custom Steam ID, if this is wrong please go back.\nOtherwise please enter the Custom Steam ID\n0. Back")
        choice = input("Enter Custom Steam ID: ")

        if choice == "0" or choice == 0:
            init_menu_main()
            break
        
        if choice == "":
            print("Please enter the Steam ID, before pressing enter.")
            time.sleep(global_sleep_time)
            continue

        return (choice, True)

def init_menu_steam_id():
        while True:
            os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
            print("You have selected to use a Non-Custom Steam ID, if this is wrong please go back.\nOtherwise please enter the ID\n0. Back")
            choice = input("Enter Non-Custom Steam ID: ")

            if choice == "0" or choice == 0:
                init_menu_main()
                break
            
            if not choice.isnumeric():
                print("A Profile ID cannot contain any non-number characters, please try again.")
                time.sleep(global_sleep_time)
                continue

            return (choice, False)

def main_menu(general_info_data: dict, steam_id: str, using_custom_id: bool, folder_path: str):
    filename = steam_id
    show_update_messages = True

    while True:
        os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
        print(f'''Steam account we are getting information about
        Steam Alias: {general_info_data['steam_name']}
        Steam Bio: {general_info_data['bio']}
        Steam Level: {general_info_data['level']}

        If this is the correct account, type 'start' otherwise exit and try again.

        Also feel free to change any settings below before starting the scan.

        TEXT OPTIONS:
        'start'. Start the detective, and scrape all data.
        'screenshots'. Scrape and Download the users screenshots.

        NUMERIC OPTIONS:
        1. Change saved filename (Currently: {filename}.json)
        2. Toggle update messages: (Currently: {"on" if show_update_messages == True else "off"})
        0. Exit
        ''')

        choice = input("Enter your choice: ")

        if choice == "1":
            os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
            print("Note: Changing the filename will not change it's extention!")
            second_choice = input("Enter new filename for output file: ")

            if second_choice == "":
                print("Filename cannot be empty, reverting to last filename.")
                time.sleep(global_sleep_time)
                continue

            if second_choice.startswith(" ") or second_choice.endswith(" "):
                time.sleep(global_sleep_time)
                print("Filename cannot start or end with a space, reverting to last filename.")
                continue

            filename = second_choice
        elif choice == "2":
            show_update_messages = not show_update_messages
            continue
        elif choice == "start":
            return (filename, show_update_messages)
        elif choice == "screenshots":
            screenshot_scrape_menu(general_info_data, steam_id, using_custom_id, folder_path)
        elif choice == "0":
            exit()
        else:
            print(f"Invalid option '{choice}', please try again.")

def screenshot_scrape_menu(general_info_data: dict, steam_id: str, using_custom_id: bool, folder_path: str):
    num_of_screenshots = int(general_info_data['screenshots'])
    parent_folder_name = steam_id

    while True:
        os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
        print(f'''You have chosen to scrape and download all screenshots for {general_info_data['steam_name']}
        Number of screenshots, that will be downloaded: {num_of_screenshots}

        This could take a few minutes for the whole process to finish, depending on how many screenshots there are. If you're happy and just want to continue, press 1.
        Feel free to change any of the settings below.

        Note: the script will create a folder for you, unless there is already one made.

        1. Start Scraping
        2. Directory name, where screenshots will be saved (Currently: {parent_folder_name})
        0. Back
        ''')

        choice = input("Enter your choice: ")

        if not choice.isnumeric():
            print("Choice must be a number, try again.")

        if choice == "1":
            commands.screenshot_scraper.scrape_and_download_screenshots(steam_id, using_custom_id, num_of_screenshots, folder_path, parent_folder_name)
            os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
            print(f"{num_of_screenshots} screenshots downloaded, and saved in to '{folder_path}/{parent_folder_name}'")
            no_choice = input("Press enter to continue back to the main menu!")
            break
        elif choice == "2":
            os.system("cls" if os.name == 'nt' else 'clear') # Select the correct way to clear a screen, based on OS
            print("Changing the directory name, will not change its location; even if you use a path for the name.")
            choice2 = input("Choose a new name for the directory, where your screenshots will be held: ")

            if choice2.startswith(" ") or choice2.endswith(" "):
                print("Directory name cannot start or end with a space, reverting to previous name.")
                time.sleep(global_sleep_time)
                continue
            parent_folder_name = choice2
        elif choice == "0":
            break
        else:
            print(f"Invalid option '{choice}', please try again.")

        
