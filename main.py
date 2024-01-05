from dotenv import load_dotenv

from bot.bot import run


def main():
    load_dotenv()
    run()


if __name__ == "__main__":
    main()
