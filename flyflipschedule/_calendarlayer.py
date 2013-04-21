# -*- coding: utf-8 -*-

import httplib2
import sys

import apiclient.discovery
import oauth2client.client
import oauth2client.file
import oauth2client.tools

import datetime


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
               'timeZone'    : self.FCTIMEZONE,
               'reminders'   : {'useDefault' : False},
               'defaultReminders' : []}
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


    def addflyevent(self, type_, shortid, longid, temperature, date):
        start = date
        

        if type_ == 'stock':
            if temperature == 25:
                rec = u'RRULE:FREQ=DAILY;INTERVAL=14'
                end = start + datetime.timedelta(days=14)
            elif temperature == 18:
                rec = u'RRULE:FREQ=DAILY;INTERVAL=28'
                end = start + datetime.timedelta(days=28)
            else:
                raise Exception('unkown temperature')
            start = start.strftime('%Y-%m-%d')
            end = end.strftime('%Y-%m-%d')

            event = {
                'summary': 'Stock %s' % shortid,
                'start': { 'date': start,
                           'timeZone': self.FCTIMEZONE },
                'end': { 'date': end,
                         'timeZone': self.FCTIMEZONE },
                'description' : '%s %dC' % (longid, temperature),
                'recurrence' : [rec],
                'location' : 'Vienna',
                'reminders' : { 'useDefault' : False,
                                'overrides' : [{'method' : 'email',
                                                'minutes': 24*60, }],
                              },
                    }
            if self._debug > 0: print '> adding stock %s' % shortid
            self.service.events().insert(calendarId=self.calendarId,
                                         body=event).execute()
        elif type_ == 'cross':
            if temperature == 25:
                # should hatch after 10 days
                end = start + datetime.timedelta(days=14)
                flip = start + datetime.timedelta(days=1)
                vc = start + datetime.timedelta(days=12, hours=23)
            elif temperature == 18:
                # should hatch after 20 days
                end = start + datetime.timedelta(days=24)
                flip = start + datetime.timedelta(days=1)
                vc = start + datetime.timedelta(days=24, hours=23)
            else:
                raise Exception('unkown temperature')
            # Cross event
            start = start.strftime('%Y-%m-%d')
            end = end.strftime('%Y-%m-%d')
            event = {
                'summary': 'Cross %s' % shortid,
                'start': { 'date': start,
                           'timeZone': self.FCTIMEZONE },
                'end': { 'date': end,
                         'timeZone': self.FCTIMEZONE },
                'description' : '%s %dC' % (longid, temperature),
                'location' : 'Vienna',
                    }
            if self._debug > 0: print '> adding cross %s' % shortid
            self.service.events().insert(calendarId=self.calendarId,
                                         body=event).execute()
            # collect virgins starting at day ten
            event = {
                'summary': 'VIRGINS Cross %s' % shortid,
                'start': { 'dateTime': vc.strftime('%Y-%m-%dT23:00:00'),
                           'timeZone': self.FCTIMEZONE },
                'end': { 'dateTime': vc.strftime('%Y-%m-%dT23:05:00'),
                         'timeZone': self.FCTIMEZONE },
                'description' : 'VIRGINS %s %dC' % (longid, temperature),
                'location' : 'Vienna',
                'reminders' : { 'useDefault' : False,
                                'overrides' : [{'method' : 'email',
                                                'minutes': 15*60, }, # day 14
                                               {'method' : 'email',
                                                'minutes': 39*60, }, # day 13
                                               {'method' : 'email',
                                                'minutes': 63*60, }, # day 12
                                               {'method' : 'email',
                                                'minutes': 87*60, }, # day 11
                                              ],
                              },
                    }
            self.service.events().insert(calendarId=self.calendarId,
                                         body=event).execute()

            # cross flip after day one
            event = {
                'summary': 'FLIP Cross %s' % shortid,
                'start': { 'dateTime': flip.strftime('%Y-%m-%dT23:00:00'),
                           'timeZone': self.FCTIMEZONE },
                'end': { 'dateTime': flip.strftime('%Y-%m-%dT23:05:00'),
                         'timeZone': self.FCTIMEZONE },
                'description' : 'FLIP %s %dC' % (longid, temperature),
                'location' : 'Vienna',
                'reminders' : { 'useDefault' : False,
                                'overrides' : [{'method' : 'email',
                                                'minutes': 15*60, }],
                              },
                    }
            self.service.events().insert(calendarId=self.calendarId,
                                         body=event).execute()
        else:
            raise Exception('type needs to be stock or cross')






