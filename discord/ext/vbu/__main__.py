import argparse
import typing
import pathlib
import textwrap
import asyncio

from .runner import (
    run_bot,
    run_website,
    run_sharder,
    run_shell,
    run_modify_commands,
    run_interactions,
)


def get_path_relative_to_file(
        path: typing.Union[pathlib.Path, str]
        ) -> pathlib.Path:
    """
    Get the full path for a file relative to a given location.
    """

    here = pathlib.Path(__file__).parent.resolve()
    return here.joinpath(path)


def create_file(*path: str, content: typing.Optional[typing.Union[str, pathlib.Path]] = None):
    joined_folder_path = pathlib.Path("./").joinpath(*path[:-1])
    joined_file_path = pathlib.Path("./").joinpath(*path)
    if content:
        if isinstance(content, pathlib.Path):
            filename = content
            with open(filename) as a:
                content = a.read()
        joined_folder_path.mkdir(parents=True, exist_ok=True)
        try:
            with open(joined_file_path, "x") as a:
                a.write(content)
        except FileExistsError:
            print(f"File {joined_file_path} was not created as one already exists.")
    else:
        joined_file_path.mkdir(parents=True, exist_ok=True)


def get_default_program_arguments() -> argparse.ArgumentParser:
    """
    Set up the program arguments for the module. These include the following (all are proceeded by "python -m voxelbotutils"):
    "run bot config.toml --min 0 --max 10 --shardcount 10"
    "run bot config/config.toml"
    "run website config.toml"
    "run website config/config.toml"
    "create-config bot"
    "create-config website"

    Returns
    --------
    :class:`argparse.ArgumentParser`
        The arguments that were parsed
    """

    LOGLEVEL_CHOICES = ["debug", "info", "warning", "error", "critical"]

    # Set up our parsers and subparsers
    parser = argparse.ArgumentParser(prog="vbu")
    runner_subparser = parser.add_subparsers(dest="subcommand")
    runner_subparser.required = True
    bot_subparser = runner_subparser.add_parser("run-bot")
    website_subparser = runner_subparser.add_parser("run-website")
    interactions_subparser = runner_subparser.add_parser("run-interactions")
    sharder_subparser = runner_subparser.add_parser("run-sharder")
    shell_subparser = runner_subparser.add_parser("run-shell")
    application_subparser = runner_subparser.add_parser("commands")
    create_config_subparser = runner_subparser.add_parser("create-config")
    check_config_subparser = runner_subparser.add_parser("check-config")

    # Set up the bot arguments
    bot_subparser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run.")
    bot_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration for the bot.")
    bot_subparser.add_argument("--min", nargs="?", type=int, default=None, help="The minimum shard ID that this instance will run with (inclusive).")
    bot_subparser.add_argument("--max", nargs="?", type=int, default=None, help="The maximum shard ID that this instance will run with (inclusive).")
    bot_subparser.add_argument("--shardcount", nargs="?", type=int, default=1, help="The amount of shards that the bot should be using.")
    bot_subparser.add_argument("--loglevel", nargs="?", default="INFO", help="Global logging level - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)
    bot_subparser.add_argument("--no-startup", action="store_true", default=False, help="Whether or not to run the startup method.")

    # Set up the website arguments
    website_subparser.add_argument("website_directory", nargs="?", default=".", help="The directory containing a static and templates folder for the website to run.")
    website_subparser.add_argument("config_file", nargs="?", default="config/website.toml", help="The configuration for the website.")
    website_subparser.add_argument("--host", nargs="?", default="0.0.0.0", help="The host IP to run the website on.")
    website_subparser.add_argument("--port", nargs="?", type=int, default="8080", help="The port to run the website with.")
    website_subparser.add_argument("--debug", action="store_true", default=False, help="Whether or not to run the website in debug mode.")
    website_subparser.add_argument("--loglevel", nargs="?", default="INFO", help="Global logging level - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)

    # Set up the interactions server arguments
    interactions_subparser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run.")
    interactions_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration for the bot.")
    interactions_subparser.add_argument("--host", nargs="?", default="0.0.0.0", help="The host IP to run the website on.")
    interactions_subparser.add_argument("--port", nargs="?", type=int, default="8080", help="The port to run the website with.")
    interactions_subparser.add_argument("--path", nargs="?", type=str, default="/interactions", help="The path to run the interactions endpoint on.")
    interactions_subparser.add_argument("--connect", action="store_true", default=False, help="Whether you want your bot to connect to the Discord gateway.")
    interactions_subparser.add_argument("--debug", action="store_true", default=False, help="Whether or not to run the website in debug mode.")
    interactions_subparser.add_argument("--loglevel", nargs="?", default="INFO", help="Global logging level - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)

    # Set up the sharder arguments
    sharder_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration for the bot.")
    sharder_subparser.add_argument("--host", nargs="?", default="127.0.0.1", help="The host address to listen on.")
    sharder_subparser.add_argument("--port", nargs="?", default=8888, type=int, help="The host port to listen on.")
    sharder_subparser.add_argument("--concurrency", nargs="?", default=1, type=int, help="The max concurrency of the connecting bot.")
    sharder_subparser.add_argument("--loglevel", nargs="?", default="INFO", help="Global logging level - probably most useful is INFO and DEBUG.", choices=LOGLEVEL_CHOICES)

    # Set up the shell arguments
    shell_subparser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run.")
    shell_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration for the bot.")

    # Set up the shell arguments
    application_subparser.add_argument("action", help="The action yuou want to take on your application commands.", choices=["add", "remove"])
    application_subparser.add_argument("bot_directory", nargs="?", default=".", help="The directory containing a config and a cogs folder for the bot to run.")
    application_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration for the bot.")
    application_subparser.add_argument("--guild", nargs="?", default=None, type=int, help="The guild that you want to modify the application commands for.")

    # See what we want to make a config file for
    create_config_subparser.add_argument("config_type", nargs=1, help="The type of config file that we want to create.", choices=["bot", "website", "all"])
    check_config_subparser.add_argument("config_type", nargs=1, help="The type of config file that we want to create.", choices=["bot", "website"])
    check_config_subparser.add_argument("config_file", nargs="?", default="config/config.toml", help="The configuration file that you want to check.")

    # Wew that's a lot of things
    return parser


def check_config_value(
        base_config_key: typing.List[str], base_config_value: typing.Any,
        compare_config_value: typing.Any) -> None:
    """
    Recursively checks a config item to see if it's valid against a base config item
    """

    default_value = base_config_value if not isinstance(base_config_value, str) else textwrap.dedent(base_config_value).replace("\n", "\\n")

    # See if the item was omitted
    if isinstance(compare_config_value, type(None)):
        print(f"No value {base_config_key} was provided in your config file - should be type {type(base_config_value).__name__} (default {default_value!r}).")
        if isinstance(base_config_value, dict):
            for i, o in base_config_value.items():
                check_config_value(base_config_key + [i], o, None)
        return

    # See if the item was a str when it should be something else
    if not isinstance(base_config_value, type(compare_config_value)):
        print(f"Wrong value {base_config_key} type was provided in your config file - should be type {type(base_config_value).__name__} (default {default_value!r}).")
        if isinstance(base_config_value, dict):
            for i, o in base_config_value.items():
                check_config_value(base_config_key + [i], o, None)
        return

    # Correct value type - see if it was dict and recurse
    if isinstance(base_config_value, dict):
        for i, o in base_config_value.items():
            check_config_value(base_config_key + [i], o, compare_config_value.get(i))
    return


def get_next_version(current_version) -> str:
    """
    Get the next version that we can use in the requirements file.
    """

    release, major, minor = [int("".join(o for o in i if o.isdigit())) for i in current_version.split(".")]
    if release == 0:
        return f"0.{major + 1}.0"
    return f"{release + 1}.0.0"


def wrap_asyncio_run(func, *args, **kwargs):
    """
    A neat `asyncio.run(func(*args, **kwargs))` function that discards
    KeyboardInterrupt exceptions quietly.
    """

    try:
        asyncio.run(func(*args, **kwargs))
    except KeyboardInterrupt:
        pass


def main():
    """
    The main method for running all of vbu.
    """

    # Wew let's see if we want to run a bot
    parser = get_default_program_arguments()
    args = parser.parse_args()

    # Let's see if we copyin bois
    if args.subcommand == "create-config":
        config_type = args.config_type[0]
        if config_type in ["website", "all"]:
            create_file("config", "website.toml", content=get_path_relative_to_file("config/web_config_example_file.toml"))
            create_file("config", "website.example.toml", content=get_path_relative_to_file("config/web_config_example_file.toml"))
            create_file("config", "database.pgsql", content=get_path_relative_to_file("config/database_base_file.pgsql"))
            create_file("_run_website.sh", content="vbu run-website .\n")
            create_file(".gitignore", content="__pycache__/\n.venv/\nconfig/config.toml\nconfig/website.toml\n")
            create_file("requirements.txt", content=f"novus[vbu]\n")
            create_file("website", "frontend.py", content=get_path_relative_to_file("config/website_frontend_content.py"))
            create_file("website", "backend.py", content=get_path_relative_to_file("config/website_backend_content.py"))
            create_file("website", "static", ".gitkeep", content="\n")
            create_file("website", "templates", ".gitkeep", content="\n")
            create_file(".venv")
            print("Created website config file.")
        if config_type in ["bot", "all"]:
            create_file("config", "config.toml", content=get_path_relative_to_file("config/config_example_file.toml"))
            create_file("config", "config.example.toml", content=get_path_relative_to_file("config/config_example_file.toml"))
            create_file("config", "database.pgsql", content=get_path_relative_to_file("config/database_base_file.pgsql"))
            create_file("cogs", "ping_command.py", content=get_path_relative_to_file("config/cog_example_file.py"))
            create_file("_run_bot.sh", content="vbu run-bot .\n")
            create_file(".gitignore", content="__pycache__/\nconfig/config.toml\nconfig/website.toml\n")
            create_file("requirements.txt", content=f"novus[vbu]\n")
            create_file(".venv")
            print("Created bot config file.")
        exit(1)

    # See if we want to check the config file
    elif args.subcommand == "check-config":
        config_type = args.config_type[0]
        import toml
        if config_type == "website":
            with open(get_path_relative_to_file("config/web_config_example_file.toml")) as a:
                base_config_file_text = a.read()
        elif config_type == "bot":
            with open(get_path_relative_to_file("config/config_example_file.toml")) as a:
                base_config_file_text = a.read()
        else:
            exit(1)
        base_config_file = toml.loads(base_config_file_text)
        try:
            with open(args.config_file) as a:
                compare_config_file = toml.load(a)
        except Exception:
            print(f"Couldn't open config file {args.config_file}")
            exit(0)
        for key, value in base_config_file.items():
            check_config_value([key], value, compare_config_file.get(key))
        print("Completed config check.")
        exit(1)

    # Run things
    elif args.subcommand == "run-bot":
        wrap_asyncio_run(run_bot, args)
    elif args.subcommand == "run-interactions":
        wrap_asyncio_run(run_interactions, args)
    elif args.subcommand == "run-website":
        wrap_asyncio_run(run_website, args)
    elif args.subcommand == "run-sharder":
        wrap_asyncio_run(run_sharder, args)
    elif args.subcommand == "run-shell":
        wrap_asyncio_run(run_shell, args)
    elif args.subcommand == "commands":
        wrap_asyncio_run(run_modify_commands, args)


if __name__ == '__main__':
    main()
