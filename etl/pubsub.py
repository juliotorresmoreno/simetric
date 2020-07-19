import redis
import threading
from simetric.settings import \
    REDIS_HOST, REDIS_PORT, \
    REDIS_PASSWORD, REDIS_URL, \
    WORKER_PERFIX, ETL_CHANNEL, \
    IS_MASTER
from simetric.settings import NUM_CPUS
from etl.middlewares import load_to_mysql, pong
import json
import time
from random import randint
import os

channel = ETL_CHANNEL


def worker(num_worker: int):
    def subscribe():
        redis_cli = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
        )

        pubsub = redis_cli.pubsub()

        pubsub.subscribe(channel)
        worker_name = WORKER_PERFIX + '_' + str(num_worker) + ':' + str(randint(10000,99999))
        print('worker %s subscribe to %s' % (worker_name, channel))
        message: dict
        for message in pubsub.listen():
            if message['type'] == 'message':                
                headers = json.loads(message['data'][:100])
                body = message['data'][100:]
                if 'worker_name' in headers and headers['worker_name'] != worker_name:
                    continue
                # All operations
                load_to_mysql(worker_name, redis_cli, headers, body)
                pong(worker_name, redis_cli, headers, body)

    return subscribe


def worker_admin():
    redis_cli = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
    )
    pubsub = redis_cli.pubsub()
    pubsub.subscribe(channel)

    time.sleep(10)

    while(True):
        redis_cli.publish(channel, json.dumps({
            "type": "ping"
        }))
        time.sleep(60)


def worker_admin_status():
    redis_cli = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
    )
    pubsub = redis_cli.pubsub()
    pubsub.subscribe(channel)

    for message in pubsub.listen():
        if message['type'] == 'message':
            headers = json.loads(message['data'][:100])
            if headers['type'] == 'pong':
                redis_cli.set(headers['worker_name'], 'active', ex=60)


class Headers:
    type: str
    name: str
    columns: list

    def __init__(self):
        return


def assign(headers: Headers, content: str):
    """
    Se encarga de asignar las tareas a cada poceso

    headers: contiene información del tipo de mensaje.
    content: es la data a procesar
    """
    redis_cli = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
    )
    slaves = redis_cli.keys()
    while len(slaves) == 0:
        time.sleep(10)
        slaves = redis_cli.keys()
    worker_name: bytes = slaves[randint(0, len(slaves)-1)]
    message = json.dumps({
        'type': headers.type,
        'name': headers.name,
        'worker_name': worker_name.decode('utf-8')
    })
    message = message + (100 - len(message)) * ' '
    message = message + content
    redis_cli.publish(channel, message)
    redis_cli.close()


if not 'LOADED' in os.environ:
    threads = list()
    for i in range(NUM_CPUS):
        t = threading.Thread(target=worker(i))
        threads.append(t)
        t.start()

    def ping_pong():
        t = threading.Thread(target=worker_admin)
        threads.append(t)
        t.start()

        t = threading.Thread(target=worker_admin_status)
        threads.append(t)
        t.start()


    if IS_MASTER == 'true':
        ping_pong()

os.environ['LOADED'] = 'true'