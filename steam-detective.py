import sys, json, os, time, re, menus
from requests_html import HTMLSession, HTMLResponse

profile_id: str

class SteamSpy:
    def __init__(self):
        pass

    def general_get_page_html(self, profile_id: str, using_custom_id: bool):
        ''' Get profile page HTML, so we don't have to keep sending out requests to the server. '''
        with HTMLSession() as s:
            if using_custom_id:
                return s.get(f'https://steamcommunity.com/id/{profile_id}')
            else:
                return s.get(f'https://steamcommunity.com/profiles/{profile_id}')

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
            'name':real_name,
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
        ''' Checks the Steam profile to see if they have a ban on their account. '''
        ban = page_html.html.find('div.profile_ban', first=True)

        if ban == None:
            return False
        else:
            return True

    def profile_last_vacban(self, has_vacban: bool, page_html):
        ''' If the account has a ban on their account, returns how long it has been since last ban. '''
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

    def games_get_list(self, profile_id: str, using_custom_id: bool):
        ''' Get a full list of the games on the users profile, if they allow you to see them. '''
        games: list = []
        total_hours_in_games: int = 0

        with HTMLSession() as s:
            if using_custom_id:
                r = s.get(f'https://steamcommunity.com/id/{profile_id}/games/?tab=all')
            else:
                r = s.get(f'https://steamcommunity.com/profiles/{profile_id}/games/?tab=all')
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

    def friends_get_list(self, profile_id: str, using_custom_id: bool):
        ''' Get a full list of the users friends, if that information is publicly available'''
        friends: list = []

        with HTMLSession() as s:
            if using_custom_id:
                r = s.get(f'https://steamcommunity.com/id/{profile_id}/friends/')
            else:
                r = s.get(f'https://steamcommunity.com/profiles/{profile_id}/friends/')
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

    def profile_get_awards(self, profile_id: str, using_custom_id: bool):
        ''' Get all awards, both gifted and recieved, from the users profile. '''
        awards_recieved: list = []
        awards_given: list = []

        awards_recieved_index: int
        awards_given_index: int
        awards_given_count: int
        awards_recieved_count: int

        awards_recieved_index = None
        awards_given_index = None

        awards_recieved_count = 0
        awards_given_count = 0

        with HTMLSession() as s:
            if using_custom_id:
                r = s.get(f'https://steamcommunity.com/id/{profile_id}/awards/')
            else:
                r = s.get(f'https://steamcommunity.com/profiles/{profile_id}/awards/')

            try:
                awards_list = r.html.find('.profile_awards_header_title')
            except:
                return None

            if len(awards_list) == 1:
                if str(awards_list[0].attrs['data-tooltip-text']).startswith("Number of awards this user has given"):
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

    def profile_get_badges(self, profile_id: str, using_custom_id: bool):
        ''' Get all badges from the users profile, provided that information is publicly available. '''
        badges: list = []
        total_exp: int = 0

        with HTMLSession() as s:
            if using_custom_id:
                r = s.get(f'https://steamcommunity.com/id/{profile_id}/badges/')
            else:
                r = s.get(f'https://steamcommunity.com/profiles/{profile_id}/badges/')

            badges_list = r.html.find('div.badge_info')

            for badge in badges_list:
                badge_name, badge_exp, badge_unlock_date = list(badge.find('.badge_info_description', first=True).text.split('\n'))

                exp_only = re.findall('\d+\sXP', badge_exp)[0]
                exp_int = int(exp_only.replace('XP', '').strip())

                total_exp += exp_int

                badge_data = {
                    'name':badge_name.strip(),
                    'exp':exp_int,
                    'date_unlocked':badge_unlock_date.strip()
                }

                badges.append(badge_data)

        all_badge_data = {
            'num_badges_unlocked':len(badges),
            'total_exp_from_badges':total_exp,
            'badges':badges
        }

        return all_badge_data

    def profile_get_groups(self, profile_id: str, using_custom_id: bool):
        ''' Get all the groups a user has joined, provided that information is public. '''
        groups: list = []

        with HTMLSession() as s:
            r = s.get(f'https://steamcommunity.com/id/{profile_id}/groups/')

            groups_list = r.html.find('.group_block_details')

            for group in groups_list:
                group_name = group.find('a.linkTitle', first=True).text.strip()
                group_link = group.find('a.linkTitle', first=True).attrs['href']

                try:
                    public = group.find('span.pubGroup', first=True).text.strip()
                    public = True
                except AttributeError:
                    public = False

                members = group.find('.memberRow a')[0].text.replace('Members', '').replace(',', '').strip()

                group_data = {
                    'group_title':group_name,
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
    
    def games_get_achievements(self, profile_id: str, games_data: dict, using_custom_id: bool, keep_empy_data=False):
        ''' Get all achievements from users played games. 
        
            keep_empty_data: if set to True it will output everything, even games without any achievement data (Default: False)
        '''
        achievements_all: list = []
        total_achievements_count: int = 0

        with HTMLSession() as s:
            for game in games_data['games']:
                app_id = game['app_id']
                game_name = game['name']

                this_game_achievements = []

                if using_custom_id:
                    r = s.get(f'https://steamcommunity.com/id/{profile_id}/stats/{app_id}/?tab=achievements', allow_redirects=False)
                else:
                    r = s.get(f'https://steamcommunity.com/profiles/{profile_id}/stats/{app_id}/?tab=achievements')

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
                    
                    data_for_this_achievement = {
                        'name':achievement_name,
                        'description':achievement_description,
                        'date_unlocked':achievement_date_unlocked
                    }

                    this_game_achievements.append(data_for_this_achievement)


                all_achievement_data_for_this_game = {
                    'game_name':game_name,
                    'achievements_unlocked':len(this_game_achievements),
                    'achievements':this_game_achievements
                }

                if not keep_empy_data and len(this_game_achievements) == 0:
                    continue

                achievements_all.append(all_achievement_data_for_this_game)
                total_achievements_count += len(this_game_achievements)
        
        full_achievement_data = {
            'total_achievements':total_achievements_count,
            'achievements':achievements_all
        }

        return full_achievement_data

def create_json_file_with_gathered_data(general_info_data: dict, game_data: dict, friend_data: list, award_data: dict, badge_data: dict, group_data: dict, achievement_data: dict, profile_id: str):
    ''' Creates a .JSON file in the same directory as the script, with the profile_id as the name. '''
    all_data = {
        'general_info':general_info_data,
        'games':game_data,
        'achievements':achievement_data,
        'awards':award_data,
        'friends':friend_data,
        'badges':badge_data,
        'groups':group_data,
    }

    data = json.dumps(all_data, indent=4)

    with open(f"{os.path.dirname(os.path.realpath(__file__))}/{profile_id}.json", "w") as f:
        f.write(data)

def main(profile_id: str, using_custom_id: bool):

    vacban: bool = False
    spy = SteamSpy()

    page_html = spy.general_get_page_html(profile_id, using_custom_id)

    print(f"(1/9) Gathering info about '{profile_id}'")
    general_info_data = spy.general_get_basic_info(page_html)

    print("(2/9) Getting VAC bans...")
    has_vacban = spy.profile_has_vacban(page_html)

    print("(3/9) Gathering users games...")
    game_data = spy.games_get_list(profile_id, using_custom_id)

    print("(4/9) Gathering users friend data...")
    friend_data = spy.friends_get_list(profile_id, using_custom_id)

    print("(5/9) Getting award data...")
    award_data = spy.profile_get_awards(profile_id, using_custom_id)

    print("(6/9) Getting badge data...")
    badge_data = spy.profile_get_badges(profile_id, using_custom_id)

    print("(7/9) Geting group data...")
    group_data = spy.profile_get_groups(profile_id, using_custom_id)

    print("(8/9) Gathering achievement data...\nThis can take upwards of 5 minutes, depending on how many achievements you have, so why not make a cuppa tea.")
    achievement_data = spy.games_get_achievements(profile_id, game_data, using_custom_id)

    last_vacban = spy.profile_last_vacban(vacban, page_html)
    general_info_data.update({'has_vacban':vacban})
    general_info_data.update({'last_vacban':last_vacban})

    print("(9/9) creating JSON file...")
    create_json_file_with_gathered_data(general_info_data, game_data, friend_data, award_data, badge_data, group_data, achievement_data, profile_id)

    
    print("JSON file created!")
    print(f"Process is done, all data saved to '{profile_id}.json'")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if sys.argv[1] == "--nocustom" and sys.argv[2] != "":
            main(sys.argv[2], False)
    elif len(sys.argv) == 2:
            main(sys.argv[1], True)
    else:
        profile_id, using_custom_id = menus.init_menu_main()
        main(profile_id, using_custom_id)