from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, permission_required

import plistlib
import os
import sys

class MunkiApplication:
	def __init__(self,name,item_des,display_name,url,license):
		self.name = name
		self.description = item_des
		self.display_name=display_name
		self.url=url
		self.license=license
	def __repr__(self):
		return repr((self.name,self.description))
	def getName(self):
		return self.name
	def display(self):
		return self.name,self.description

class MunkiApplicationRelease:
	def __init__(self,application,version,min,max,installer_location):
		self.app_object = application
		self.app_version = version
		self.min_os=min
		self.max_os=max
		self.location=installer_location
	def __repr__(self):
		return repr((self.app_object.name,self.app_version,self.min_os,self.max_os,self.location))
	def display(self):
		print "display",self.app_object.getName(),self.app_version
	def getName(self):
		return self.app_object.getName()	
	def getVersion(self):
		return self.app_version
	def getMinOS(self):
		return self.min_os
	def getMaxOS(self):
		return self.max_os
	def getAppLocations(self):
		return self.location
	def getReleseObject(self,app_name):
		for i in self.app_object:
			if app_name == i.getName():
				return i

class MunkiBranch:
	def __init__(self,name):
		self.name = name
		self.members=[]
	def __repr__(self):
		return repr((self.name,self.members))	
	def addAppToBranch(self,application):
		self.members.append(application)

	def list(self):
		print self.name
		for i in self.members:
			i.display()
	
	def getVersionsOfApp(self,app_name):
		return_list=[]
		for i in self.members:
			if app_name == i.getName():
				return_list.append(i.app_object)
		return return_list
	
	def getNameOfBranch(self):
		return self.name

	def getReleaseObject(self,app_name):
		for i in self.members:
			if app_name == i.getName():
				return i

@login_required
def index(request):
	path_prefix= settings.MUNKI_REPO_DIR
	# Read catalogue plist
	path_to_all_catalogue=os.path.join(path_prefix,"catalogs","all")
	if os.path.isfile(path_to_all_catalogue):
		all_catalogue=plistlib.readPlist(path_to_all_catalogue)
	else:
		all_catalogue=""
			
	# Read additional info plist
	file_with_additional_data="AppData.plist"
	path_to_current_script=os.path.dirname(__file__)
	try:
		additional_data=plistlib.readPlist(os.path.join(path_to_current_script,file_with_additional_data))
	except:
		additional_data=""
	
	
	##  Set global variables		
	branches=[MunkiBranch("dev"),MunkiBranch("testing"),MunkiBranch("production")]
	list_of_applications=[]
	list_of_releases=[]
	packageURLPrefix="http://osxpkg.internal.sanger.ac.uk/pkgs"
			
	# Get all the info out of the all catalogue and build the objects
	
	# Iterate through each application in the catalogue
	for item in all_catalogue:
		
		# Has this application been seen before?
		count=0
		for application in list_of_applications:
			if item['name'] == application.getName():
				count +=1
		# If this is a new application create an object for it
		if count ==0:
			if "description" in item.keys():
				item_description=item['description']
			else:
				item_description=""
			if "display_name" in item.keys():
				item_display=item["display_name"]
			else:
				item_display=item["name"]
			# Add in any additional info
			item_URL=""
			item_license=""
			for row in additional_data:
				if item["name"] == row["installerName"]:
					item_URL=row["downloadURL"]
					item_license=row["license"]
					
	
				
			application_object = MunkiApplication(item['name'],item_description,item_display,item_URL,item_license)
			list_of_applications.append(application_object)
		# otherwise, find the existing one
		else:
			for i in list_of_applications:
				if i.name == item['name']:
					application_object = i
			
			
					
		# Create an object for this release
		
		if "minimum_os_version" in item.keys():
			min_os_version=item["minimum_os_version"]
		else:
			min_os_version=""

		if "maximum_os_version" in item.keys():
			max_os_version=item["maximum_os_version"]
		else:
			max_os_version=""

		
		release_object = MunkiApplicationRelease(application_object,item['version'],min_os_version,max_os_version,item['installer_item_location'])
		list_of_releases.append(release_object)
	
		# Iterate through each catalog on this item
		for catalog in item['catalogs']:
			# Iterate through each branch and see if the item belongs there
			for branch in branches:
				if catalog == branch.getNameOfBranch():
					branch.addAppToBranch(release_object)
	
	# Prepare it for display
	big_old_list_for_display=[]
	# Sort the list of applications alphabetically 
	for row_app in sorted(list_of_applications, key=lambda MunkiApplication: MunkiApplication.display_name.lower()):
		row={}
		# Get the general common information about the application
		row["app_object"]=row_app
		for branch in branches:
			# Go through each branch and add the versions in
			version_list=[]
			for member in branch.members:
				if member.app_object.name == row_app.name:
					version_list.append(member)
			
			
			row["{}".format(branch.name)]=version_list
	
		big_old_list_for_display.append(row)

	return render_to_response('matrix/index.html', {'entries': big_old_list_for_display,'branches': branches,'URLprefix':packageURLPrefix})