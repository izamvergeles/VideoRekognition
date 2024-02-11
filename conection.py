import boto3
# Código realizado con la ayuda de Pablo Nicolás

# Iniciar AWS
def login(id, key, token, region_name='us-east-1', bucket='izam'):
    print("\033[1mAWS Configuration Status\033[0m")
    try:
        # Verificar credenciales intentando listar "contenedores"
        s3_client = boto3.client('s3',
                          aws_access_key_id=id,
                          aws_secret_access_key=key,
                          aws_session_token=token,
                          region_name=region_name)
        s3_client.list_buckets()

        # Verificar la existencia del bucket
        s3_client.head_bucket(Bucket=bucket)

        # Configuración cliente AWS Rekognition
        rekognition_client = boto3.client('rekognition',
                              aws_access_key_id=id,
                              aws_secret_access_key=key,
                              aws_session_token=token,
                              region_name=region_name)

        print("\033[92mCredentials configured correctly.\033[0m")

        # Devuelve tanto el cliente rekognition como el de almacenamiento s3
        return rekognition_client, s3_client
    except Exception as e:
        # Se imprime el error
        error_message = str(e)
        print(f"\033[91mError: {error_message}\033[0m")
        return None, None