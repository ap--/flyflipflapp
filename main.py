#!/usr/bin/env python


import flyflipschedule
import flyfliputils

import datetime


testset = [ ('; FOO-Baz ;;', 25, datetime.datetime.today()),
            ('; FOO-Baz ;; \u2642 XXX ; BAR-Foo ;; \u263f', 25, datetime.datetime.today()) ]


if __name__ == '__main__':

    import sys


    CLIENT_SECRETS = 'client_secrets.json'
    STORAGEFILE = 'secrets_storage.dat'

    cal = flyflipschedule.GCalendar(CLIENT_SECRETS, STORAGEFILE, debug=2)

    print cal.getflycalendarid()

    for event in cal.iterflyevents():
        for k,v in event.iteritems():
            print k, v
        print ''

    if sys.argv[-1] == 'add':
        for gt, temp, date in testset:
            tube = flyfliputils.flytuplefromgenotype(gt) + (temp, date,)
            cal.addflyevent(*tube)    

    


