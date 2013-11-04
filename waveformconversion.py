#!/usr/bin/env python

"""
Helper to retrieve matlab waveform data into python.
"""
from datetime import (datetime, timedelta)
import numpy as np
import scipy.io as sio

class Waveform:
    def __init__(self):
        self.network = None
        self.station = None
        self.location = None
        self.channel = None
        self.sample_rate = 0
        self.start_time = datetime.now()
        self.data = np.empty(0)
        self.units = 'unknown'
        self.version = 0
        self.misc_fields = {}
        self.history = []
        
    def waveform2python(self,w, yn_to_tf=True):
            self.network = str(w.scnl.network)
            self.station = str(w.scnl.station)
            self.location = str(w.scnl.location)
            self.channel = str(w.scnl.channel)
            self.sample_rate = w.Fs
            ordinal_time = int(w.start)
            delta_time = ordinal_time - w.start
            self.start_time = datetime.fromordinal(ordinal_time) - timedelta(ordinal_time - w.start)
            self.data = w.data
            self.units = w.units
            self.version = 0
            self.misc_fields = dict(zip(w.misc_fields, w.misc_values))            
            if yn_to_tf:
                for mv in self.misc_fields:
                    try:
                        if self.misc_fields[mv].lower() in ('yes','no','true','false'):
                            self.misc_fields[mv] = self.misc_fields[mv] in ('yes','true')
                    except AttributeError:
                        pass
            self.history = []
            
    def __repr__(self):
        myrepr=[]
        myrepr.append("net: [%s], sta:[%s], loc:[%s], cha:[%s]" % (
            self.network, self.station, self.location, self.channel))
        myrepr.append("starting: [%s]" % self.start_time)
        myrepr.append("data: %d samples   ranging from [%f to %f]" % (
            len(self.data), min(self.data),max(self.data)))
        myrepr.append("units: %s" % self.units)
        if len(self.misc_fields):
            myrepr.append("with miscelleneous fields:")
            for miscfieldname, miscfieldvalue in self.misc_fields.items():
                myrepr.append('  ' + str(miscfieldname) + ': ' + str(miscfieldvalue))
        return '\n'.join(myrepr)
                       

        
    def create_from_mat(self,vnames=['rms_waveforms'],
                        matfilename="C:\Users\Celso\Desktop\RMS20030926.mat"):
        """ Return a dictionary of waveform lists. Each entry is a variable"""
        
        def is_waveform(an_item):
            try:
                return an_item[1].classname == 'waveform'
            except AttributeError:
                return False
        
        m = sio.loadmat(matfilename,mat_dtype=True,squeeze_me=True,
                        struct_as_record=False, variable_names=vnames)
        # optional: mdict = dictionary destination for results.m
        waveforms = dict([x for x in m.items() if is_waveform(x)])
        # print waveforms['rms_waveforms']
        
        self.waveform2python(waveforms['rms_waveforms'][0])
    