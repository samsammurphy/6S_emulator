## Introduction

The 6S emulator is an open-source atmospheric correction tool. It is based on the [6S](http://modis-sr.ltdri.org/pages/6SCode.html) radiative transfer model but it **runs 100x faster** with minimal additional error (i.e. < 0.5 %).

This speed increase is acheived by building interpolated look-up tables. This trades set-up time for execution time. The look-up tables take a long time (i.e. hours) to build, here are some prebuilts for: [Sentinel 2](https://www.dropbox.com/s/aq873gil0ph47fm/S2A_MSI.zip?dl=1), [Landsat 8](https://www.dropbox.com/s/49ikr48d2qqwkhm/LANDSAT_OLI.zip?dl=1), [Landsat 7](https://www.dropbox.com/s/z6vv55cz5tow6tj/LANDSAT_ETM.zip?dl=1) & [Landsat 4 and 5](https://www.dropbox.com/s/uyiab5r9kl50m2f/LANDSAT_TM.zip?dl=1). You only need to build (or download) a look-up table once.
 
Interpolated look-up tables are the core of the 6S emulator. Essentially, they are used to calculate atmospheric correction coefficients (a, b) which convert at-sensor radiance (L) to surface reflectance (ρ) as follows:

ρ = (L - a) / b

### Installation

##### Quick note

These installation requirements are for those building look-up tables. To use a pre-existing look-up table, all that is required are python3.x, numpy and scipy.

We interact with 6S through an excellent Python wrapper called [Py6S](http://py6s.readthedocs.io/en/latest/index.html) and share the same dependencies. 

#### Recommended installation

The [recommended installation](http://py6s.readthedocs.io/en/latest/installation.html) method is to use the [conda](https://conda.io/docs/install/quick.html) package and environment manager.

`$ conda create -n py6s-env -c conda-forge py6s`

This will create a new environment that needs to be activated.

#### Alternative 1: add conda-forge channel

You could permanently add the conda-forge channel if you prefer to avoid (de)activate environments.

`$ conda config --add channels conda-forge`

`$ conda install py6s`

#### Alternative 2: docker

You could optionally run the following [docker](https://www.docker.com/) container instead, which has all dependencies pre-installed

`$ docker run -it samsammurphy/ee-python3-jupyter-atmcorr:v1.0`

then clone this repository into the container

`# git clone https://github.com/samsammurphy/6S_emulator`

#### Alternative 3: manual install

Here are a list of all [dependencies](https://github.com/samsammurphy/6S_emulator/wiki/Dependencies) for manual installation.

### Usage

#### Quick Start

See the [jupyter notebook](https://github.com/samsammurphy/6S_emulator/blob/master/jupyter_notebooks/atmcorr_example.ipynb) for a quick start example of atmospheric correction. 

#### Building your own interpolated look-up tables

It is much more bandwidth efficient to send  and receive look-up tables, and then interpolate them locally, which is why building and interpolating are handled by separate modules. To see a more complete list of examples of how to build a look-up table (for any satellite mission) see this [wiki](https://github.com/samsammurphy/6S_emulator/wiki/Build-examples). Here is a short example.

`$ python3 LUT_build.py --wavelength 0.42`

which will build a look-up table for a wavelength of 0.42 microns, it can be interpolated as follows

`$ python3 LUT_interpolate.py  path/to/LUT_directory`

where the 'path/to/LUT_directory' is the full path to the look-up table files ('.lut').

#### Using interpolated look-up tables

An interpolated look-up tables is a [pickle](https://docs.python.org/3/library/pickle.html) file of a [scipy](https://www.scipy.org/) linear n-dimensional [interpolator](https://docs.scipy.org/doc/scipy-0.19.0/reference/generated/scipy.interpolate.LinearNDInterpolator.html). It can be loaded like this:

```
import pickle

fpath = 'path/to/interpolated_lookup_table.ilut'

with open(fpath,"rb") as ilut_file:
    iLUT = pickle.load(ilut_file)
```

An interpolated look-up table requires the following input variables (in order) to provide atmospheric correction coefficients:

1. solar zentith [degrees] (0 - 75)
2. water vapour [g/m2] (0 - 8.5)
3. ozone [cm-atm] (0 - 0.8)
4. aerosol optical thickness [unitless] (0 - 3)
5. surface altitude [km] (0 - 7.75)

In code it might look something like this

`a, b = iLUT(solar_z, h2o, o3, aot, km)`

where a and b are the atmospheric correction coefficients at perihelion. The look-up tables are built at perihelion (i.e. January 4th) to save space because Earth's elliptical orbit can be corrected as follows:

````
import math

elliptical_orbit_correction = 0.03275104*math.cos(doy/59.66638337) + 0.96804905
a *= elliptical_orbit_correction
b *= elliptical_orbit_correction
```

the coefficients can now be used to correct radiance to surface reflectance

`surface_reflectance = (L - a) / b`
