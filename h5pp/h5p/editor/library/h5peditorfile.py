from django.conf import settings
from PIL import Image
import json
import uuid
import os
import re


class H5PEditorFile:

    global name
    name = None

    ##
    # Constructor. Process data for file uploaded through the editor
    ##
    def __init__(self, request, files, framework):
        if not 'field' in request.POST or request.POST['field'] == None:
            return

        field = request.POST['field']

        self.interface = framework
        self.result = dict()
        self.field = json.loads(field)
        self.files = files['file']
        self.path = os.path.join(settings.MEDIA_ROOT, 'h5pp', 'tmp', self.files.name)

        # Check if uploaded base64 encoded file
        if 'dataURI' in request.POST and request.POST['dataURI'] != '':
            data = request.POST['dataURI']

            # Extract data from string
            (typ, data) = data.split(';')
            (_, data) = data.split(',')
            self.data = data.decode('base64')

            # Extract file type and extension
            (_, typ) = typ.split(':')
            (_, extension) = typ.split('/')
            self.typ = typ
            self.extension = extension
            self.size = len(self.data)
        else:
            # Handle temporarily uploaded form file
            self.typ = self.files.content_type.split('/')[0]
            self.extension = os.path.splitext(self.files.name)[1]
            self.size = self.files.size

    ##
    # Indicates if an uploaded file was found or not
    ##
    def isLoaded(self):
        return isinstance(self.result, dict)

    ##
    # Check current file up agains mimes types and extensions in the given list
    ##
    def check(self, mimes):
        ext = self.extension.lower().replace('.', '')
        for mime, extension in mimes.iteritems():
            if isinstance(extension, list):
                # Multiple extensions
                if ext in extension:
                    self.typ = mime
                    return True
            elif ext == extension:
                self.typ = mime
                return True

        return False

    ##
    # Validate the file
    ##
    def validate(self):
        if 'error' in self.result:
            return False

        # Check for field type
        if not 'type' in self.field:
            print('Unable to get field type')
            return False

        # Check if mime type is allowed
        if ('mimes' in self.field and not self.typ in self.field['mimes']) or self.extension[0:3] == 'py':
            print('File type isn\'t allowed')
            return False

        # Type specific validations
        if self.field['type'] == 'image':
            allowed = {
                'image/png': 'png',
                'image/jpeg': ['jpg', 'jpeg'],
                'image/gif': 'gif'
            }
            if not self.check(allowed):
                print('Invalid image file format. Use jpg, png or gif')
                return False

            # Get image size from base64 string
            if 'data' in locals() or 'data' in globals():
                image = Image.open(self.data)
            else:
                with open(self.path, 'w+') as f:
                    f.write(self.files.read())
                # Image size from tmp file
                image = Image.open(self.path)

            if not image:
                print('File is not an image')
                return False

            self.result['width'], self.result['height'] = image.size
            self.result['mime'] = self.typ

        elif self.field['type'] == 'audio':
            allowed = {
                'audio/mpeg': 'mp3',
                'audio/mp3': 'mp3',
                'audio/x-wav': 'wav',
                'audio/wav': 'wav',
                'audio/ogg': 'ogg'
            }
            if not self.check(allowed):
                print('Invalid audio file format. Use mp3 or wav')
                return False

            self.result['mime'] = self.typ

        elif self.field['type'] == 'video':
            allowed = {
                'video/mp4': 'mp4',
                'video/webm': 'webm',
                'video/ogg': 'ogv'
            }
            if not self.check(allowed):
                print('Invalid video file format. Use mp4 or webm')
                return False

            self.result['mime'] = self.typ

        elif self.field['type'] == 'file':
            self.result['mime'] = self.typ

        else:
            print('Invalid field type')
            return False

        return True

    ##
    # Get the type of the current file
    ##
    def getType(self):
        return self.field['type']

    ##
    # Get the name of the current file
    ##
    def getName(self):
        global name
        if name == None:
            name = str(uuid.uuid1())

            # Add extension to name
            if 'data' in locals() or 'data' in globals():
                name = name + self.extension
            else:
                matches = re.search('(?i)([a-z0-9]{1,})$', self.files.name)
                if matches.group(1):
                    name = name + '.' + matches.group(1)

        return name

    def getFile(self):
        return self.files
    ##
    # Get file data if created from string
    ##

    def getData(self):
        return None if not 'data' in locals() or 'data' in globals() else self.data

    ##
    # Print result from file processing
    ##
    def printResult(self):
        global name
        self.result['path'] = self.getType() + 's/' + self.getName()
        name = None
        return json.dumps(self.result)
