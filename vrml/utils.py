

BASE_URL = "https://vrmasterleague.com"

short_game_names = {
    "Echo Arena": "EchoArena",
    "Onward": "Onward",
    "Pavlov": "Pavlov",
    "Snapshot": "Snapshot",
    "Contractors": "Contractors",
    "Final Assault": "FinalAssault"
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
