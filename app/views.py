# Libraries related to Django
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import UploadedImage
from .forms import UploadImageForm


# Libraries related to Image Processing
from PIL import Image
import io
import base64

# Libraries related to Computer Vision
import cv2
import numpy as np
import torch
from ultralytics import YOLO

def get_class_label_from_index(class_index):
    class_labels = {
        0: 'Bicycle',  # Replace with actual class labels
        1: 'Car',
        2: 'Bus',
        3: 'Lorry'
        # Add more class indices and labels as needed
    }

    return class_labels.get(class_index, 'unknown')

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = UploadImageForm()
    
    images = UploadedImage.objects.all()

    return render(request, 'index.html', {'form': form, 'images': images})

def result(request):
    if request.method == 'POST':
        form = UserImage(request.POST, request.FILES)  
        if form.is_valid():  
            form.save()  
  
            # Getting the current instance object to display in the template  
            imgage = form.instance
            image_np = np.array(image)

            # Define colors for different classes
            class_colors = {
                0: (0, 0, 255),
                1: (0, 255, 255),
                2: (255, 0, 0),
                3: (255, 255, 0)
                # Add more class indices and colors as needed
            }

            # Loading the custom model
            model = YOLO('./model/best.pt')
            detections = model(image)

            # Access detection results and display on image
            for box in detections[0].boxes:
                class_index = int(box.cls.item())
                bounding_box = box.xyxy.tolist()[0]
                confidence_score = box.conf.item()

                class_label = get_class_label_from_index(class_index)
                class_color = class_colors.get(class_index, (0, 0, 0))  # Default color if not found

                # Draw bounding box and label on the image_np
                xmin, ymin, xmax, ymax = bounding_box
                cv2.rectangle(image_np, (int(xmin), int(ymin)), (int(xmax), int(ymax)), class_color, 2)
                cv2.putText(image_np, f'{class_label} {confidence_score:.2f}', (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, class_color, 1)

            # Convert the NumPy array to an image
            image = Image.fromarray(image_np)

            # Convert the PIL Image to bytes
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="PNG")
            image_data = base64.b64encode(image_bytes.getvalue()).decode()

            # Pass the image data to the template context
            context = {
                'form': form,
                'image_data': f"data:image/png;base64,{image_data}"
            }
            
            return render(request, 'result.html', context)
        else:
            form = UserImageForm()  
    return render(request, 'result.html', {'form': form})

def index_temp(request):
    return render(request, 'index_temp.html', {})