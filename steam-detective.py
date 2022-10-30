import sys, json, os, time, re, concurrent.futures, asyncio, achievements, pprint
from requests_html import HTMLSession, HTMLResponse, AsyncHTMLSession

profile_id: str

class SteamSpy:
    def __init__(self):
        self.achievements = []
        self.achievement_count = 0

    def general_get_page_html(self, profile_id: str):
        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}')
        return r

    def general_get_basic_info(self, page_html: HTMLResponse):
        '''Get all basic information, such as: name, bio, level etc.'''
        steam_name: str
        steam_bio: str
        steam_level: int

        real_name: str

        steam_games: int
        steam_screenshots: int
        steam_reviews: int
        steam_friends: int
        steam_awards: int

        steam_name = page_html.html.find('div.persona_name span.actual_persona_name', first=True).text.strip()
        steam_bio = page_html.html.find('div.profile_summary', first=True).text.strip()
        steam_level = int(page_html.html.find('div.friendPlayerLevel span.friendPlayerLevelNum', first=True).text.strip())
        try:
            steam_games = int(page_html.html.find('a[href*=games] span.profile_count_link_total', first=True).text.replace(',', '').strip())
        except AttributeError:
            steam_games = None
        steam_screenshots = int(page_html.html.find('a[href*=screenshots] span.profile_count_link_total', first=True).text.replace(',', '').strip())
        try:
            steam_reviews = int(page_html.html.find('a[href*=recommended] span.profile_count_link_total', first=True).text.replace(',', '').replace(',', '').strip())
        except AttributeError:
            steam_reviews = None
        try:
            steam_friends = int(page_html.html.find('a[href*=friends] span.profile_count_link_total', first=True).text.replace(',', '').strip())
        except AttributeError:
            steam_friends = None
        try:
            steam_awards = int(page_html.html.find('a[href*=awards] span.profile_count_link_total', first=True).text.replace(',', '').strip())
        except AttributeError:
            steam_awards = None

        real_name = page_html.html.find('div.header_real_name.ellipsis bdi', first=True).text.strip()

        profile_info = {
            'steam_name':steam_name,
            'bio':steam_bio,
            'level':steam_level,
            'games':steam_games,
            'screenshots':steam_screenshots,
            'reviews':steam_reviews,
            'friends':steam_friends,
            'awards':steam_awards
        }

        return profile_info

    def profile_has_vacban(self, page_html: HTMLResponse):
        ban = page_html.html.find('div.profile_ban', first=True)

        if ban == None:
            return False
        else:
            return True

    def profile_last_vacban(self, has_vacban: bool, page_html):

        if has_vacban:
            days = page_html.html.find('div.profile_ban_status:last-child', first=True).text.strip()
            days = days.replace('Multiple VAC bans on record | Info', '')
            days = days.replace(' day(s) since last ban', '').strip()
            
            days = int(days)
            weeks = int(days / 7)
            months = int(days / 30)
            years = int(days / 365)

            days = {
                'days':days,
                'weeks':weeks,
                'months':months,
                'years':years
            }
        
            return days

        else:
            return None

    def games_get_list(self, profile_id: str):
        games = []
        total_hours_in_games = 0

        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}/games/?tab=all')
            r.html.render(sleep=1)

            games_list = r.html.find('div#games_list_rows div.gameListRow')

        
        for game in games_list:
            name = game.find('.gameListRowItemName', first=True).text.strip()
            hours = game.find('.hours_played', first=True).text.replace('hrs on record', '').replace(',', '').replace('.', '').strip()
            url = game.find('.gameListRowLogo a', first=True).attrs['href']
            app_id = url.replace('https://steamcommunity.com/app/', '').strip()

            if hours == '':
                hours = 0
            else:
                hours = int(hours)

            total_hours_in_games += hours

            stats = {
                'name':name,
                'url':url,
                'app_id':app_id,
                'hours_played':hours
            }

            games.append(stats)
        
        all_game_data = {
            'total_playtime':{
                'minutes':round(total_hours_in_games * 60, 2),
                'hours':round(total_hours_in_games, 2),
                'days':round(total_hours_in_games / 24, 2),
                'years':round(total_hours_in_games / 8760, 2)
            },
            'games':games
        }

        return all_game_data

    def friends_get_list(self, profile_id: str):
        friends = []
        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}/friends/')
            time.sleep(1)
            
            friends_list = r.html.find('div.persona')

            for friend in friends_list:
                try:
                    name = str(friend.attrs['data-search']).split(';')[0].strip()
                except KeyError:
                    continue


                steam_id = str(friend.attrs['data-steamid'])
                profile_url = str(friend.find('a', first=True).attrs['href'])

                mate = {
                    'steam_name':name,
                    'steam_id':steam_id,
                    'profile_url':profile_url
                }

                friends.append(mate)

        return friends

    def profile_get_awards(self, profile_id: str):
        awards_recieved: list
        awards_given: list

        awards_recieved_index: int
        awards_given_index: int
        awards_given_count: int
        awards_recieved_count: int

        awards_recieved = []
        awards_given = []
        awards_recieved_index = None
        awards_given_index = None

        awards_recieved_count = 0
        awards_given_count = 0

        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}/awards/')

            try:
                awards_list = r.html.find('.profile_awards_header_title')
            except:
                return None

            if len(awards_list) == 1:
                if str(awards_list[0].attrs['data-tooltip-text']).startswith("Number of awards this use has given"):
                    awards_given_index = 0
                else:
                    awards_recieved_index = 0
            else:
                awards_recieved_index = 0
                awards_given_index = 1

            real_awards_sec = r.html.find('.profile_awards_section')

            if awards_recieved_index != None:
                awards = r.html.find('.profile_awards_section')[awards_recieved_index].find('.profile_award')

                for award in awards:
                    name_full = str(award.find('.profile_award_name', first=True).text)
                    name = str(re.sub('\(x\d+\)', '', name_full)).strip()
                    count_full = re.findall('\(x\d+\)', name_full)[0]
                    count = int(count_full.replace('(x', '').replace(')', '').strip())

                    award_data = {
                        'name':name,
                        'count':count
                    }

                    awards_recieved_count += count
                    awards_recieved.append(award_data)

            if awards_given_index != None:
                awards = r.html.find('.profile_awards_section')[awards_given_index].find('.profile_award')
                for award in awards:
                    name_full = str(award.find('.profile_award_name', first=True).text)
                    name = re.sub('\(x\d+\)', '', name_full).strip()
                    count_full = re.findall('\(x\d+\)', name_full)[0]
                    count = int(count_full.replace('(x', '').replace(')', '').strip())

                    award_data = {
                        'name':name,
                        'count':count
                    }

                    awards_given_count += count
                    awards_given.append(award_data)


            all_award_data = {
                'general_info':{
                    'total_awards_recieved':awards_recieved_count,
                    'total_awards_given':awards_given_count
                },
                'recieved_awards':awards_recieved,
                'given_awards':awards_given,
            }

            return all_award_data

    def profile_get_badges(self, profile_id: str):
        badges = []
        total_exp = 0
        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}/badges/')

            badges_list = r.html.find('div.badge_info')

            for badge in badges_list:
                name, exp, date = list(badge.find('.badge_info_description', first=True).text.split('\n'))

                exp_only = re.findall('\d+\sXP', exp)[0]
                exp_int = int(exp_only.replace('XP', '').strip())

                total_exp += exp_int

                badge_data = {
                    'name':name.strip(),
                    'exp':exp_int,
                    'date_unlocked':date.strip()
                }

                badges.append(badge_data)

        all_badge_data = {
            'num_badges_unlocked':len(badges),
            'total_exp_from_badges':total_exp,
            'badges':badges
        }

        return all_badge_data

    def profile_get_groups(self, profile_id: str):
        groups = []
        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}/groups/')

            groups_list = r.html.find('.group_block_details')

            for group in groups_list:
                name = group.find('a.linkTitle', first=True).text.strip()
                group_link = group.find('a.linkTitle', first=True).attrs['href']
                try:
                    public = group.find('span.pubGroup', first=True).text.strip()
                except AttributeError:
                    public = ""
                members = group.find('.memberRow a')[0].text.replace('Members', '').replace(',', '').strip()

                if public == "- Public":
                    is_public = True
                else:
                    is_public = False

                group_data = {
                    'group_title':name,
                    'group_url':group_link,
                    'public':is_public,
                    'total_members':int(members)
                }
                
                groups.append(group_data)

        all_group_data = {
            'total_groups_joined':len(groups),
            'groups':groups
        }

        return all_group_data
    
    def games_get_achievements(self, profile_id: str, games_data: dict):
        achievements_all = []
        total_achievements_count = 0

        with HTMLSession() as s:
            for game in games_data['games']:
                app_id = game['app_id']
                game_name = game['name']

                this_game_achievements = []

                r = s.get(f'https://steamcommunity.com/id/{profile_id}/stats/{app_id}/?tab=achievements')

                if r.status_code == 302 or r.status_code == 303:
                    continue
                
                achievements = r.html.find('.achieveRow')

                print(f"Gathering achievements for {game_name}")
                
                for achievement in achievements:
                    try: 
                        achievement_date_unlocked = achievement.find('.achieveUnlockTime', first=True).text
                    except AttributeError:
                        continue

                    achievement_name = achievement.find('h3', first=True).text.strip()
                    achievement_description = achievement.find('h5', first=True).text.strip()

                    if achievement_name and achievement_description == "":
                        continue
                    
                    data_for_this_achievement = {
                        'name':achievement_name,
                        'description':achievement_description,
                        'date_unlocked':achievement_date_unlocked
                    }

                    this_game_achievements.append(data_for_this_achievement)

                #if len(this_game_achievements) == 0:
                #    continue

                all_achievement_data_for_this_game = {
                    'game_name':game_name,
                    'achievements_unlocked':len(this_game_achievements),
                    'achievements':this_game_achievements
                }

                achievements_all.append(all_achievement_data_for_this_game)
                total_achievements_count += len(this_game_achievements)
        
        full_achievement_data = {
            'total_achievements':total_achievements_count,
            'achievements':achievements_all
        }

        return full_achievement_data

def create_json_file_with_gathered_data(info: dict, games: dict, friends: list, awards: dict, badges: dict, groups: dict, achievements: dict, profile_id: str):
    big_data = {
        'general_info':info,
        'games':games,
        'friends':friends,
        'awards':awards,
        'badges':badges,
        'groups':groups,
        'achievements':achievements
    }

    data = json.dumps(big_data, indent=4)

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/{profile_id}.json", "w") as f:
        f.write(data)

def main(profile_id: str):
    spy: SteamSpy
    page_html: HTMLResponse
    vacban: bool

    friends: list

    awards: dict
    badges: dict
    games: dict
    groups: dict
    info: dict
    last_vacban: dict
    achivements: dict

    spy = SteamSpy()

    print("(1/10) Gathering data, this may take a moment...")
    page_html = spy.general_get_page_html(profile_id)

    print(f"(2/10) Gathering info about '{profile_id}'")
    info = spy.general_get_basic_info(page_html)

    print("(3/10) Getting VAC bans...")
    vacban = spy.profile_has_vacban(page_html)

    print("(4/10) Gathering users games...")
    games = spy.games_get_list(profile_id)

    print("(5/10) Gathering users friend data...")
    friends = spy.friends_get_list(profile_id)

    print("(6/10) Getting award data...")
    awards = spy.profile_get_awards(profile_id)

    print("(7/10) Getting badge data...")
    badges = spy.profile_get_badges(profile_id)

    print("Geting group data...")
    groups = spy.profile_get_groups(profile_id)

    print("(9/10) Gathering achievement data...\nThis can take upwards of 5 minutes, depending on how many achievements you have, so why not make a cuppa tea.")
    time.sleep(1)
    achievements = spy.games_get_achievements(profile_id, games)

    last_vacban = spy.profile_last_vacban(vacban, page_html)
    info.update({'has_vacban':vacban})
    info.update({'last_vacban':last_vacban})

    print("(10/10) creating JSON file...")
    create_json_file_with_gathered_data(info, games, friends, awards, badges, groups, achievements, profile_id)

    print("JSON file created!")
    print(f"Process is done, all data saved to '{profile_id}.json'")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        profile_id = sys.argv[1]
    else:
        profile_id = input("Enter a steam ID: ")

    main(profile_id)