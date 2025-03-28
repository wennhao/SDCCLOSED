from ultralytics import YOLO
from roboflow import Roboflow

rf = Roboflow(api_key="bPqPDgjLmQvwrzTOItmf") # don't share
project = rf.workspace("sdcclosedcategory").project("projact_f_w-pafgp-vsknt")
version = project.version(4)
dataset = version.download("yolov8")

model = YOLO('yolov8n.pt')

results = model.train(
   data=f"{dataset.location}/data.yaml",
   imgsz=640,
   epochs=10,
   batch=16,
   name='yolov8n_signs'
)