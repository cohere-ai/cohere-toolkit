from dotenv import find_dotenv, load_dotenv, set_key


def update_env_file(env_vars: dict[str, str]):
    dotenv_path = find_dotenv()

    if dotenv_path == "":
        dotenv_path = ".env"
        open(dotenv_path, "a").close()

    for key in env_vars:
        set_key(dotenv_path, key, env_vars[key])

    load_dotenv(dotenv_path)
