import shutil
import datetime

from src.constants import tzinfo

def create_db_backup() -> None:
    db_path = 'resources/'
    db_name = 'database.db'
    backups_path = 'backups/'
    
    tnow = datetime.datetime.now(tz=tzinfo)
    
    shutil.copy2(db_path + db_name, f'{backups_path}backup_{tnow.day:02}_{tnow.month:02}_{tnow.year}.db')