# CodeOwl Backend

### About 
Server of CodeOwl project. Ensures the coordinated operation of the site, neural network and other parts.


### Hardware requirements 
- Processor with at least 4 cores with a clock speed of at least 2.7 GHz
- RAM 8 GB or more
- 2 GB disk space

### Software requirement
- Windows 7 or newer
- Python 3.6 or newer
- CUDA driver (if you have GPU)

### Installation 
Download the repository and open a terminal in the "CodeOwlBackend" folder.
Run the commands:
```
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```
To download and connect the model, run the command:
```
python downloadmodel.py
```

### Usage 
Activate the virtual environment with the command, if you haven't already done so.
```
venv\Scripts\activate.bat
```

Start the server:
```
python codeowl\manage.py runserver
```
Open http://127.0.0.1:8000 and enjoy :)
