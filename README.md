# Video Rekognition
Proyecto basado en AWS rekognition para la detección de personas mirando a cámara en un vídeo.

Se divide en 4 ficheros:
- **[conection.py](./conection.py)**
- **[credentials.py](./credentials.py)**
- **[detectFace.py](./detectFace.py)**
- **[index.py](./index.py)**

## conection.py
Fichero encargado de procesar la conexión con AWS.
Desde index.py se llama a login usando las credenciales y este devuelve los objetos de la conexión rekognition y s3.

## credentials.py
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

## detectFace.py
Contiene todas las funciones de forma independiente para el procesado del video una vez se obtenga la respuesta.
Esta funciones se dividen en 2 bloques principales:
- Trabajo con los datos del video procesado
- Uso de procesoso de AWS para identificación de personas, mover archivo de ruta en el bucket, crear colecciones, comenzar con el proceso del vídeo...

## index.py
Fichero principal del programa encargado de llamar y estructurar cada instrucción.
Encargado de comprimir el vídeo y esperar al procesado del vídeo.

## Descripción extendida
Este proyecto comienza con el analisis de imágenes que ofrece AWS con detectFaces, tras observar y estudiar detenidamente que parámetros y datos ofrecía se llego a la solución de crear una herramienta que permita detectar cuando una persona se encuentra mirando a cámara, siendo este gesto un claro indicio para sospechar del mismo. Una vez con la idea, el proyecto tenía por donde empezar, grabar o encontrar un videos para obtener información. Tras una busqueda en internet se llego a la conclusión de que era mejor grabar diferentes videos y procesarlos usando video Rekognition de AWS. Una vez con esos datos se detecta que en video no se aporta informaciónd de los ojos de las personas detectadas por lo que todo el proyecto no servía para nada. También habia un gran problema con el tiempo de cada detección puesto que se hacia cada muchos segundos perdiendo muchos frames importante.

Investigando en AWS y sus herramientas para procesar videos se descubrió Person Traking, funcionaba prácticamente igual, pero daba mucha mas información por vídeo puesto que analizaba mas frames. Con esta herramienta y un estudio del JSON proporciando se taodavía habia futuro, se podía detectar usando la posición de la cara, no siendo igual de fiable pero dentro de unos margenes es aceptable. Con las variables importantes y las herramientas importantes se trabaja para obtener la mayor precisión posible. 

Todo este trabajo ha sido acompañado de otras funciones como la compresión del video para disminuir el tiempo de subida y preocesado, almacenamiento de detecciones y comparación de cara detectadas para definir reincidentes en un mismo vídeo. La idea principal era crear una base de datos personalizada y local pero el bucket de Amazon es necesario para el procesado de vídeo por lo que no tenía mucho sentido almacenar en diferentes luegares los mismos elementos.

