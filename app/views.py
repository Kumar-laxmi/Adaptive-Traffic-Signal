# Libraries related to Django
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files.base import ContentFile
from .models import UploadedImage
from .forms import UploadImageForm


# Libraries related to Image Processing
from PIL import Image
from io import BytesIO
import base64
import plotly.express as px
from plotly.offline import plot

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
    UploadedImage.objects.all().delete()
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    
        image_addr = 'media/' + UploadedImage.objects.values_list('image').latest('uploaded_at')[0]
        image = Image.open(image_addr)
        image_np = np.array(image)

        # Define colors for different classes
        class_colors = {
                    0: (0, 0, 255),
                    1: (0, 255, 255),
                    2: (255, 0, 0),
                    3: (255, 255, 0)
                    # Add more class indices and colors as needed
                }
        
        # Define the Coordinates of the Region Of Interest
        quads = [
            np.array([(588, 551), (819, 725), (527, 1079), (47, 1079)], np.int32),
            np.array([(1307, 509), (1494, 341), (1916, 536), (1916, 819)], np.int32),
            np.array([(1057, 122), (1222, 194), (1718, 137), (1598, 49)], np.int32),
            np.array([(410, 374), (716, 216), (243, 2), (4, 148)], np.int32)
        ]

        # ROI color (Green)
        roi_color = (0, 255, 0)

        # Create a list to store the vehicle counts for each lane
        vehicle_counts = [0] * len(quads)

        # Loading the custom model
        model = YOLO('app/model/best.pt')
        detections = model(image)

        # Initialize counters for each class and ROI
        vehicle_counts = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]


        # Iterate through each detection
        for box in detections[0].boxes:
            class_index = int(box.cls.item())
            if class_index in [0, 1, 2, 3]:  # Vehicle class indices
                bounding_box = box.xyxy.tolist()[0]

                # Check if the center of the bounding box is inside any of the quads
                bbox_center = ((bounding_box[0] + bounding_box[2]) / 2, (bounding_box[1] + bounding_box[3]) / 2)
                for i, quad in enumerate(quads):
                    if cv2.pointPolygonTest(quad, bbox_center, False) == 1:
                        vehicle_counts[i][class_index] += 1
        
        # Array to store the total number of vehicles in each Region Of Interest
        total_counts = [sum(roi_counts) for roi_counts in vehicle_counts]


        # Flatten the data into a 1D array
        data_flat = np.array(vehicle_counts).flatten()

        # Create a histogram from the flattened data
        histogram_fig = px.histogram(
            data_flat,
            nbins=20,  # You can adjust the number of bins as needed
            labels=dict(x="Productivity"),
        )

        # Save the figure into a variable
        plot_vehicle = plot(histogram_fig, auto_open=False, output_type='div')

        # Draw regions of interest and lane names
        for i, quad in enumerate(quads):
            lane_name = f'lane{i + 1}'
            lane_color = roi_color

            # Draw region of interest
            cv2.polylines(image_np, [quad], isClosed=True, color=lane_color, thickness=2)

            # Draw lane name
            cv2.putText(image_np, lane_name, (quad[0][0], quad[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, lane_color, 2)

        # Draw bounding boxes on vehicles
        for box in detections[0].boxes:
            class_index = int(box.cls.item())
            bounding_box = box.xyxy.tolist()[0]
            confidence_score = box.conf.item()

            class_color = class_colors.get(class_index, (0, 0, 0))  # Default color if not found

            xmin, ymin, xmax, ymax = bounding_box
            cv2.rectangle(image_np, (int(xmin), int(ymin)), (int(xmax), int(ymax)), class_color, 2)
            cv2.putText(image_np, f'{confidence_score:.2f}', (int(xmin), int(ymin) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, class_color, 1)

        # Store Vehicle Count in the variables
        lane1 = lane2 = lane3 = lane4 = 0
        for i, count in enumerate(total_counts):
            if i == 0:
                lane1 = count
            elif i == 1:
                lane2 = count
            elif i == 2:
                lane3 = count
            elif i == 3:
                lane4 = count
            else:
                print('Warning in Lane Vehicle calculation!!!')

        # Convert the NumPy array to an image
        image = Image.fromarray(image_np)

        new_uploaded_image = UploadedImage()
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_file = ContentFile(image_bytes.getvalue(), name='new_image.jpg')
        new_uploaded_image.image.save('new_image.jpg', image_file)

        return render(request, 'index.html', {
            'form': form, 
            'image': new_uploaded_image,
            'lane1': lane1,
            'lane2': lane2,
            'lane3': lane3,
            'lane4': lane4,
            'plot_vehicle': plot_vehicle
        })
    else:
        form = UploadImageForm()
        images = UploadedImage.objects.all()
        return render(request, 'index.html', {
            'form': form, 
            'images': images
        })


def index_temp(request):
    return render(request, 'index_temp.html', {})