
from simetric.settings import DATABASES
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

def create_conn() -> Engine:
    engine: Engine = create_engine('mysql://%s:%s@%s:%s/%s' % (
        DATABASES['default']['USER'],
        DATABASES['default']['PASSWORD'],
        DATABASES['default']['HOST'],
        DATABASES['default']['PORT'],
        DATABASES['default']['NAME'],
    ))

    return engine
