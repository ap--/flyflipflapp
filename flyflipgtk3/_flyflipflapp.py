#!/usr/bin/env python
#

import yaml

from gi.repository import Gtk, GLib, GObject, Gdk

import datetime

import os
import inspect

GObject.threads_init()
Gdk.threads_init()


def fprnt(tube, temperature, date):
    print tube, u'  @%d\u00b0C' % temperature, date.strftime('# %Y-%m-%d %H:%M')


class Gtk3FlyFlipFlapp(object):


    def __init__(self, 
            parsefunc=fprnt,
            allelesconf='../alleles.yaml', timefmt='%Y-%m-%d %H:%M'):

        self._parsefunc = parsefunc
        self.ALLELESCONF = allelesconf
        self.TIMEFMT = timefmt

        # GTK3 stuff
        b = Gtk.Builder()
        PATH = os.path.dirname(inspect.getfile(Gtk3FlyFlipFlapp))
        guifile = os.path.join(PATH, 'main.ui')
        b.add_from_file(guifile)
        b.connect_signals(self)
        self.w = b.get_object("window1")
        
        # get Buttons
        self._button_now = b.get_object("nowbutton")
        self._button_add = b.get_object("addbutton")
        self._button_clear = b.get_object("clearbutton")
        
        # get fly grids
        self._grid_fly0 = b.get_object("fly0grid")
        self._grid_fly1 = b.get_object("fly1grid")

        # get type selector and dateentry
        self._cbox_tubetype = b.get_object("tubetypecbox")
        self._cbox_temp = b.get_object("flytemp")
        self._entry_date = b.get_object("dateentry")
        
        # get fly0 stuff
        self._fly0_hc2 = b.get_object("fly0hc2")
        self._fly0_hc3 = b.get_object("fly0hc3")
        self._fly0_c1a = b.get_object("fly0c1a")
        self._fly0_c2a = b.get_object("fly0c2a")
        self._fly0_c2b = b.get_object("fly0c2b")
        self._fly0_c3a = b.get_object("fly0c3a")
        self._fly0_c3b = b.get_object("fly0c3b")
        self._fly0_gen = b.get_object("fly0gender") 
        self._fly1_gen = b.get_object("fly1gender") 
        
        # get fly1 stuff
        self._fly1_hc2 = b.get_object("fly1hc2")
        self._fly1_hc3 = b.get_object("fly1hc3")
        self._fly1_c1a = b.get_object("fly1c1a")
        self._fly1_c2a = b.get_object("fly1c2a")
        self._fly1_c2b = b.get_object("fly1c2b")
        self._fly1_c3a = b.get_object("fly1c3a")
        self._fly1_c3b = b.get_object("fly1c3b")
       
        # connect all signals:
        self.w.connect("delete-event", self._request_close)

        self._fly0_hc2.connect("clicked", self._changed_homozygous, '_fly0_c2')
        self._fly0_hc3.connect("clicked", self._changed_homozygous, '_fly0_c3')
        self._fly1_hc2.connect("clicked", self._changed_homozygous, '_fly1_c2')
        self._fly1_hc3.connect("clicked", self._changed_homozygous, '_fly1_c3')

        self._fly0_c2a.connect("changed", self._changed_allele, self._fly0_c2b)
        self._fly0_c3a.connect("changed", self._changed_allele, self._fly0_c3b)
        self._fly1_c2a.connect("changed", self._changed_allele, self._fly1_c2b)
        self._fly1_c3a.connect("changed", self._changed_allele, self._fly1_c3b)

        self._cbox_tubetype.connect("changed", self._changed_tubetype)

        self._entry_date.connect("changed", self._changed_date)

        self._button_now.connect("clicked", self._clicked_now, self._entry_date)
        self._button_clear.connect("clicked", self._clicked_clear)
        self._button_add.connect("clicked", self.parse)

        self._grid_fly0.set_sensitive(False)
        self._grid_fly1.set_sensitive(False)

        self._setup_alleles(self.ALLELESCONF)
        self._setup_genders()
        # done
        self.w.show_all()


    def _changed_homozygous(self, checkbutton, cbn):
        MODC1 = not checkbutton.get_active()
        cNa, cNb = self.__getattribute__(cbn+'a'), self.__getattribute__(cbn+'b')
        cNb.set_active(cNa.get_active())
        cNb.set_sensitive(MODC1)
        return True


    def _changed_tubetype(self, combobox):
        typ = combobox.get_model().get_value(combobox.get_active_iter(),0)
        if typ == 'Stock':
            self._grid_fly0.set_sensitive(True)
            self._grid_fly1.set_sensitive(False)
        elif typ == 'Cross':
            self._grid_fly0.set_sensitive(True)
            self._grid_fly1.set_sensitive(True)
        return True

    
    def _changed_allele(self, cNa, cNb):
        if not cNb.get_sensitive():
            cNb.set_active(cNa.get_active())
        return True


    def _changed_date(self, entry):
        string = entry.get_text()
        try:
            datetime.datetime.strptime(string.strip(), self.TIMEFMT)
        except ValueError:
            entry.set_icon_from_stock(
                    Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_DIALOG_ERROR)
        else:
            entry.set_icon_from_stock(
                    Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_APPLY)
        return True


    def _clicked_now(self, button, entry):
        t = datetime.datetime.now().strftime(self.TIMEFMT)
        entry.set_text(t)
        return True


    def _clicked_clear(self, button, fly=-1):
        HC0 = [self._fly0_hc2, self._fly0_hc3,
               self._fly0_c1a, self._fly0_c2a,
               self._fly0_c2b, self._fly0_c3a,
               self._fly0_c3b, self._fly0_gen]
        HC1 = [self._fly1_hc2, self._fly1_hc3,
               self._fly1_c1a, self._fly1_c2a,
               self._fly1_c2b, self._fly1_c3a,
               self._fly1_c3b, self._fly1_gen]
        if fly < 0 or fly == 0:
            for h in HC0:
                h.set_active(0)
        if fly < 0 or fly == 1:
            for h in HC1:
                h.set_active(0)
        return True


    def _setup_alleles(self, configfile):
        alleles = yaml.load(open(configfile,'r'))
        C1 = [self._fly0_c1a, self._fly1_c1a]
        C2 = [self._fly0_c2a, self._fly0_c2b, self._fly1_c2a, self._fly1_c2b]
        C3 = [self._fly0_c3a, self._fly0_c3b, self._fly1_c3a, self._fly1_c3b]
        KS = ['chromosome1', 'chromosome2', 'chromosome3']
        for k, cbs in zip(KS, [C1, C2, C3]):
            ls = Gtk.ListStore(str)
            cell = Gtk.CellRendererText()
            for allele in alleles[k]:
                ls.append([allele])
            for cb in cbs:
                cb.set_model(ls)
                cb.set_active(0)
                cb.pack_start(cell, True)
                cb.add_attribute(cell, "text", 0)
        return         


    def _setup_genders(self):
        ls = Gtk.ListStore(str)
        ls.append([u' '])
        ls.append([u'\u2640'])
        ls.append([u'\u2642'])
        ls.append([u'\u263f'])
        cell = Gtk.CellRendererText()
        for cb in [self._fly0_gen, self._fly1_gen]:
            cb.set_model(ls)
            cb.set_active(0)
            cb.pack_start(cell, True)
            cb.add_attribute(cell, "text", 0)
        return

    
    def _is_date_valid(self):
        ICON = self._entry_date.get_icon_stock(Gtk.EntryIconPosition.PRIMARY)
        return ICON == Gtk.STOCK_APPLY    


    def _get_fly_string(self, index):
        def get_text(fly, cbi):
            cb = self.__getattribute__('_fly%d_%s' % (fly, cbi))
            return cb.get_model().get_value(cb.get_active_iter(),0)
        s = '; %s / %s ; %s / %s ;' % (get_text(index,'c2a'), 
                                       get_text(index,'c2b'),
                                       get_text(index,'c3a'),
                                       get_text(index,'c3b'))
        c1 = get_text(index,'c1a')             
        g = get_text(index, 'gen')
        if c1.strip():
            s = '%s %s' % (c1, s)
        if g.strip():
            s = '%s %s' % (s, g)
        return s


    def parse(self, *args):
        if self._is_date_valid():
            dat = self._entry_date.get_text()
            dat = datetime.datetime.strptime(dat.strip(), self.TIMEFMT)
            tmp = int(self._cbox_temp.get_model().get_value(
                            self._cbox_temp.get_active_iter(),0))
            typ = self._cbox_tubetype.get_model().get_value(
                            self._cbox_tubetype.get_active_iter(),0)
            if typ == 'Stock':
                self._parsefunc(self._get_fly_string(0), tmp, dat)
            elif typ == 'Cross':
                self._parsefunc('%s XXX %s' % (self._get_fly_string(0),
                                self._get_fly_string(1)), tmp, dat)
        

    def _request_close(self, *args):
        Gtk.main_quit()


    def start(self):
        Gtk.main()


if __name__ == "__main__":

    u = Gtk3FlyFlipFlapp()
    u.start()
