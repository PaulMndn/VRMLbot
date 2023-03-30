

BASE_URL = "https://vrmasterleague.com"

short_game_names = {
    "Archangel: Hellfire": "ArchangelHellfire",
    "Blaston": "Blaston",
    "Contractors": "Contractors",
    "Echo Arena": "EchoArena",
    "Final Assault": "FinalAssault",
    "Onward": "Onward",
    "Pavlov PC only": "PavlovPC",
    "Pavlov PS5/PC": "Pavlov",
    "Snapshot": "Snapshot",
    "Space Junkies": "SpaceJunkies",
    "Ultimechs": "Ultimechs"
}

def dc_escape(string: str):
    "Return the string with all Discord message formatting characters escaped."
    if string is None:
        string = ""
    return string.translate(str.maketrans({"*": "\*",
                                           "_": "\_",
                                           "`": "\`",
                                           "<": "\<",
                                           ">": "\>",
                                           "|": "\|",
                                           "~": "\~"}))
