# Emotion Detection Web Application

Cloud-native emotion detection application built with Python and Microsoft Azure.

## Overview

This project implements a serverless image-processing pipeline capable of detecting faces and identifying dominant facial emotions.

Users can upload an image through an HTTP endpoint. The application stores the image in Azure Blob Storage and analyzes detected faces using Azure AI services.

The project was developed to explore serverless computing, event-driven architectures, cloud storage and AI service integration.

## Technologies

- Python
- Microsoft Azure
- Azure Functions
- Azure Blob Storage
- Azure Face API
- Azurite
- REST API
- JSON

## Architecture

The application provides two Azure Functions workflows.

### HTTP Image Upload

1. A client sends an image to the `UploadImage` HTTP endpoint.
2. The image is stored in the `images-upload` Blob Storage container.
3. Azure Face API analyzes the image.
4. The dominant emotion of each detected face is extracted.
5. The result is returned to the client as JSON.

### Event-Driven Processing

A Blob Trigger automatically reacts when an image is added to the `images-upload` container.

The function:

1. Reads the uploaded image.
2. Sends it to Azure Face API.
3. Detects faces and their emotion attributes.
4. Determines the dominant emotion for each detected face.
5. Generates a JSON analysis result.
6. Stores the result in the `results` Blob Storage container.

Example output:

```json
{
  "ImageName": "example.jpg",
  "FacesCount": 1,
  "Emotions": ["happiness"],
  "ProcessedAt": "timestamp"
}
