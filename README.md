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

surface reflectance (ref) can be calculated from at-sensor radiance (L) using this equation:

```
In [2] ref = (math.pi*(L-Lp))/(tau2*(Edir+Edif))
```


### Building a LUT

This repo comes with a few LUTs already for demonstration purposes. If you would like to a build a LUT from scratch here is the syntax:

```
$ python3 LUT_build.py {satellite_sensor} {aerosol_profile} {view_zenith} {--test,--full,--validation}
```

The options are:

* {satellite_sensor} = LANDSAT_TM, LANDSAT_ETM, LANDSAT_OLI or ASTER

* {aerosol_profile} = BB, CO, DE, MA, NO or UR

* {view_zenith} = integer value for view zenith of sensor in degrees (typically = 0)

* {--flags} = must pick one!

..where:

BB = BiomassBurning, CO = Continental, DE = Desert, MA = Maritime, NO = NoAerosols, UR = Urban

--full = Complete selection of input parameters. Outputs used in atmospheric correction. ***This might take several hours to execute*** (but you only need to do it once, ever).

--test = NOT for atmospheric correction, just for a 'quick' test

--validation = (advanced) a selection of input parameters that are used for validation

***EXAMPLE***: To create a lookup tabe not supplied here, e.g. for LANDSAT 8's OLI sensor using an urban aerosol model, you could run the following command:

```
$ python3 LUT_build.py LANDSAT_OLI UR 0 --test
```

### Interpolating a LUT

The general syntax is:

```
$ python3 LUT_interpolate.py {satellite_sensor} {aerosol_profile} {view_zenith}
```

Let's interpolate one of the LUTs supplied with this repo

```
$ python3 LUT_interpolate.py LANDSAT_OLI MA 0
```



