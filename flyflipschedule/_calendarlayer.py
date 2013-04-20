# -*- coding: utf-8 -*-

import httplib2
import sys

import apiclient.discovery
import oauth2client.client
import oauth2client.file
import oauth2client.tools


class GCalendar(object):
        
    FCSUMMARY = 'flyflip schedule'
    FCDESCRIPTION = 'scheduled flywork'
    FCTIMEZONE = 'Europe/Vienna'

    def __init__(self, client_secrets, storagefile, debug=False):
        self._debug = int(debug)
        self._credentials = self._getcredentials(client_secrets, storagefile)
        http = self._credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('calendar', 'v3', http=http)
    
        self.calendarId = self.getflycalendarid()


    def _getcredentials(self, secrets, store):
        if self._debug > 1: print '> creating credentials'
        storage = oauth2client.file.Storage(store)
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = oauth2client.tools.run(self._flow(secrets), storage)
        return credentials


    def _flow(self, secrets):
        flow = oauth2client.client.flow_from_clientsecrets(
                secrets, scope=['https://www.googleapis.com/auth/calendar'],
                message='provide secrets')
        return flow


    def _findflycalendarid(self):
        if self._debug > 0: print '> searching flycalendar'
        page_token=None
        while True:
            clist = self.service.calendarList().list(pageToken=page_token).execute()
            if clist['items']:
                for clist_entry in clist['items']:
                    if clist_entry['summary'] == self.FCSUMMARY:
                        return clist_entry['id']
            page_token = clist.get('nextPageToken')
            if not page_token:
                return None


    def _addflycalendar(self):
        if self._debug > 0: print '> adding flycalendar'
        cl = { 'summary'     : self.FCSUMMARY,
               'description' : self.FCDESCRIPTION,
               'timeZone'    : self.FCTIMEZONE }
        ret = self.service.calendars().insert(body=cl).execute()
        return ret['id']


    def getflycalendarid(self):
        _id = self._findflycalendarid()
        if _id is None:
            _id = self._addflycalendar()
        return _id


    def iterflyevents(self):
        page_token = None
        while True:
            events = self.service.events().list(calendarId=self.calendarId,
                                                pageToken=page_token).execute()
            try:
                events['items']
            except KeyError:
                return
            if events['items']:
                for event in events['items']:
                    yield event
            page_token = events.get('nextPageToken')
            if not page_token:
                return








