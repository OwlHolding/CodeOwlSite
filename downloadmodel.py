import urllib.request
from zipfile import ZipFile
import os
print("Start Downloading")
with urllib.request.urlopen('http://4k3skl.keenetic.pro:8088/model.zip') as f:
    data = f.read()
print("Download successfully")
with open("model.zip", "wb") as f:
    f.write(data)
print("Extracting file")
with ZipFile("model.zip") as f:
    f.extractall(path="codeowl/main/static/models")
print("Deleting temporary files")
os.remove("model.zip")
print("Successfully")
