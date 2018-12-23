#!/usr/bin/env python

'''
------------------------------------------------------------------------------------------------
Author: @Isaac
Last Updated: 23 Dec 2018
Contact: Message @Isaac at https://forum.c1games.com/
Copyright: CC0 - completely open to edit, share, etc
Short Description: 
This is an example script to show some of the svr_lib.py functions.
------------------------------------------------------------------------------------------------

Just change algo_name to be a valid algo name and you can uncomment the functions you'd like to see.
'''

import svr_lib as svr

'''
You must put all of the code regarding the svr_lib module inside of "if __name__ == '__main__':"
since it uses the multiprocessing library.
'''
if __name__ == '__main__':

    # change this name to be whatever algo you want
    algo_name = 'dumb-dumb-octo_v0.17'

    '''
        These are functions that are associated with the leaderboard metrics.
    '''
    # print (svr.get_leaderboard_metrics())
    # print (svr.get_num_players())
    # print (svr.get_num_matches())
    # print (svr.get_num_algos())

    '''
        These are functions associated with getting algos from the leaderboard.
    '''
    # print (svr.get_leaderboard_algos(3))
    # print (svr.get_leaderboard_ids(pages=[1,2,3], limit=1900))
    # print (svr.get_leaderboard_ids(pages=1))

    '''
        These are functions associated with getting algo's ids.
        You can either do this by searching through the leaderboard or all algos.
        Searching through the leaderboard is much much faster so if you know it exists, you should enable it.
        (verbose is just so you can see the functions run)
    '''
    # print (svr.search_for_id(algo_name, verbose=True))                    # this is if the algo is NOT on the leaderboard
    # print (svr.search_leaderboard_for_id(algo_name, verbose=True))        # this is if the algo IS on the leaderboard

    '''
        These are functions associated with getting an algo's match ids.
        If the algo is not on the leaderboard, set that param to False (default is False).
        (verbose is just so you can see the functions run)
    '''
    # print (svr.get_algos_matches(3000))
    # print (svr.get_match_ids(algo_name, in_leaderboard=True))

    '''
        These are some basic string formatting functions to make it so you can copy and paste into a browser url.
    '''
    # print (svr.get_match_str(1656045))
    # print (svr.get_matches_str(algo_name, in_leaderboard=True, verbose=False))        # algo_name could also just be an algo's id, if you know it
