import time, math, os
from requests_html import HTMLSession

class SteamScreenshotScraper():
    def __init__(self, steam_id: str, using_custom_id: bool):
        self.steam_id = steam_id
        self.using_custom_id = using_custom_id

    def get_screenshot_links(self, total_num_of_screenshots: int):
        temp_links: list = []
        screenshot_links: list = []
        num_of_pages = math.ceil(total_num_of_screenshots / 50)

        for x in range(1, num_of_pages + 1):
            with HTMLSession() as s:
                print(f"Scraping page {x} of {num_of_pages}")
                if self.using_custom_id:
                    r = s.get(f'https://steamcommunity.com/id/{self.steam_id}/screenshots/?p={x}&sort=newestfirst&view=grid')
                else:
                    r = s.get(f'https://steamcommunity.com/profiles/{self.steam_id}/screenshots/?p={x}&sort=newestfirst&view=grid')
                
                r.html.render(sleep=1)
                screenshots = r.html.find('a.profile_media_item.ugc')

                for screenshot in screenshots:
                    link = str(screenshot.attrs['href'])
                    temp_links.append(link)
        
        print("Getting pure image links")
        total_links = len(temp_links)
        for i,link in enumerate(temp_links):
            print(f"Getting image link {i + 1}/{total_links + 1}")
            with HTMLSession() as s:
                r = s.get(link)
                image = r.html.find('.actualmediactn a', first=True).attrs['href']
                screenshot_links.append(image)

        print(f"Gathered {len(screenshot_links)}")
        return screenshot_links

    def download_screenshots(self, links: list, folder_path: str, parent_folder_name:str):
        if not os.path.exists(f"{folder_path}/{parent_folder_name}"):
            os.mkdir(f"{folder_path}/{parent_folder_name}")
        
        if not os.path.exists(f"{folder_path}/{parent_folder_name}/screenshots"):
            os.mkdir(f"{folder_path}/{parent_folder_name}/screenshots")

        link_length = len(links)
        for i, link in enumerate(links):
            print(f"Downloading image {i + 1} of {link_length + 1}")
            with HTMLSession() as s:
                r = s.get(link)
                
                pic_data = r.html.raw_html

                with open(f"{folder_path}/{parent_folder_name}/screenshots/{i}.jpg", "wb") as f:
                    f.write(pic_data)


def scrape_and_download_screenshots(steam_id: str, using_custom_id: bool, num_of_screenshots: int, folder_path:str, parent_folder_name: str):
    scraper = SteamScreenshotScraper(steam_id, using_custom_id)
    links = scraper.get_screenshot_links(num_of_screenshots)
    scraper.download_screenshots(links, folder_path, parent_folder_name)