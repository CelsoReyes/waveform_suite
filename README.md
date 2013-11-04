waveform_suite
==============

The Waveform Suite for Matlab is getting long in the tooth and could use a refresh. Here it is.


waveformconverter.py
====================
allows the "easy" conversion from MATLAB waveform-suite objects into ObsPy.
Currently, this is a one-way trip

While this module is still under construction, At its most rudimentary level, it already works.

To get waveforms from a .mat file....
    >>> w = loadmatwaveforms("somewave.mat")

So, assume a file was saved from matlab...
```matlab
> mywaveforms = [waveform(), waveform(), waveform()];
> differentwave = [waveform];
> some_other_variable = 3;
> save mystuff
```

Then
    >>> w = loadmatwaveforms("mystuff.mat")
will return w as a dictionary...
    w['mywaveforms']= <osbpy.core.stream.Stream>  # containing 3 individual Traces
    w['otherwave'] = <obspy.core.stream.Stream> #containing 1 Trace