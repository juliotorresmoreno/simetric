
from etl.pubsub import assign, Headers
from simetric.helpers.database import create_conn
from io import StringIO
import pandas as pd
import json

class Map:
  """
  Clase encargada de mapear la información para que pueda ser procesada por los trabajadores.
  """
  name: str = ''
  rest: str = ''
  columns: str = ''
  
  def __init__(self):
    self.name: str = ''
    self.rest: str = ''

  def apply(self, chunk: bytes, created: bool = False):
    """
    Permite procesar un bloque de mensajes

    chunk: bytes a procesar.
    created: define si se debe o no crear y/o remplazar la tabla en cuestion
    """

    chunks = self.rest + chunk.decode('utf-8')
    last = chunks.rfind('\n')
    content = chunks[:last]
    self.rest = chunks[last:].strip()
    if created == True:
      conn = create_conn()
      body_io = StringIO(content)
      df: pd.DataFrame = pd.read_csv(body_io, sep=',')
      df.to_sql(self.name, con=conn, if_exists='replace')
      self.columns = content.split('\n')[0]
    else:
      self.send_load_data(self.columns + '\n' + content)
  
  def end(self):
    """
    Debido a que el proceso deja un resto al final del archivo es necesario
    que el ultimo  bloque sea procesado de forma independiente.
    """
    self.send_load_data(self.rest)
    self.rest = ''

  def send_load_data(self, content: str):
    if content == '':
      return
    headers = Headers()
    headers.type = 'load_data'
    headers.name = self.name
    assign(headers, content)