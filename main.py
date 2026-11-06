from pathlib import Path
from dotenv import load_dotenv
from atlas.ui import AtlasApp

load_dotenv(Path(__file__).resolve().parent / '.env')

if __name__ == '__main__':
    AtlasApp(Path.cwd()).run()
