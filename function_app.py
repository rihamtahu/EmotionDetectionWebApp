import azure.functions as func
import logging
import os
import json
from io import BytesIO
from datetime import datetime

from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials

app = func.FunctionApp()

@app.blob_trigger(arg_name="myblob", path="images-upload/{name}", connection="AzureWebJobsStorage")
def ImageUploadTrigger(myblob: func.InputStream):
    name = myblob.name.split('/')[-1]
    logging.info(f"Processing image: {name}, Size: {myblob.length} bytes")

    try:
        # Configuration Face API
        endpoint = os.getenv("FACE_API_ENDPOINT")   # ex: "https://<region>.api.cognitive.microsoft.com/"
        api_key = os.getenv("FACE_API_KEY")

        face_client = FaceClient(endpoint, CognitiveServicesCredentials(api_key))

        # Lire l'image depuis le flux blob
        image_stream = BytesIO(myblob.read())

        # Détection de visages avec émotions
        detected_faces = face_client.face.detect_with_stream(
            image=image_stream,
            return_face_attributes=['emotion']
        )

        emotions_list = []
        for face in detected_faces:
            emotions = face.face_attributes.emotion
            # On garde la principale émotion détectée
            dominant_emotion = max(emotions.__dict__, key=lambda k: getattr(emotions, k))
            emotions_list.append(dominant_emotion)

        result = {
            "ImageName": name,
            "FacesCount": len(detected_faces),
            "Emotions": emotions_list if emotions_list else ["neutral"],
            "ProcessedAt": datetime.utcnow().isoformat()
        }

        # Sauvegarder le résultat dans Blob Storage
        connection_string = os.getenv("AzureWebJobsStorage")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client("results")
        container_client.create_container()  # Ignore si déjà existant

        result_file_name = f"result-{name}.json"
        result_blob = container_client.get_blob_client(result_file_name)
        result_blob.upload_blob(json.dumps(result, indent=4), overwrite=True)

        logging.info(f"Analysis complete: {json.dumps(result, indent=4)}")

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        raise


@app.route(route="UploadImage", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def UploadImage(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger received a request.')

    try:
        # Récupérer le fichier uploadé
        file = req.files.get('file')
        if not file:
            return func.HttpResponse("No file uploaded", status_code=400)

        # Générer un nom unique
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"

        # Upload dans Blob Storage (container images-upload)
        connection_string = os.getenv("AzureWebJobsStorage")
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client("images-upload")
        container_client.create_container()  # Ignore si déjà existant
        container_client.upload_blob(name=filename, data=file.stream, overwrite=True)

        # Appeler Face API directement pour retourner l’émotion immédiatement
        face_client = FaceClient(os.getenv("FACE_API_ENDPOINT"), CognitiveServicesCredentials(os.getenv("FACE_API_KEY")))
        image_stream = BytesIO(file.read())
        detected_faces = face_client.face.detect_with_stream(
            image=image_stream,
            return_face_attributes=['emotion']
        )

        emotions_list = []
        for face in detected_faces:
            emotions = face.face_attributes.emotion
            dominant_emotion = max(emotions.__dict__, key=lambda k: getattr(emotions, k))
            emotions_list.append(dominant_emotion)

        result = {
            "ImageName": filename,
            "FacesCount": len(detected_faces),
            "Emotions": emotions_list if emotions_list else ["neutral"],
            "ProcessedAt": datetime.utcnow().isoformat()
        }

        # Retourner le résultat au front
        return func.HttpResponse(json.dumps(result), mimetype="application/json", status_code=200)

    except Exception as e:
        logging.error(f"Error in UploadImage: {e}")
        return func.HttpResponse(str(e), status_code=500)
