import datetime
import shutil

def create_db_backup() -> None:
    db_path = 'resources/'
    db_name = 'database.db'
    backups_path = 'backups/'
    
    today = datetime.datetime.today()
        
    shutil.copy2(db_path + db_name, f'{backups_path}{today.day}_{today.month}_{today.year}_backup.db')