
import credentials
from datetime import datetime
import cv2
import os
import io
# Codigo obtenido en tutorial de AWS
# Comienza el procesado del video
def StartFaceDetection(bucket, video_name, rekognition):
    response = rekognition.start_person_tracking(
        Video={
        'S3Object': 
            {
            'Bucket': bucket, 
            'Name': video_name
            }
        })
    return response['JobId']

# Código propio
def ProcessResponse(response, s3, urlCompresedVID, rekognition):
    for person in response['Persons']:
        if 'Face' in person['Person']:
            # Obtener el ángulo de 'Yaw' y 'Pitch' desde 'Pose'
            yaw_angle = person['Person']['Face']['Pose']['Yaw']
            pitch_angle = person['Person']['Face']['Pose']['Pitch']

            # Definir un umbral para determinar si la persona está mirando directamente a la cámara
            yaw_threshold = 26
            pitch_threshold = 26
            # Como las personas no suele mirar las cosas de forma diagonal se tiene en cuenta
            # si la persona esta mirando hacia un lado de forma horizontal o vertical
            if(abs(yaw_angle) < 10 and abs(pitch_angle) > 26):
                pitch_threshold = 35
            if abs(pitch_angle) < 10 and abs(yaw_angle) > 26:
                yaw_threshold = 35           
            # Pasando a absolutos los rangos se define si está mirando o no a la cámara
            is_looking_at_camera = abs(yaw_angle) < yaw_threshold and abs(pitch_angle) < pitch_threshold
            
            if is_looking_at_camera:
                frame = person['Timestamp']
                # Puede que haya mas de una persona mirando a camara en un video por lo que se debe guardar el indice               
                index_person = person['Person']['Index']
                
                # Si no se detecta el cuerpo de la persona solo se obtiene la cabeza en vez de el cuerpo entero
                if 'BoundingBox' in person['Person']:
                    face_box = person['Person']['BoundingBox']
                elif 'Face' in person['Person'] and 'BoundingBox' in person['Person']['Face']:
                    face_box = person['Person']['Face']['BoundingBox']
                else:
                    face_box = None
                
                # Busca en el video el frame para recortar a la persona
                cap = cv2.VideoCapture(urlCompresedVID)
                cap.set(cv2.CAP_PROP_POS_MSEC, frame)
                ret, frame = cap.read()
                # Verificar si se leyó correctamente y procesar el fotograma si es necesario
                if ret:
                    # Dibujar un rectángulo alrededor del cuadro de la cara
                    start_point = (int(face_box['Left'] * frame.shape[1]), int(face_box['Top'] * frame.shape[0]))
                    end_point = (int((face_box['Left'] + face_box['Width']) * frame.shape[1]),
                                int((face_box['Top'] + face_box['Height']) * frame.shape[0]))
                    color = (0, 0, 255)  # Color en formato BGR
                    thickness = 2
                    frame_with_rectangle = cv2.rectangle(frame, start_point, end_point, color, thickness)

                    # Guardar la imagen dentro del rectángulo
                    face_image = frame[int(face_box['Top'] * frame.shape[0]):int((face_box['Top'] + face_box['Height']) * frame.shape[0]),
                                    int(face_box['Left'] * frame.shape[1]):int((face_box['Left'] + face_box['Width']) * frame.shape[1])]

                    # Guardar la imagen en un archivo (por ejemplo, en formato PNG)
                    # Convertir la imagen de formato de matriz a bytes
                    ret, buffer = cv2.imencode('.png', face_image)
                    image_bytes = io.BytesIO(buffer)

                    image_name = str(index_person) + "-" + datetime.now().strftime('%Y%m%d_%H%M%S%f') + ".png"
                    bucket_path = "suspects/" + datetime.now().strftime('%Y%m%d') + "/"
                    cv2.imwrite(image_name, face_image)
                    print("\nSubiendo imagen...")
                    s3.upload_fileobj(image_bytes, credentials.bucket_name, bucket_path + image_name)
                    SearchPerson(rekognition, image_name, bucket_path, s3)
                    AddImageToCollection(rekognition, image_name, bucket_path)
                cap.release()
    os.remove(urlCompresedVID)

# Código propio (ChatGPT)
# Función encarga de añadir a la colección las imagenes
def AddImageToCollection(rekognition, image_name, bucket_path):
    response = rekognition.index_faces(
        CollectionId=credentials.collection_id,
        Image={
            'S3Object': {
                'Bucket': credentials.bucket_name,
                'Name': bucket_path + image_name
            }
        }
    )

# Código propio (ChatGPT)
def SearchPerson(rekognition, image_name, bucket_path, s3):

    # Buscar caras similares en la colección de caras
    search_response = rekognition.search_faces_by_image(
        CollectionId=credentials.collection_id,
        Image={
            'S3Object': {
                'Bucket': credentials.bucket_name,
                'Name': bucket_path + image_name
            }
        },
        FaceMatchThreshold=70,  # Umbral de confianza para considerar una coincidencia
        MaxFaces=10  # Número máximo de caras a devolver
    )
    # Si se detectan 3 o mas conicidencias se define a la persona como reincidente guaradando
    # la foto en ontra carpeta dentro del bucket
    if len(search_response['FaceMatches']) >= 3:
        SaveRepeatOffenders(s3, bucket_path, image_name)
        
# Código propio
# Se cambia de ruta las personas reincidentes
def SaveRepeatOffenders(s3, bucket_path, image_name):
    print("Se han detectado reincidentes")
    s3.copy_object(
            Bucket= credentials.bucket_name,
            CopySource={'Bucket': credentials.bucket_name, 'Key': bucket_path + image_name},
            Key="repeatOffenders/" + image_name
        )


# Código propio
# Función que se encarga de verificar si la colección existe en la lista de colecciones
# y si no existe crear una nueva
def MakeCollection(rekognition):
    response = rekognition.list_collections()

    collections = response['CollectionIds']
    if credentials.collection_id in collections:
        print(f"La colección '{credentials.collection_id}' ya existe.")
    else:
        rekognition.create_collection(CollectionId=credentials.collection_id)
        print(f"Se ha creado la colección '{credentials.collection_id} de imágenes'.")

