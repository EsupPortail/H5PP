##
# Makes it easy to track events throughout the H5P system
##
from django.db.models import F
from h5pp.models import h5p_events, h5p_counters
import time


class H5PEvent:
    LOG_NONE = 0
    LOG_ALL = 1
    LOG_ACTIONS = 2

    log_level = LOG_ACTIONS
    log_time = 2592000  # 30 days

    def __init__(self, user, typ, sub_type=None, content_id=None, content_title=None, library_name=None, library_version=None):
        self.user = user
        self.typ = typ
        self.sub_type = sub_type
        self.content_id = content_id
        self.content_title = content_title
        self.library_name = library_name
        self.library_version = library_version
        self.time = int(time.time())

        if self.validLogLevel(typ, sub_type):
            self.save(self.user)

        if self.validStats(typ, sub_type):
            self.saveStats()

    ##
    # Determines if the event type should be saved/logged
    ##
    def validLogLevel(self, typ, sub_type):
        if self.log_level == 'LOG_NONE':
            return False
        elif self.log_level == 'LOG_ALL':
            return True
        else:
            if self.isAction(typ, sub_type):
                return True
            return False

    ##
    # Check if the event should be included in the statistics counter
    ##
    def validStats(self, typ, sub_type):
        if (typ == 'content' and sub_type == 'shortcode insert') or (typ == 'library' and sub_type == None) or (typ == 'results' and sub_type == 'content'):
            return True
        elif self.isAction(typ, sub_type):
            return True
        return False

    ##
    # Check if event type is an action
    ##
    def isAction(self, typ, sub_type):
        if (typ == 'content' and sub_type in ['create', 'create upload', 'update', 'update upload', 'upgrade', 'delete'] or typ == 'library' and sub_type in ['create', 'update']):
            return True
        return False

    ##
    # A helper which makes it easier for systems to have the data
    # Add all relevant properties to a assoc, array
    # There are no NONE values. Empty string or 0 is used instead
    ##
    def getDataArray(self):
        return {
            'created_at': self.time,
            'type': self.typ,
            'sub_type': '' if not self.sub_type else self.sub_type,
            'content_id': 0 if not self.content_id else self.content_id,
            'content_title': '' if not self.content_title else self.content_title,
            'library_name': '' if not self.library_name else self.library_name,
            'library_version': '' if not self.library_version else self.library_version
        }

    ##
    # Stores the event data in the database
    ##
    def save(self, user):

        # Get data in array format without NONE values
        data = self.getDataArray()

        # Add user
        data['user_id'] = user.id

        # Insert into DB
        self.pid = h5p_events.objects.create(**data)

        return self.pid.id

    ##
    # Add current event data to statistics counter
    ##
    def saveStats(self):
        atype = self.typ + ' ' + self.sub_type

        # Verify if counter exists
        currentNum = h5p_counters.objects.filter(
            type=atype, library_name=self.library_name, library_version=self.library_version).values('num')

        if not currentNum.exists():
            # Insert new counter
            h5p_counters.objects.create(
                type=atype, library_name=self.library_name, library_version=self.library_version, num=1)
        else:
            # Update counter with num+1
            counter = h5p_counters.objects.get(
                type=atype, library_name=self.library_name, library_version=self.library_version)
            counter.num = F('num') + 1
            counter.save()
