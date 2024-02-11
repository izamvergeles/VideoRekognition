import credentials
import conection
import detectFace
import imageio
import time
import sys
import numpy as np
from datetime import datetime

# Se define la fecha actual en segundos para guardar el video de forma única y facil de identificar
current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
url_VID = credentials.video_URL
url_compresedVID = credentials.video_folder + current_date + ".mp4"
video_name = "uploadVideo/" + current_date + ".mp4"

# Se obtienen los objetos s3 y rekognition
rekognition, s3 = conection.login(credentials.aws_access_key_id, credentials.aws_secret_access_key, credentials.aws_session_token)

# Se crea una coleccion para almacenar las caras en esta y posteriormete comprobar si las caras detectadas
# ya se habian detectado antes
detectFace.MakeCollection(rekognition)

# Para poder aumentar la eficiencia del proceso cada video se comprime antes de ser subido al bucket
def compress_video_imageio(input_path, output_path, bitrate='1000k'):
    reader = imageio.get_reader(input_path)
    fps = reader.get_meta_data()['fps']
    writer = imageio.get_writer(output_path, fps=fps, bitrate=bitrate)

    # Debido a una advertencia de debe ajustar las dimensiones de los frames para
    # poder ser divisible entre 16
    original_resolution = np.array(reader.get_meta_data()['size'])
    adjusted_resolution = (original_resolution // 16) * 16

    # Leer cada fotograma del video y escribirlo en el nuevo video
    for frame in reader:
        frame = frame[:adjusted_resolution[1], :adjusted_resolution[0], :]
        writer.append_data(frame)

    # Cerrar el escritor
    writer.close()

try:
    print("Comprimiendo vídeo...")
    compress_video_imageio(url_VID, url_compresedVID)
except Exception as e:
    print(f"Error durante la compresión del video: {str(e)}")


# Lee el contenido del video comprimido para subirlo al bucket
with open(url_compresedVID, 'rb') as data:
    print("Subiendo vídeo...")
    s3.upload_fileobj(data, credentials.bucket_name, video_name)
    
    
# Se envia la petición a AWS que comience a procesar el video subido al bucket obteniendo el id del trabajo
jobID = detectFace.StartFaceDetection(credentials.bucket_name, video_name, rekognition)
    
response = rekognition.get_person_tracking(JobId=jobID)

print("Procesando vídeo...")
carga = " "
# Para detectar cuando ha terminado el procesado del video se genera un bucle hasta obtener el
# JobStatus SUCCEEDED. Para evitar sobrecarga por cada comprobación se espera 1 segundo
while response['JobStatus'] != 'SUCCEEDED':
    if response['JobStatus'] == 'IN_PROGRESS':
        carga = (carga + ".") if len(carga) < 3 else "."  # Reiniciar la carga después de 3 puntos
        sys.stdout.write(f'\033[1m\rProcesando{carga}\033[0m')
        sys.stdout.flush()
        time.sleep(1)
        response = rekognition.get_person_tracking(JobId=jobID)
    else:
        print("\033[91mSe ha detectado un error al procesar el vídeo.\033[0m")
        break

# Una vez con la respuesta se busca a personas mirando a camara
detectFace.ProcessResponse(response, s3, url_compresedVID, rekognition)
