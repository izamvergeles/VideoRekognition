# VideoRekognition
Proyecto basado en AWS rekognition para la detección de personas mirando a cámara en un vídeo.

Se divide en 4 ficheros:
- **conection.py**
- **credentials.py**
- **detectFace.py**
- **index.py**

# conection.py
Fichero encargado de procesar la conexión con AWS.
Desde index.py se llama a login usando las credenciales y este devuelve los objetos de la conexión rekognition y s3.

# credentials.py
Almacena todos las credenciales de conexión con AWS.

aws_access_key_id = '' <br>
aws_secret_access_key = ''<br>
aws_session_token = ''<br>
region_name = ''<br>
bucket_name = ''<br>
video_folder = './data/'<br>
video_URL = './data/vid1.mp4'<br>
collection_id = ''<br>

**video_folder** define la ruta donde se almacena el video comprimido de forma temporal.<br>
**video_URL** se encarga de definir la ruta en la que se encuentra el video a procesar.

# detectFace.py
Contiene todas las funciones de forma independiente para el procesado del video una vez se obtenga la respuesta.
Esta funciones se dividen en 2 bloques principales:
- Trabajo con los datos del video procesado
- Uso de procesoso de AWS para identificación de personas, mover archivo de ruta en el bucket, crear colecciones, comenzar con el proceso del vídeo...

# index.py
Fichero principal del programa encargado de llamar y estructurar cada instrucción.
Encargado de comprimir el vídeo y esperar al procesado del vídeo.

