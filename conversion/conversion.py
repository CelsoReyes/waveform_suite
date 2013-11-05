#!/usr/bin/env python

"""
Helper to retrieve matlab waveform data into python.

Use this module to convert MATLAB waveform suite files into Obspy

For example,

>>> w = loadmatwaveforms('/Users/celsoreyes/github/waveform_suite/conversion/tests/data/sample_envelope_waveforms.mat')
>>> print(w['rms_waveforms'])
7 Trace(s) in Stream:
--.OKCF.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T23:59:40.010008Z | 0.1 Hz, 8639 samples
--.OKID.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T11:59:50.010008Z | 0.1 Hz, 4320 samples
--.OKRE.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T23:59:40.010008Z | 0.1 Hz, 8639 samples
--.OKSP.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T23:59:40.010008Z | 0.1 Hz, 8639 samples
--.OKTU.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T23:59:40.010008Z | 0.1 Hz, 8639 samples
--.OKWE.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T23:59:40.010008Z | 0.1 Hz, 8639 samples
--.OKWR.--.SHZ | 2004-06-12T00:00:00.010008Z - 2004-06-12T23:59:40.010008Z | 0.1 Hz, 8639 samples
"""
from datetime import (datetime, timedelta)
import numpy as np
import scipy.io as sio
from obspy.core.trace import Trace
from obspy.core.stream import Stream


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
        misc_fields = dict()
        if 'CALIB' in self.misc_fields:
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
            self.starttime = (datetime.fromordinal(ordinal_time) -
                              timedelta(ordinal_time - w.start))
            self.data = w.data
            self.units = w.units
            self.version = 0
            self.misc_fields = dict(zip(w.misc_fields, w.misc_values))
            word_to_bool = {'true': True, 'yes': True,
                            'false': False, 'no': False}
            if yn_to_tf:
                for k, v in self.misc_fields.items():
                    try:
                        if v in word_to_bool:
                            self.misc_fields[k] = word_to_bool[v]
                    except AttributeError:
                        pass
            self.history = []
            return self  # for chaining. feels kludgy

    def __repr__(self):
        myrepr = []
        myrepr.append("net: [%s], sta:[%s], loc:[%s], cha:[%s]" % (
            self.network, self.station, self.location, self.channel))
        myrepr.append("starting: [%s]" % self.starttime)
        myrepr.append("data: %d samples   ranging from [%f to %f]" % (
            len(self.data), min(self.data), max(self.data)))
        myrepr.append("units: %s" % self.units)
        if len(self.misc_fields):
            myrepr.append("with miscelleneous fields:")
            for miscfieldname, miscfieldvalue in self.misc_fields.items():
                myrepr.append('  ' + str(miscfieldname) + ': ' +
                              str(miscfieldvalue))
        return '\n'.join(myrepr)


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

    m = sio.loadmat(matfilename, mat_dtype=True, squeeze_me=True,
                    struct_as_record=False, variable_names=vnames)
    loaded_waveforms = dict([x for x in m.items() if is_waveform(x)])
    result = {}
    for vname in loaded_waveforms:
        w = Waveform()
        result[vname] = Stream([w.waveform2python(one_waveform).python2obspy()
                                for one_waveform in loaded_waveforms[vname]])
    return result

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
