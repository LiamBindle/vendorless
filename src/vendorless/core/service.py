from .dotdict import DotDict
from typing import Optional
from dataclasses import dataclass

class Service(DotDict):
    service_name: str


# services:
#   {{ variables.service_name }}:
#     image: postgres:17-alpine
#     restart: always
#     environment:
#       - POSTGRES_DB={{ variables.db_name }}
#       - POSTGRES_USER={{ variables.username }}
#       - POSTGRES_PASSWORD={{ variables.password }}
#       - PGDATA=/data/{{ variables.pgdata_path }}
#     ports:
#       - "5432:5432"
#     volumes:
#       - {{ variables.volume }}:/data


@dataclass
class PostgresDatabaseInputs:
    database_name: str
    service_name: str
    username: str
    password: str
    volume: str
    data_path: str


@dataclass
class PostgresDatabaseOutputs:
    service_name: str
    port: int
    database_name: str
    username: str
    password: str

