#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Isaac
Last Updated: 22 Apr 2018
Contact: Message @Isaac at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc
Short Description: 
This is a python library to provide some basic interactions with C1's terminal-api.
------------------------------------------------------------------------------------------------

Every function is self documented and I have provided an example script.
If you still have any questions or suggestions just let me know on the forums - @Isaac
'''

import multiprocessing as mp
import requests
import time
import json
import sys

api_link = 'http://terminal.c1games.com/api'

def clean_content(content):
    '''
    Formats string from an HTML webpage from requests api.

        Args:
            * content: A string from requests.get(URL).content

        Returns:
            A string that can be parsed using JSON
    '''
    return str(content)[2:-1].replace("\\'",'').replace('\\\\','\\').replace('\\"','')

def get_page(url):
    '''
    Get a web page using the requests library.

        Args:
            * url: A webpage url to get

        Returns:
            A requests response object
    '''
    return requests.get(url)

def get_page_content(path, url=api_link):
    '''
    Get the content from a webpage, for the terminal api this is a JSON string.

        Args:
            * path: A path relative to terminal's api link
            * url: The base url, default is terminal's api link

        Returns:
            A string that can be parsed using json.
    '''
    return clean_content(get_page(url+path).content)

def get_leaderboard_metrics():
    '''
    Get the leaderboard metrics that are shown on the terminal leaderboard page.

        Returns:
            A dictionary containing the current leaderboard metrics.
    '''
    contents = get_page_content('/game/leaderboard/metrics')
    return json.loads(contents)['data']

def get_leaderboard_metric(key, season='2'):
    '''
    Get a specific leaderboard metric from the terminal leaderboard page.

        Args:
            * key: The leaderboard metric you'd like to retrieve

        Returns:
            The number associated with the leaderboard metric.
    '''
    data = get_leaderboard_metrics()
    try: return data[season][key]
    except KeyError as e:
        raise Exception('No leaderboard metric with key: {}'.format(key))

def get_leaderboard_algos(i):
    '''
    Get the algos that are on the i_th page of the leaderboard.

        Args:
            * i: The leaderboard page to retrieve (starts at 1, not 0)

        Returns:
            A list of dictionaries, where each dictionary contains an algo and it's stats.
    '''
    if i < 1: raise KeyError('leaderboard page must be larger than 0, got {}'.format(i))
    contents = get_page_content('/game/leaderboard?page={}'.format(i))
    return json.loads(contents)['data']['algos']

def get_num_players(season='2'):
    '''
    Get the total number of terminal players.

        Args:
            * season: Currently can only be '1' or '2'

        Returns:
            The total number of terminal players.
    '''
    return get_leaderboard_metric('Players', season=season)

def get_num_matches(season='2'):
    '''
    Get the total number of terminal matches played for a season (default is current).

        Args:
            * season: Currently can only be '1' or '2'

        Returns:
            The total number of terminal matches played in a season.
    '''
    return get_leaderboard_metric('Matches', season=season)

def get_num_algos(season='2'):
    '''
    Get the total number of terminal algos uploaded.

        Args:
            * season: Currently can only be '1' or '2'

        Returns:
            The total number of terminal algos uploaded.
    '''
    return get_leaderboard_metric('Algos', season=season)

def get_algos_matches(ID):
    '''
    Get the last matches that an algo has played.

        Args:
            * ID: The id of the algo

        Returns:
            A list of dictionaries, where each dictionary contains a match and it's stats.
    '''
    try:
        contents = get_page_content('/game/algo/{}/matches'.format(ID))
        return json.loads(contents)['data']['matches']
    except json.decoder.JSONDecodeError: raise KeyError('"{}" is not a valid ID, must be an integer'.format(ID))

def search_for_id(algo_name, num_processes=20, verbose=False):
    '''
    Searches for an algo's id by checking it's name. It loops through every single id and it's matches until it finds the associated name.
    If you make a typo, it will take a very long time, be sure :).
    It searches (generally) based on the algo's last uploaded,
    so if you just uploaded the algo, you can make this like 5,
    but you'll want it to be larger if you uploaded the algo a long time ago.

        Args:
            * algo_name: The name of the algo to find
            * num_processes: The number of subprocesses to start, make this larger if your algo is really old
            * verbose: Whether or not to print as it searches

        Returns:
            An id associated with the algo_name you passed.
            If there are duplicate names then it returns the first that it finds.
            This will most likely be the most recent algo uploaded, but this IS NOT guaranteed.
    '''
    offset = 507
    num_algos = get_num_algos() + get_num_algos(season='1')
    start = num_algos + offset

    manager = mp.Manager()
    rtn_dict = manager.dict()
    next_id = manager.dict()
    next_id[0] = num_algos + offset
    ps = {}

    for i in range(num_processes+1, 0, -1):
        ps[i] = mp.Process(target=search_for_algo, args=(algo_name, next_id, rtn_dict, verbose))
        ps[i].start()

    while len(rtn_dict) == 0:
        time.sleep(.1)

    for p in ps.values():
        p.terminate()

    if verbose: print ('\n\nName: {}\t\tID: {}'.format(algo_name,rtn_dict.values()[0]))

    return rtn_dict.values()[0]

def search_for_algo(algo_name, next_id, rtn_dict, verbose):
    '''
    Helper function that is used by search_for_id, continually checks the next_algo for algo_name.

        Args:
            * algo_name: The name of the algo to find
            * next_id: The id of the algo it should check next
            * rtn_dict: A dictionary to store whether or not the name has been found, necessary for the mp module
            * verbose: Whether or not to print as it searches

        Returns:
            An id associated with the algo_name passed, -1 if not found.
    '''
    next_id[0] -= 1
    ID = check_id_for_algo(algo_name, next_id[0], rtn_dict, verbose)
    if ID != -1: return ID
    while ID == -1 :
        next_id[0] -= 1
        ID = check_id_for_algo(algo_name, next_id[0], rtn_dict, verbose)
        if ID != -1:
            return ID
    return -1

def check_id_for_algo(algo_name, ID, rtn_dict, verbose=False):
    '''
    Helper function that is used by search_for_algo, checks every match played by an algo to see if the algo_name is found.

        Args:
            * algo_name: The name of the algo to find
            * ID: The id of the algo to check the matches played
            * rtn_dict: A dictionary to store whether or not the name has been found, necessary for the mp module
            * verbose: Whether or not to print as it searches

        Returns:
            An id associated with the algo_name passed, -1 if not found.
    '''
    try:
        if verbose: print ('checking id {}\t\t\t\r'.format(ID), end='')

        for match in get_algos_matches(ID):
            w_algo = match['winning_algo']
            l_algo = match['losing_algo']

            w_name = w_algo['name']
            l_name = l_algo['name']
            w_id = w_algo['id']
            l_id = l_algo['id']

            if l_name.upper() == algo_name.upper():
                rtn_dict[0] = l_id
                return l_id
            if w_name.upper() == algo_name.upper():
                rtn_dict[0] = w_id
                return w_id
    except Exception as e:
        print (e)

    return -1

def search_leaderboard_for_id(algo_name, r=104, verbose=False):
    '''
    Searches for an algo's id by checking it's name. It loops through every leaderboard page and checks every algo until it finds the associated name.
    This serves the same function as search_for_id, but is much much faster if you know that the algo is currently listed on the leaderboard.

        Args:
            * algo_name: The name of the algo to find
            * r: The max number of pages to check (104 is the current max - will check every page)
            * verbose: Whether or not to print as it searches

        Returns:
            An id associated with the algo_name you passed.
            If there are duplicate names then it returns the first that it finds (highest elo).
    '''
    for i in range(1, r+1):
        try:
            if verbose: print ('checking leaderboard page {}\t\t\r'.format(i), end='')

            for algo in get_leaderboard_algos(i):
                name = algo['name']
                ID = algo['id']

                if name.upper() == algo_name.upper():
                    if verbose: print ('\n\nName: {}\t\tID: {}'.format(algo_name,ID))
                    return ID
        except Exception as e:
            if verbose: print ()
            print (e)
            break

    if verbose: print ()
    return -1

def get_leaderboard_ids(pages=[1], limit=(-sys.maxsize - 1)):
    '''
    Gets every single algo's id on leaderboard's pages.

        Args:
            * pages: A list of leaderboard pages to check (index number), or a single page to check
            * limit: You can specify an elo limit, where it will not return any algo's below that limit

        Returns:
            A dictionary where each key is an algo name and it's value is it's id.
    '''
    if type(pages) == int: pages = [pages]

    algos = {}
    for i in pages:
        try:
            for algo in get_leaderboard_algos(i):
                name = algo['name']
                ID = algo['id']
                elo = algo['rating']

                if elo < limit: break
                algos[name] = ID

        except Exception as e:
            print (e)
    return algos

def get_match_ids(algo, in_leaderboard=False, verbose=False):
    '''
    Gets the ids of the matches an algo has played.

        Args:
            * algo: The algo you want the matches from, it can be:
                - The algo's ID
                - The algo's name (you should then specify whether or not it is in the leaderboard to find it faster)
            * in_leaderboard: Whether or not the algo is on the leaderboard - used to make searching for an algo's id much faster
            * verbose: Whether or not to print as it searches

        Returns:
            A list of match ids associated with that algo.
    '''
    if type(algo) == str:
        if in_leaderboard:
            ID = search_leaderboard_for_id(algo, verbose=verbose)
        else:
            ID = search_for_id(algo, verbose=verbose)
    elif type(algo) == int:
        ID = algo

    if ID == -1: return []
    return [match['id'] for match in get_algos_matches(ID)]

def get_match_str(mID):
    '''
    Function to get a simple formatted string to watch a match.

        Args:
            * mID: The id number of the match

        Returns:
            A string you can copy and paste into a browser to watch that game.
    '''
    return 'http://terminal.c1games.com/watch/{}'.format(mID)

def get_matches_str(algo, in_leaderboard=False, verbose=False):
    '''
    Function to get all of an algo's matches in formatted strings.

        Args:
            * algo: The algo you want the matches from, it can be:
                - The algo's ID
                - The algo's name (you should then specify whether or not it is in the leaderboard to find it faster)
            * in_leaderboard: Whether or not the algo is on the leaderboard - used to make searching for an algo's id much faster
            * verbose: Whether or not to print as it searches

        Returns:
            A string you can copy and paste into a browser to watch that game.
    '''
    matchIDs = get_match_ids(algo, in_leaderboard=in_leaderboard, verbose=verbose)
    return [get_match_str(x) for x in matchIDs]

if __name__ == '__main__':
    pass
