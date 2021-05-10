# Run web server:
# python3 -m flask run --host=0.0.0.0 --port=5000

import flask
import numpy as np
import cv2
import sys
import torch
import torchvision


DEVICE = 'cpu'


####################################
# Load model
###################################
print('Loading doge model...')

model = torchvision.models.detection.retinanet_resnet50_fpn(
  pretrained=False, pretrained_backbone=False)
model = model.to(DEVICE)
model.load_state_dict(torch.load('model.pth', map_location=DEVICE))
model.eval()
print('Done loading doge model')

def run_model(img):
    img = img.transpose([2, 0, 1])
    img = torch.from_numpy(img).float()
    img = img.to(DEVICE)
    detections = model([img])[0]
    print(detections)
    return detections

####################################
# Flask
###################################
app = flask.Flask(__name__)

@app.route("/")
def index():
    print('ah something is coming')
    return flask.render_template(
      'base.html',
      image_url='static/intro.jpeg',
      message='Try upload new image!',
      detections=[{
        'x1': 100,
        'y1': 10,
        'x2': 200,
        'y2': 100,
        'score': 0.9
      }, {
        'x1': 190,
        'y1': 100,
        'x2': 300,
        'y2': 250,
        'score': 0.1
      }]
    )


@app.route("/process_image", methods=['GET', 'POST'])
def process_image():
    result = {'message': ''}
    
    # try to parse as image and run model.
    detections = None
    if 'fileToUpload' not in flask.request.files:
      return flask.redirect("/", code=302)
    try:
        x = flask.request.files['fileToUpload']
        imgbuffer = x.stream.read()
        img = np.frombuffer(imgbuffer, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) / 255.0
        detections = run_model(img)
    except Exception as e:
        result['message'] = 'error: ' + str(e)

    # parse result.
    if detections is not None:
      
      result['image_url'] = 'tmp/' + x.filename
      with open(result['image_url'], 'wb') as f:
        f.write(imgbuffer)
      
      result['message'] = 'No doge very sad'
      result['detections'] = []
      for box, score, label in zip(detections['boxes'],
                                   detections['scores'],
                                   detections['labels']):
        if score > 0.2 and int(label) == 69:
            x1, y1, x2, y2 = box
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            result['detections'].append({
                'x1': x1,
                'x2': x2,
                'y1': y1,
                'y2': y2,
                'score': float(score)
            })
            
            if score > 0.8:
                result['message'] = 'very doge, wow amazing'

    return flask.render_template(
      'base.html',
      message=result['message'],
      image_url=result.get('image_url', ''),
      detections=result.get('detections', []),
    )


@app.route('/tmp/<path:filename>')
def custom_static(filename):
    return flask.send_from_directory(
       'tmp', filename)


