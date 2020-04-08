"""
Script to create a zooniverse project and upload local images

Note:
Before you run the script, you should run

    pip install panoptes_client

and then you are ready to upload the images with

    python upload_images.py

It's easiest to do in a python2 environment!

Please make sure, you adapted the lines of code
under '# Setup'
"""


import glob
from panoptes_client import Panoptes, Project, SubjectSet, Subject
import tqdm

# Setup
# path1 = '../source_images/EUREC4A_VIS_workflow/EUREC4A_MODIS_AQUA-VIS/'
# path2 = '../source_images/EUREC4A_VIS_workflow/EUREC4A_MODIS_TERRA-VIS/'
# path3 = '../source_images/EUREC4A_VIS_workflow/GOES16_C02/'

path1 = '../source_images/EUREC4A_ICON_alb_workflow/'
username = ''  # Zooniverse username
password = ''  # Zooniverse password
display_name = 'Sugar, flower, fish or gravel'
description = 'Shallow clouds are the nemesis of climate modelers. Help us by detecting cloud organization from satellite images.'
subject_name = 'EUREC4A-ICON-Scenes'

# Read filenames to upload
# import pdb; pdb.set_trace()
# files = sorted(glob.glob(path1+'*.jpeg'))
# files = files + sorted(glob.glob(path2+'*.jpeg'))
# files = files + sorted(glob.glob(path3+'*C02*.jpeg'))
files = sorted(glob.glob(path1+'*[02468]??.jpeg'))

# Create metadata
subject_metadata = {}
for f, file in enumerate(files):
	subject_metadata[file] = {'file': file, 'subject_reference': f}


Panoptes.connect(username=username, password=password)
# tutorial_project = Project()
tutorial_project = Project.find(7699)
# tutorial_project.display_name = display_name
# tutorial_project.description = description
# tutorial_project.primary_language = 'en'
# tutorial_project.private =True
# tutorial_project.save()

subject_set = SubjectSet()
subject_set.links.project = tutorial_project
subject_set.display_name = subject_name
subject_set.save()

tutorial_project.reload()
print(tutorial_project.links.subject_sets)

new_subjects = []
for filename, metadata in tqdm.tqdm(subject_metadata.items()):
	subject = Subject()
	subject.links.project = tutorial_project
	subject.add_location(filename)
	subject.metadata.update(metadata)
	subject.save()
	new_subjects.append(subject)

subject_set.add(new_subjects)