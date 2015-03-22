from bs4 import BeautifulSoup			#Additional component for HTML parsing
import urllib
import subprocess
import os
import sys
import re
import codecs
import ctypes

# loglevel = 1 - additional logs to cmd-line for debugging
loglevel = 0 

# Global Dictionaries 							
keysLocalMap = {
		'Original Name:': 'name',
		'Publisher:': 'publisher',
		'Product:': 'product',
		'Description:': 'descr',
		'MD5:': 'md5',
		'SHA1:': 'sha1',
		'SHA256:': 'sha256',
		'Prod version:': 'version',
		'Copyright:': 'copyright'
	}
keysWebMap = {
		'File name:': 'name',
		'Publisher:': 'publisher',
		'Product:': 'product',
		'Description:': 'descr',
		'MD5:': 'md5',
		'SHA-1:': 'sha1',
		'SHA-256:': 'sha256',
		'File size:': 'size',
		'Product version:': 'version',
		'Copyright:': 'copyright'
	}

def findLocalKey(keyName):
	return keysLocalMap.get(keyName, None)

def findWebKey(keyName):
	return keysWebMap.get(keyName, None)

# Processing local file information
def getLocalResult(filename):
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
	# getting file propreties to temporary text file
	subprocess.call("sigcheck.exe -a -h "+ folder +'/'+ filename +" >> localfiledesc.txt", shell=True)
	lineEl = []
	# opening text file in latin-1 encoding (to solve unicode problems)
	input_attribute_file = codecs.open("localfiledesc.txt", encoding='latin-1')
	# itterations for every line in text file split data separated by TABs
	for line in input_attribute_file:
		lineEl = line.split('\t')
		if (len(lineEl) > 1):				# excluding lines with additional information
			keyEl = lineEl[1]				
			valueEl = lineEl[2][0:-2]		# removing line ending
			if (keyEl):
				keyName = findLocalKey(keyEl)	
				if keyName is not None:
					# latin-1 used to solve unicode problem
					parsedLocalFileInfo[keyName] = valueEl.encode('latin-1').strip()
	input_attribute_file.close()
	# remove temporary text file
	os.remove("localfiledesc.txt")
	# get filesize and put it to the dictionary
	statinfo = os.stat(folder +'/'+ filename)
	sizeEl = unicode(statinfo.st_size)
	parsedLocalFileInfo['size'] = sizeEl
	# the file name is given to uppercase (to avoid mismatches due to register)
	parsedLocalFileInfo['name'] = filename	
	if loglevel == 1:
		print (parsedLocalFileInfo)
	return parsedLocalFileInfo

# Processing cloud file information
def getWebResult(filename, sha):
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
	# checking opened url coincedence with original to avoid homepage redirect in case of no data in cloud
	url = urllib.urlopen("http://www.herdprotect.com/" + filename + "-" + str(sha) + ".aspx").geturl()
	if url == ("http://www.herdprotect.com/" + filename + "-" + str(sha) + ".aspx"):							
		herdprotectHtml = urllib.urlopen("http://www.herdprotect.com/" + filename + "-" + str(sha) + ".aspx")
		global filescnt
		filescnt = filescnt+1
		# parsing html
		soup = BeautifulSoup(herdprotectHtml)
		for param in soup.find_all("div", class_="keyvaluepair"):
			keyEl = param.find(class_="key")
			valueEl = param.find(class_="value")

			if (keyEl):
				parsedKeyName = keyEl.string 
				keyName = findWebKey(parsedKeyName)
				if keyName is not None:
					parsedFileWebInfo[keyName] = valueEl.get_text(strip=True).encode('latin-1').strip()
		# parsing size from web to kb
		webSize = parsedFileWebInfo['size']
		if (webSize):
			pattern = '\(([0-9\,]+)[^\)]+\)'
			convertedSize = re.search(pattern, webSize).groups()[0].replace(",", "")
			parsedFileWebInfo['size'] = unicode(convertedSize)
		#parsing publisher
		webPublisher = parsedFileWebInfo['publisher']
		if (webPublisher):
			pattern = '([\w\s\.]*)'
			convertedPublisher = re.search(pattern, webPublisher).groups()[0]
			parsedFileWebInfo['publisher'] = unicode(convertedPublisher)
		# getting checksum values to upper case (to avoid mismatches due to register)
		parsedFileWebInfo['md5'] = parsedFileWebInfo['md5'].upper()
		parsedFileWebInfo['sha1'] = parsedFileWebInfo['sha1'].upper()
		parsedFileWebInfo['sha256'] = parsedFileWebInfo['sha256'].upper()
		# If there is no value for parameter in cloud put standart "n/a"
		for keyValue in parsedFileWebInfo:
			if parsedFileWebInfo[keyValue] == "":
				parsedFileWebInfo[keyValue] = "n/a"
		if loglevel == 1:
			print (parsedFileWebInfo)
	# if url is not the same as we opened - there is no data in cloud.
	else:
		errorlog.write ('\nNo data in Cloud.')
		global cloudExistanceFlag
		cloudExistanceFlag = 'false'
	global webUrl
	webUrl = url
	return parsedFileWebInfo


#Getting file list from cmd-line arguments:
for arg in sys.argv:
	folder = arg
try:
	files = os.listdir(folder)
except OSError:	
	ctypes.windll.user32.MessageBoxA(0, "Please specify existing folder or path with the files as an argument.\nExample: > main.py testfolder", "Checker Report", 0)
	sys.exit()
fileslst =  os.listdir(folder)

# Counters for final report:
globalerrorcnt = 0
filescntall = 0
filescnt = 0
localResult = {}
webResult = {}

# Error log started:
errorlog = open('log.txt', 'w')
errorlog.write("HerdProtect Checker report:\n-----------------------------")

# Starting itterations for file list:
for item in fileslst:
	errorcnt = 0 
	filescntall = filescntall + 1
	cloudExistanceFlag = 'true'				# flag signaling the presence file data in the cloud
	if item[-1] == '\n':		# cutting new line ending
		filename = item[0:-1]
	else:
		filename = item
	print
	print('File in progress: ' + filename)
	errorlog.write ('\n\nFile Name: ' + filename)
	
	localResult[filename] = getLocalResult(filename)
	sha = localResult[filename]['sha1']
	webResult[filename] = getWebResult(filename, sha)

	# if flag is not 'false' proceed file properties comparison
	if cloudExistanceFlag != 'false':
		localRes = localResult[filename]
		webRes = webResult[filename]
		for keyName in webRes:
			if webRes[keyName] != localRes[keyName]:
				errorlog.write ("\n   Parameter Name: " + str(keyName))
				errorlog.write ("\n      Cloud: " + str(webRes[keyName]))
				errorlog.write ("\n      Local: " + str(localRes[keyName]))
				errorcnt = errorcnt+1
		globalerrorcnt = globalerrorcnt + errorcnt
		errorlog.write ("\nURL: " + str(webUrl))
		errorlog.write ('\nErrors found in file: ' + filename + ' : '+ str(errorcnt))
		
errorlog.write ('\n\nErrors found global: ' + str(globalerrorcnt) + '\n-----------------------------')
errorlog.close()

# Show final messagebox to user with counters and inforamtion
ctypes.windll.user32.MessageBoxA(0, "Files in folder: " + str(filescntall) + "\nFiles checked: " + str(filescnt) + "\nErrors Found: " + str(globalerrorcnt) + "\nSee log.txt for errors", "Checker Report", 0)