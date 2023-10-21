# The fetchers functions get nested data out of league_data

def get_leg(league_data):
    return league_data['settings']['leg']

def get_upper_and_lower_leg(league_data):
    """
    This function intends to return data on which legs we should iterate through to backfill data for
    a given season. For example, in a completed 17 week season, it should return
    an array of [lower, upper] - ex: [0, 17]
    """
    upper = 0
    # Note - this conditional is superflous (and bad) at the moment - it appears the
    # resulting 'leg' is the same whether the season is in_season or complete
    if league_data["status"] == "in_season":
        upper = league_data["settings"]["leg"] # This will be the current leg
    elif league_data["status"] == "complete":
        upper = league_data["settings"]["leg"] # This will be the last leg
    elif league_data["status"] == "post_season":
        upper = league_data["settings"]["leg"] # This will be the last leg
    else:
        print("Unknown definition of league_data['status']: {}".format(league_data["status"]))
        raise
    

    return [0, upper]

def get_playoff_week_start(league_data):
    return league_data["settings"]["playoff_week_start"]