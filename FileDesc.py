
import subprocess
import os

parsedLocalFileInfo = {
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

keysLocalMap = {
    'Original Name:': 'name',
    'Publisher:': 'publisher',
    'Product:': 'product',
    'Version:': 'descr',
    'MD5:': 'md5',
    'SHA-1:': 'sha1',
    'SHA-256:': 'sha256',
    'Product version:': 'version',
    'Copyright:': 'copyright'
}



subprocess.call("sigcheck.exe -a -h 7z.exe >> filedesc.txt", shell=True)
subprocess.call("filesize 7z.exe >> filedesc.txt", shell=True)

input_file = open('filedesc.txt')
lines = input_file.readline()
input_file.close()

for i, line in enumerate(lines):
	keyEl = line.split()
    valueEl = line.split()

    if (keyEl):
        parsedKeyName = keyEl.string.encode('utf-8')
        keyName = findKey(parsedKeyName)

        if keyName is not None:
            parsedLocalFileInfo[keyName] = valueEl.string.encode('utf-8')

 input_file.close()