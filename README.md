## Atmospheric Correction using Python

The goal is to help you convert at-sensor radiance to surface reflectance. 

The code runs the 6S radiative transfer code in Fortran under the hood. The 6S code was adopted by NASA and USGS for their surface reflectance products for both the Landsat and MODIS missions. It can be used to correct any satellite imagery between 0.4 - 4 microns.

Interaction with 6S is achieved through a Python wrapper called [Py6S](http://py6s.readthedocs.io/en/latest/introduction.html). The wrapper supports all the functionality of the original 6S code (and more!)
 
A key contribution in this repo is the use of interpolated look-up tables (iLUTs) to speed up Py6S.


### What are iLUTs? 


It helps to first consider a normal lookup table (LUT). We could run Py6S a whole bunch of times and record both the input and output values in a LUT. Then, later on, we could use a given set of input values to rapidly look up the output values. The problem with this is that the input and output values are limited to discrete values but in real life they are continuous. After creating a LUT we therefore interpolate it in n-dimensional space so that we can use continuous inputs and to get continuous outputs.

### How do I use an iLUT?

The iLUTs are 'interpolator objects' which take in the following input:

* solar zenith angle (degrees)
* water vapour column (g/cm^2)
* ozone column (atm-cm)
* aerosol optical thickness
* altitude (km)

and provide the following output

* direct solar irradiance (Edir)
* diffuse solar irradiance (Edif)
* transmissivity from surface to sensor (tau2)
* path radiance (Lp)

You can use an iLUT in Python like this:

```
In [1] Edir, Edif, tau2, Lp = iLUT(solar_z,H2O,O3,AOT,alt)
```

### How do I calculate surface reflectance?

surface reflectance (rho) can be calculated from at-sensor radiance (L) using this equation:

rho = pi * (L - Lp) / tau2 * (Edir + Edif)



