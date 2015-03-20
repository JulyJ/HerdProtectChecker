from os import listdir, stat
from os.path import isfile, join
from bs4 import BeautifulSoup
import urllib


# mypath = "./files"
# onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]

# for f in listdir(mypath):
#     file = join(mypath, f)
#     if (isfile(file)):
#         print stat(file)

herdprotectHtml = urllib.urlopen("http://www.herdprotect.com/calc.exe-9018a7d6cdbe859a430e8794e73381f77c840be0.aspx")


soup = BeautifulSoup(herdprotectHtml)

# params = soup.find_all("div", class_="keyvaluepair")

parsedFileWebInfo = {
    'name': '',
    'publisher': '',
    'product': '',
    'descr': '',
    'md5': '',
    'sha1': '',
    'sha256': '',
    'size': '',
    'version': '',
    'copyright': ''
}

# _parsedFileInfo = {
#     'File name:',
# }

keysWebMap = {
    'File name:': 'name',
    'Publisher:': 'publisher',
    'Product:': 'product',
    'Version:': 'descr',
    'MD5:': 'md5',
    'SHA-1:': 'sha1',
    'SHA-256:': 'sha256',
    'File size:': 'size',
    'Product version:': 'version',
    'Copyright:': 'copyright'
}

# keysNeeded = [
#     'File name:',
#     'Publisher:',
#     'Product:',
#     'Version:',
#     'MD5:',
#     'SHA-1:',
#     'SHA-256:',
#     'File size:',
#     'Product version:',
#     'Copyright:'
# ]

def findKey(keyName):
    return keysWebMap.get(keyName, None)

for param in soup.find_all("div", class_="keyvaluepair"):
    keyEl = param.find(class_="key")
    valueEl = param.find(class_="value")

    if (keyEl):
        parsedKeyName = keyEl.string.encode('utf-8')
        keyName = findKey(parsedKeyName)

        if keyName is not None:
            parsedFileWebInfo[keyName] = valueEl.string.encode('utf-8')

print parsedFileWebInfo
