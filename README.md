# Prueba Simetric

#### REQUERIMIENTOS:
Se necesita que el aspirante desarrolle una solución basada en Django Framework y Django Rest Framework que cubra las necesidades requeridas en el sistema descrito a continuación.

Tenemos la necesidad de poder subir archivos (.csv) al sistema de almacenamiento de amazon web services (AWS S3) y crear una tabla en una base de datos externa (diferente a la que usa el ORM de Django Framework) basada en el archivo, las columnas de esta tabla deben corresponder al del archivo, y cuyos tipos de datos pueden ser todos ​ varchar ​ o ​ text , ​ una vez subido, se debe leer el archivo implementando ejecución por hilos para almacenar su información en la tabla creada.

Se debe garantizar que los datos guardados en las tablas creadas deben poder ser consultados desde un endpoint, el cual, debe tener implementado paginación, búsqueda por filtros y ordenamiento por columna.
Se debe implementar pruebas unitarias al sistema.

Nota: Cada archivo corresponderá a una estructura o formato donde cada ‘columna’ está separada por coma (.csv), ej:
```csv
transaction_id,transaction_date,transaction_amount,client_id,client_name
52fba4fa-3a01-4961-a809-e343dd4f9597,2020-06-01,10000,1067,nombre cliente
```
### Como ejecutar el proyecto
1. El primer paso es copiar el archivo .env.example a .env.
2. Editar el archivo .env y rellenar los datos necesarios. A continuación un ejemplo de lo que debe tener este archivo:
```txt
ETL_S3_BUCKET=
ETL_REDIS_HOST=
ETL_REDIS_PORT=6379
ETL_REDIS_PASSWORD=
ETL_NUM_CPUS=1
ETL_WORKER_PERFIX=machine0
ETL_IS_MASTER=true

ETL_DB_ENGINE=django.db.backends.mysql
ETL_DB_NAME=
ETL_DB_USER=
ETL_DB_PASSWORD=
ETL_DB_HOST=
ETL_DB_PORT=3306

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
```
### Variables de entorno
**ETL_S3_BUCKET**=Corresponde a un nombre de bucket único creado en la cuenta de AWS que se usara para este proyecto. Las credenciales del usuario de AWS deben tener permisos de IAM al arn del bucket. Un ejemplo de arn seria arn:aws:s3:::{nombre_bucket}/{nombre_folder}
ETL_REDIS_HOST=Dirección IP del servidor de redis. En caso de hacer uso de canales seguros se deberá usar stunnel.
ETL_REDIS_PORT=Puerto del servidor de redis. En caso de hacer uso de canales seguros se deberá usar stunnel.
ETL_REDIS_PASSWORD=Contraseña en caso de que se haga uso de esta.
ETL_NUM_CPUS=Numero de trabajadores en ejecución por worker en activo en gunicorn. Se recomienda 1.
ETL_WORKER_PERFIX=Nombre de la maquina que ejecuta el servicio.
ETL_IS_MASTER=si su valor es true se ejecutara un hilo lanzando ping's por el canal en redis.

ETL_DB_ENGINE=Driver de la base de datos. Por defecto es django.db.backends.mysql. Si se quiere cambiar es necesario alterar el archivo requirements.txt
ETL_DB_NAME=Nombre de la base de datos en MySQL.
ETL_DB_USER=Nombre de usuario en la base de datos de MySQL.
ETL_DB_PASSWORD=Contraseña de usuario en la base de datos de MySQL.
ETL_DB_HOST=Nombre del host o la direccion ip de la base de datos de MySQL.
ETL_DB_PORT=Puerto de la base de datos de MySQL.

AWS_ACCESS_KEY_ID=Corresponde a las credenciales de AWS en IAM.
AWS_SECRET_ACCESS_KEY=Corresponde a las credenciales de AWS en IAM.
AWS_DEFAULT_REGION=zona geográfica de AWS donde se desea realizar las operaciones.

3. Ejecutar el comando:
```bash
docker build -t simetric .
```
4. Ejecutar el comando:
```bash
docker run --restart always \
  -ti -p 8000:8000 \
  --name simetric simetric
```
### Probar el proyecto
1. **Subir archivos**: Es necesario realizar una petición POST a la ruta /etl/, a continuación un ejemplo:
```http
POST http://host:8000/etl/ HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="text"

title
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="titanic.csv"
Content-Type: text/csv

< ./example/titanic.csv
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```
 - **Consultar el api**: A continuación la forma en que debe construirse la petición:
```http
GET http://host:8000/api/{nombre_tabla}/?limit=0,2&sex=male&Name=like:Braund&Ticket=like:A&Fare=gt:7&sort=name:desc,Sex:asc HTTP/1.1
```
Parámetros:
 - **nombre_tabla**: Es el nombre del origen de datos que se quiere consultar. Su nombre proviene del nombre del archivo subido por medio del método de upload, por ejemplo si se usa el archivo titanic adjunto en la carpeta de examples.
 - **limit**: Permite realizar la paginación. El valor antes de la coma corresponde al numero de registros que deben saltarse, mientras que el segundo corresponde al numero de registros que se quiere consultar.
 - **sort**: Permite realizar operaciones de ordenación. El formato puede ser:
```
sort={campo}
 ```
O bien
```
sort={campo}:asc
 ```
O bien
```
sort={campo}:desc
 ```
--**otros**: Corresponden a los nombres de las columnas de la tabla que se esta consultando. El formato puede ser:
```
{campo}={operador}:{valor}
```
Los operadores soportados son:
**eq**: Condición igual a el valor especificado.
**neq**: Condición diferente a el valor especificado.
**like**: Condición similar a el valor especificado.
**lt**: Condición menor a el valor especificado.
**gt**: Condición mayor a el valor especificado.
**lte**: Condición menor o igual al valor especificado.
**gte**: Condición mayor o igual al valor especificado.

## Justificación:
La tarea solicitada es un problema recurrente que tuvo en sus inicios como solución la programación paralela impulsada por el uso de hilos. Sin embargo, en esta ultima década dio origen a proyectos como Apache Hadoop y Apache Spark entre todo el ecosistema.

La solución planteada evita el uso de programación concurrente y en vez de ello recurre a hilos de ejecución paralela distribuida en múltiples instancias con una capacidad de procesamiento elastico.

Los mensajes enviados tienen una cabecera de 100 bytes en formato json, sin embargo, la data enviada se envía en formato CSV y la razón de esto es que json es el formato de intercambio de información mas ineficiente para el tratamiento de datos en especial cuando son muchos los datos.

El  servidor wsgi elegido ha sido gunicorn puesto permite que los trabajadores vivan en memoria.

**Limitaciones**: Se ha usado Redis para asignar las tareas, sin embargo, esto no permite conocer en tiempo real el estado de los trabajadores por lo cual puede darse el caso de que se le asigne una tarea a un proceso ocupado. Para mitigar esto cada asignación tiene un tamaño máximo de bytes permitiendo que cada trabajador pueda completar la tarea anterior en el menor tiempo posible. Si un  trabajador recibe una tarea estando ocupado por la naturaleza bloqueante de los procesos esta quedara en la cola de mensajes hasta que se libere y pueda ser procesado.

