from bs4 import BeautifulSoup			#Additional component for HTML parsing
import urllib
import subprocess
import os
import re
import tkMessageBox
import codecs

#Getting file list from cmd-line arguments:
for arg in sys.argv:
	folder = arg
fileslst =  os.listdir(folder) 

def findLocalKey(keyName):
	return keysLocalMap.get(keyName, None)

def findWebKey(keyName):
    return keysWebMap.get(keyName, None)

#Dictionaries for file propreties:
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

# Counters for final report:
globalerrorcnt = 0
filescnt = 0

# Error log started:
errorlog = open('log.txt', 'w')
errorlog.write("HerdProtect Checker report:")

# Starting itterations for file list:
for item in fileslst:
	errorcnt = 0 										# error for one file counter
	flag = 'true'										# flag signaling the presence file data in the cloud
	if item[-1] == '\n':								# cutting new line ending
		filename = item[0:-1]
	else:
		filename = item
	print
	print('File in progress: ' + filename)				# progress output to the cmd-line
	errorlog.write ('\nFile Name: ' + filename)			# progress output to the error log
	subprocess.call("sigcheck.exe -a -h "+ folder +'/'+ filename +" >> localfiledesc.txt", shell=True)		# getting file propreties to temporary text file
	lineEl = []
	input_attribute_file = codecs.open("localfiledesc.txt", encoding='latin-1')								# opening text file in latin-1 encoding (to solve unicode problems)
	for line in input_attribute_file:					# itterations for every line in text file
		lineEl = line.split('\t')						# data in text file separated by tabs
		if (len(lineEl) > 1):							# excluding lines with additional information
			keyEl = lineEl[1]							# getting Name of file proprety value
			valueEl = lineEl[2][0:-2]					# removing line ending
			if (keyEl):									# checking value existance
				keyName = findLocalKey(keyEl)			# getting name of parameter from dictionary
				if keyName is not None:					# do we need this parameter? check in dictionary
					parsedLocalFileInfo[keyName] = valueEl
	input_attribute_file.close()
	os.remove("localfiledesc.txt")						# remove temporary text file

	statinfo = os.stat(folder +'/'+ filename)			# get file size
	sizeEl = unicode(statinfo.st_size)					# convert file size from longint to string
	parsedLocalFileInfo['size'] = sizeEl				# put file size value to the dict
	parsedLocalFileInfo['name'] = parsedLocalFileInfo['name'].upper()		# the file name is given to uppercase (to avoid mismatches due to register)
	#print parsedLocalFileInfo												# output resulting dictionary to cmd for debugging (commented by default)

	url = urllib.urlopen("http://www.herdprotect.com/" + filename + "-" + parsedLocalFileInfo['sha1'] + ".aspx").geturl()		# checking url opened
	if url == ("http://www.herdprotect.com/" + filename + "-" + parsedLocalFileInfo['sha1'] + ".aspx"):							# checking opened url coincedence with original to avoid homepage redirect in case of no data in cloud
		herdprotectHtml = urllib.urlopen("http://www.herdprotect.com/" + filename + "-" + parsedLocalFileInfo['sha1'] + ".aspx")# opening url
		filescnt = filescnt+1 												# file counter increased
		soup = BeautifulSoup(herdprotectHtml)								# preparing html for parsing
		for param in soup.find_all("div", class_="keyvaluepair"):			# zooming to parameters div
		    keyEl = param.find(class_="key")								# getting Name of file proprety value
		    valueEl = param.find(class_="value")							# getting parameter value

		    if (keyEl):														# cheking value existance
		        parsedKeyName = keyEl.string 								# converting parameter to string
		        keyName = findWebKey(parsedKeyName)							# getting name of parameter from dictionary

		        if keyName is not None:										# do we need this parameter? check in dictionary
		            parsedFileWebInfo[keyName] = valueEl.string
		
		webSize = parsedFileWebInfo['size']									#getting file size value from dict
		if (webSize):														# value exists?
			pattern = '\(([0-9\,]+)[^\)]+\)'								# preparing regexp
			convertedSize = re.search(pattern, webSize).groups()[0].replace(",", "")	# finding size in bytes from string
			parsedFileWebInfo['size'] = unicode(convertedSize)				# convert file size to string

		parsedFileWebInfo['md5'] = parsedFileWebInfo['md5'].upper()			# getting checksum values to upper case (to avoid mismatches due to register)
		parsedFileWebInfo['name'] = parsedFileWebInfo['name'].upper()		# the file name is given to uppercase (to avoid mismatches due to register)
		parsedFileWebInfo['sha1'] = parsedFileWebInfo['sha1'].upper()
		parsedFileWebInfo['sha256'] = parsedFileWebInfo['sha256'].upper()
		#print parsedFileWebInfo											# output resulting dictionary to cmd for debugging (commented by default)
	else:																	# if url is not the same as we opened - there is no data in cloud.
		errorlog.write ('\nNo data in Cloud.')
		flag = 'false'														# flag signaling the presence file data in the cloud

	if flag != 'false':														# if flag is not 'false' proceed file properties comparison
		for keyName in parsedFileWebInfo:									# for all propreties in dictionare proceed
			if parsedLocalFileInfo[keyName] != parsedFileWebInfo[keyName]:	# are they equal?
				errorlog.write ("\n   Parameter Name: " + str(keyName))		# parameter mismatch
				errorlog.write ("\n      Cloud: " + parsedFileWebInfo[keyName].encode('utf-8','ignore'))		# mismatched value in cloud
				errorlog.write ("\n      Local: " + parsedLocalFileInfo[keyName].encode('utf-8','ignore'))		# mismatched value local
				errorcnt = errorcnt+1 										# local error counter increased
		globalerrorcnt = globalerrorcnt + errorcnt							# global error counter increased
		errorlog.write ('\nErrors found in file: ' + filename + ' : '+ str(errorcnt))	# file report to error log
		errorlog.write
errorlog.write ('\nErrors found global: ' + str(globalerrorcnt))			# global report to error log
errorlog.close()

# Show final messagebox to user with counters and inforamtion
tkMessageBox.showinfo(title="Checker Report", message="Files Checked: " + str(filescnt) + "\nErrors Found: " + str(globalerrorcnt) + "\nSee log.txt for errors")
