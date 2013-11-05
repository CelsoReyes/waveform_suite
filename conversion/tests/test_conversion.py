#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The waveform_suite.conversion test suite.
"""
import unittest
import os


class ConversionTestCase(unittest.TestCase):
    """
    Test cases for waveform_suite.conversion
    """
    def setUp(self):
        # directory where the test files are located
        self.path = os.path.dirname(__file__)
        self.datapath = os.path.join(self.path, "data")

    def loaddata_test(self):
        """Test the loading of data"""
        filename = "sample_envelope_waveforms.mat"
        file_ = os.path.join(self.datapath, filename)
        w = loadmatwaveforms(file_)
        obsw = {}
        print w
        for k in w:
            print k
            w[k].plot()
            for t in w[k]:
                print(t)

    def failing_test(self):
        assert (0 == 1)


def suite():
    return unittest.makeSuite(ConversionTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
