# steam-detective
A Python script that allows you to get information on a profile, saved in JSON format.

# What it does
It started with me wanting to create a script that would get all of my game titles and time played from Steam to put in a database, I then realised there was no real way to do this; so I created this script to do it for me. As you can see the script has evolved past that now, so what happened? Honestly, I just got into it and wanted to keep going.

Now we have the script that is here on GitHub.

<h3>Okay so what does it actually do?</h3>
The script allows you to give a Steam ID for any profile, it then scrapes public information and dumps all of that stuff as a JSON file for easy parsing.

It gathers:

1. General information, sort of an overview of the profile.
2. A list of every game, their title and the hours they have played for.
3. The total ammount of time they have spent playing games on Steam. With your choice of minutes, hours, days or years.
4. The users friends, their Steam IDs, Profile URLs and current Steam name.
5. A list of their awards, the ones they have given and recieved.
6. All badges the user has collected, plus the total amount of experience gained from the badges.
7. Every group they are a member of, the groups total member count, link to the group, the name of the group and if it is public.
8. Shows if the user has a VAC or game ban on their account, and if they do how long it has been. With your choice of minutes, hours, days or years.

Now it must be said that this isn't a magical tool. If the user has chosen not to show any of this information, the JSON file will be mostly empty.

# How to use it
Using the script is incredibly easy, but before you use it you need to do:

`pip install requests_html`

which is the scraping module I am using for the script. Once that is done you can do:

`python steam-detective.py [profiles_custom_steam_id]`

For example `python steam-detective.py eroticgaben` would show information about Gabe Newell's Steam Account.

to run the script using a Custom Steam ID (aka one a user has set themselves.) or you can use the '--nocustom' flag to use a normal Steam ID.

`python steam-detective.py [profiles_steam_id]`

For example `python steam-detective.py 76561198085278322` would also show information about Gabe Newell's Steam Account.

alternatively you can run the script like:

`python steam-detective.py`

without passing in a ID, the script will take you through some menus to get input the right ID for your situation.

# Forking
If you want to fork my project, please go ahead. If you feel like you can add stuff, or even build on top of this to make something cool; please feel free to. You do not have to credit me, but can if you want to.
