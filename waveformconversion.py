#!/usr/bin/env python

"""
Helper to retrieve matlab waveform data into python.
"""
from datetime import (datetime, timedelta)
import numpy as np
import scipy.io as sio
from obspy.core.trace import Trace
import obspy.core.stream as obsstream

class Waveform:
    def __init__(self, matlabfile=None, matlabvariable=None):
        if matlabfile:
             self.create_from_mat(vnames=matlabvariable,
                        matfilename=matlabfile)
             return
        self.network = None
        self.station = None
        self.location = None
        self.channel = None
        self.sampling_rate = 0.0
        self.starttime = datetime.now()
        self.data = np.empty(0)
        self.units = 'unknown'
        self.version = 0
        self.misc_fields = {}
        self.history = []
        
    def python2obspy(self):
        from obspy.core.trace import Stats, Trace
        from obspy.core.utcdatetime import UTCDateTime
        s = Stats()
        s.network = self.network
        s.station = self.station
        s.location = self.location
        s.channel = self.channel
        s.sampling_rate = self.sampling_rate
        s.starttime = UTCDateTime(self.starttime)
        s.npts = len(self.data)
        misc_fields=dict()
        if self.misc_fields.has_key('CALIB'):
            s.calib = self.misc_fields.pop('CALIB')
        s.update(self.misc_fields)
        return Trace(self.data[:], header=s)    
        
    def waveform2python(self, w, yn_to_tf=True):
            self.network = str(w.scnl.network)
            self.station = str(w.scnl.station)
            self.location = str(w.scnl.location)
            self.channel = str(w.scnl.channel)
            self.sampling_rate = w.Fs
            ordinal_time = int(w.start)
            delta_time = ordinal_time - w.start
            self.starttime = datetime.fromordinal(ordinal_time) - timedelta(ordinal_time - w.start)
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
            return self # for chaining
            
    def __repr__(self):
        myrepr=[]
        myrepr.append("net: [%s], sta:[%s], loc:[%s], cha:[%s]" % (
            self.network, self.station, self.location, self.channel))
        myrepr.append("starting: [%s]" % self.starttime)
        myrepr.append("data: %d samples   ranging from [%f to %f]" % (
            len(self.data), min(self.data),max(self.data)))
        myrepr.append("units: %s" % self.units)
        if len(self.misc_fields):
            myrepr.append("with miscelleneous fields:")
            for miscfieldname, miscfieldvalue in self.misc_fields.items():
                myrepr.append('  ' + str(miscfieldname) + ': ' + str(miscfieldvalue))
        return '\n'.join(myrepr)
                       

    '''    
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
    '''
    
def loadmatwaveforms(matfilename=None, vnames=None):
    """ load from a file into a dictionary of obspy streams
    
    specify specific variable with vnames
    results are returned with keys as variable names
    """
    def is_waveform(an_item):
        try:
            return an_item[1].classname == 'waveform'
        except AttributeError:
            return False
        
    m = sio.loadmat(matfilename,mat_dtype=True,squeeze_me=True,
                        struct_as_record=False, variable_names=vnames)
    loaded_waveforms = dict([x for x in m.items() if is_waveform(x)])
    result={}
    for vname in  loaded_waveforms:
        #for one_waveform in loaded_waveforms[vname]:
           # print one_waveform
        w = Waveform()
        result[vname] = obsstream.Stream([w.waveform2python(one_waveform).python2obspy() for one_waveform in loaded_waveforms[vname] ])
        # print result[vname]
    return result
    
w = loadmatwaveforms("C:\Users\Celso\Desktop\RMS20030926.mat")
obsw={}
print w
for k in w:
    print k
    w[k].plot()
    for t in w[k]:
        print(t)
    
    
    
    