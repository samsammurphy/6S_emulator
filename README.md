### What is this repo about?

It is about atmospheric correction of satellite images. The aim is to help you convert from:

radiance -> surface reflectance

### How does it work?

This project is written in Python. We use the [6S](link) radiative transfer code through a Python wrapper called [Py6S](link). 

We build [interpolated look up tables (iLUTs)](link) to get the parameter values we need to convert from [at-sensor radiance to surface reflectance](link).

### Why is this important?

Radiative transfer code (e.g. 6S, MODTRAN, etc.) take a [long time](link) to execute. The *standard* solution is to use interpolated look up tables (refs). We have built one for 6S.

### What about MODTRAN?

6S compares well, slight edge, free and open-source




