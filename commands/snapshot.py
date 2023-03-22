import os
from requests_html import HTMLSession
from datetime import datetime
def get_and_save_steam_snapshot(steam_id: str, using_custom_id: bool, folder_path: str, folder_name: str):
    
    with HTMLSession() as s:
        if using_custom_id:
            r = s.get(f'https://steamcommunity.com/id/{steam_id}')
        else:
            r = s.get(f'https://steamcommunity.com/profiles/{steam_id}')

    
    html = r.html.raw_html

    if not os.path.exists(f"{folder_path}/{folder_name}"):
        os.mkdir(f"{folder_path}/{folder_name}")

    if not os.path.exists(f"{folder_path}/{folder_name}/snapshots"):
        os.mkdir(f"{folder_path}/{folder_name}/snapshots")

    sub_folder_name = datetime.now().replace(microsecond=0)
    os.mkdir(f"{folder_path}/{folder_name}/snapshots/{sub_folder_name}")

    with open(f"{folder_path}/{folder_name}/snapshots/{sub_folder_name}/index.html", "wb") as f:
        f.write(html)

    print(f"Snapshot saved to '{folder_path}/{folder_name}/snapshots/{sub_folder_name}/index.html'")
    choice = input("Press enter to return to main menu...")  
