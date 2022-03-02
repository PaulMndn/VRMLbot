# VRMLbot

A bot that integrates [VRML](https://vrmasterleague.com/ "VR Master League") data into Discord.

As the used [API from VRML](https://api.vrmasterleague.com/ "VRML API") is currently in "Pre-pre alpha" you may encounter minor instabilities. However, this bot is in active developement and will be adjusted to any changes of the API.

### [Bot invite link](https://discord.com/api/oauth2/authorize?client_id=940586777469657138&permissions=532844903504&scope=applications.commands%20bot)

## Required files and folder

To run the bot several folders and files are required. In the projects root directory create folders `data/` and `log/`.

Furthermore, a `config.json` file is required in the root directory. It contains the following data:

```json
{
    "token": "your.bot.token",
    "dev": false,
    "debug_guilds": []
}
```

- `"token"` is your Discord bot's token and is used to log in. This is required.
- `"dev"` activates dev mode for the bot. This influences logging behabiour as well as using `debug_guilds`. Defaults to `false`.
- `"debug_guilds"` is a list of guild ids as integer. In dev mode commands will not be registered globally but only in the guilds specified here. Defaults to an empty list.

## Available commands

### `/about`

General Information about the bot including upcoming features and tips.

### `/set game`

Set a default game/league for this server. This is used as a fallback for various commands.

### `/game`

Get information about a game/leage in VRML

### `/player`

Search for an active player registered in VRML. This can be filtered for a specific game/league. If no game is given and no default game is set, all games/leagues are searched.

The result includes general player infomation and past teams of the current season.

### `/team`

Search for a team in a game/league. If no game and no default game is set, this results in an error.

The result includes general team information, rostered players, upcoming matches and past matches of the current season.

## Features in development

- A `/standings` command to get standings information for a game/league. This will inlude to see the standings around a specific rank and possibly team
- Role management to automatically assign team roles to the members of the server. This will require a pointer role under which the team roles will becreated and the `Manage Roles` permission for the bot and a specified default game for the server.
