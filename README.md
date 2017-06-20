## Introduction

The 6S emulator is an open-source atmospheric correction tool. It is based on the [6S](http://modis-sr.ltdri.org/pages/6SCode.html) radiative transfer model but it **runs 100x faster** with minimal additional error (i.e. < 0.5 %).

This speed increase is acheived by building interpolated look-up tables. This trades set-up time for execution time. The look-up tables take a long time (i.e. hours) to build, here are some prebuilts for: [Sentinel 2](https://www.dropbox.com/s/aq873gil0ph47fm/S2A_MSI.zip?dl=1), [Landsat 8](https://www.dropbox.com/s/49ikr48d2qqwkhm/LANDSAT_OLI.zip?dl=1), [Landsat 7](https://www.dropbox.com/s/z6vv55cz5tow6tj/LANDSAT_ETM.zip?dl=1) & [Landsat 4 and 5](https://www.dropbox.com/s/uyiab5r9kl50m2f/LANDSAT_TM.zip?dl=1). You only need to build (or download) a look-up table once.
 
It is much more bandwidth efficient to send/receive look-up tables, and then interpolate them locally. For example

`$ python3 LUT_interpolate.py  path/to/LUT_directory`

Interpolated look-up tables are the core of the 6S emulator. Essentially, they are used to calculate atmospheric correction coefficients (a, b) which can then convert at-sensor radiance (L) to surface reflectance (ρ) as follows:

ρ = (L - a) / b

### Installation

We interact with 6S through an excellent Python wrapper called [Py6S](http://py6s.readthedocs.io/en/latest/index.html) and share the same dependencies. 

##### Quick note

These installation requirements are for those building look-up tables. To use a pre-existing look-up table, all that is required are python3.x, numpy and scipy.

#### Recommended

The [recommended installation](http://py6s.readthedocs.io/en/latest/installation.html) method is to use the [conda](https://conda.io/docs/install/quick.html) package and environment manager.

`$ conda create -n py6s-env -c conda-forge py6s`

This will create a new environment that needs to be activated.

#### Alternative 1: add conda-forge channel

You could permanently add the conda-forge channel if you prefer to avoid the need to (de)activate environments.

`$ conda config --add channels conda-forge`

`$ conda install py6s`

#### Alternative 2: docker

You can run the following docker container with all dependencies pre-installed

`$ docker run -it samsammurphy/ee-python3-jupyter-atmcorr:v1.0`

then clone this repository into the container

`# git clone https://github.com/samsammurphy/6S_emulator`

#### Alternative 3: manual install

Here are a list of all [dependencies](https://github.com/samsammurphy/6S_emulator/wiki/Dependencies) for manual installation.

### Usage

The jupyter notebook has a basic example of atmospheric correction.





