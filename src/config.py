import pydantic


class Config(pydantic.BaseSettings):
    API_TOKEN: str = 'TOKEN'
