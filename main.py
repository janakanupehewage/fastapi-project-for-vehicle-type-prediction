from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import io

# Initialize FastAPI app
app = FastAPI()

# Load the trained model
model = load_model('vehicle_type_identifier_model.keras')

# Define class labels for vehicle types
class_names = ['bus', 'car', 'motorcycle', 'truck']


# Preprocessing function for the input image
def preprocess_image(image) -> np.ndarray:
    
    image = image.resize((150, 150))
    image = np.array(image)
    
    if image.shape[-1] == 4:
        image = image[..., :3]
    
    image = image / 255.0
    image = np.expand_dims(image, axis=0)  
    
    return image

# GET endpoint to check the API status
@app.get("/")
async def root():
    return {"message": "The Vehicle Type Prediction API is ready to use. Upload an image of a bus, car, motorcycle, or truck, and the API will tell you what type of vehicle it is."}



# POST endpoint to upload and predict the vehicle type
@app.post("/predict/")
async def predict_vehicle(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        processed_image = preprocess_image(image)

        # Make the prediction
        predictions = model.predict(processed_image)
        predicted_class = class_names[np.argmax(predictions[0])]

        return JSONResponse(content={"vehicle_type": predicted_class})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


