from dotenv import load_dotenv

if not load_dotenv():
    print('can\'t find .env file')
    exit(1)