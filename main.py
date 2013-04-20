#!/usr/bin/env python


import flyflipschedule


if __name__ == '__main__':

    CLIENT_SECRETS = 'client_secrets.json'
    STORAGEFILE = 'secrets_storage.dat'

    cal = flyflipschedule.GCalendar(CLIENT_SECRETS, STORAGEFILE)

    print cal.getflycalendarid()
