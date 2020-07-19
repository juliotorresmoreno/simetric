from io import StringIO
import pandas as pd
import redis
import json
from simetric.settings import ETL_CHANNEL, DATABASES
from sqlalchemy import create_engine
from simetric.helpers.database import create_conn

channel = ETL_CHANNEL


def load_to_mysql(
    worker_name: str,
    redis_cli: redis.Redis,
    headers: dict,
    body: bytes
):
    if headers['type'] != 'load_data':
        return
    redis_cli.set(worker_name, 'inactive', ex=1)
    
    conn = create_conn()
    body_io = StringIO(body.decode('utf-8'))
    df: pd.DataFrame = pd.read_csv(body_io, sep=',')
    df.to_sql(headers['name'], con=conn, if_exists='append')
    redis_cli.set(worker_name, 'active', ex=60)


def pong(
    worker_name: str,
    redis_cli: redis.Redis,
    headers: dict,
    body: str
):
    if headers['type'] != 'ping':
        return
    redis_cli.publish(channel, json.dumps({
        "type": "pong",
        "worker_name": worker_name,
    }))
