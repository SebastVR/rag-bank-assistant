import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.config.settings import settings


class S3Storage:
    """
    Clase general para manejar almacenamiento en S3 o MinIO usando boto3.
    Elige el backend según settings.app_env: 'dev' (MinIO) o 'prod' (AWS S3).
    """

    def __init__(self):
        env = settings.app_env.lower()
        self.env = env
        if env in ("prod", "production"):
            self.bucket_name = settings.aws_s3_bucket_name
            self.s3_client = boto3.client(
                "s3",
                region_name=settings.aws_region_name,
                aws_access_key_id=settings.aws_s3_access_key_id,
                aws_secret_access_key=settings.aws_s3_secret_access_key,
                config=Config(signature_version="s3v4"),
            )
        else:
            self.bucket_name = settings.minio_bucket_name
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=settings.minio_endpoint,
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                config=Config(signature_version="s3v4"),
            )

    def write_file(self, folder, object_name, file_data):
        """
        Sube un archivo a la carpeta indicada dentro del bucket.
        """
        full_path = self._build_path(folder, object_name)

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_path,
                Body=file_data,
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "NoSuchBucket":
                self.create_bucket_if_not_exists()
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=full_path,
                    Body=file_data,
                )
            else:
                raise Exception(f"Error al escribir el archivo en el bucket: {str(e)}")
        except Exception as e:
            raise Exception(f"Error al escribir el archivo en el bucket: {str(e)}")

        return full_path

    def get_public_url(self, folder, object_name):
        """
        Devuelve una URL pública si el bucket/objeto es público.
        """
        full_path = self._build_path(folder, object_name)

        if self.env in ("dev", "development"):
            endpoint = settings.minio_endpoint.rstrip("/")
            return f"{endpoint}/{self.bucket_name}/{full_path}"
        return f"https://{self.bucket_name}.s3.amazonaws.com/{full_path}"

    def generate_presigned_url(self, folder, object_name, expiration=3600):
        """
        Genera una URL presignada para acceder al archivo.
        Funciona tanto para MinIO como para AWS S3.
        """
        full_path = self._build_path(folder, object_name)

        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": full_path,
                },
                ExpiresIn=expiration,
            )
        except Exception as e:
            print(f"Error al generar el enlace presignado: {str(e)}")
            return None

    def delete_object(self, folder, object_name):
        """
        Elimina un archivo del bucket.
        """
        full_path = self._build_path(folder, object_name)

        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=full_path,
            )
        except Exception as e:
            raise Exception(f"Error al eliminar el archivo en el bucket: {str(e)}")

    def delete_objects(self, folder, object_keys):
        """
        Elimina varios archivos del bucket.
        object_keys debe ser una lista de nombres/rutas.
        """
        if not object_keys:
            return

        keys = [
            {
                "Key": self._build_path(folder, key),
            }
            for key in object_keys
        ]

        try:
            self.s3_client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    "Objects": keys,
                    "Quiet": False,
                },
            )
        except Exception as e:
            raise Exception(f"Error al eliminar archivos en el bucket: {str(e)}")

    def bucket_exists(self):
        """
        Verifica si el bucket existe.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError:
            return False

    def create_bucket_if_not_exists(self):
        """
        Crea el bucket si no existe.
        Útil para MinIO en desarrollo.
        """
        if self.bucket_exists():
            return

        try:
            if self.env in ("prod", "production"):
                if settings.aws_region_name == "us-east-1":
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={
                            "LocationConstraint": settings.aws_region_name,
                        },
                    )
            else:
                self.s3_client.create_bucket(Bucket=self.bucket_name)

        except Exception as e:
            raise Exception(f"Error al crear el bucket: {str(e)}")

    def _build_path(self, folder, object_name):
        """
        Construye la ruta final del archivo dentro del bucket.
        """
        folder = folder.strip("/") if folder else ""
        object_name = object_name.strip("/")

        return f"{folder}/{object_name}" if folder else object_name
