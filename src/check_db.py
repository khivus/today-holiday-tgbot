# from datetime import datetime

# import pycron

# from src.models import User, Settings


# @pycron.cron("* * * * *")
# async def process_check_db(arg) -> None:
#     print('helo')
#     time_now = f'{datetime.now().hour}:{datetime.now().minute}'
#     print(time_now)
#     # users = await User.filter(time=time_now).all()
#     users = await User.all()
#     settings = await Settings.filter(time=time_now).all()  # TODO:
#     print(users)
#     print(settings)
