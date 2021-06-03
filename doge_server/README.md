# Run Doge Detector on Flask Web server


Setup and run


```
sudo apt-get -yqq update
sudo apt-get -yqq install python3-pip
pip3 install --upgrade pip
pip3 install -r requirements.txt

FLASK_APP=main.py python3 -m flask run --host=0.0.0.0 --port=5000
```

