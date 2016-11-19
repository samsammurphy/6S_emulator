## Atmospheric correction of satellite images using 6S

### Who is this repo for?

If you need to convert **at-sensor radiance to surface reflectance** then this repo might might be for you

### How does it work?

We use the [6S](http://modis-sr.ltdri.org/pages/6SCode.html) radiative transfer code through a Python wrapper called [Py6S](http://py6s.readthedocs.io/en/latest/introduction.html). The project is written in Python. 

We build interpolated look up tables ([iLUTs](https://github.com/samsammurphy/6S_LUT/wiki/Interpolated-Look-up-Tables-(iLUTs))) to get the parameter values needed to [atmospherically correct](https://github.com/samsammurphy/6S_LUT/blob/master/z/jupyter_notebooks/atmcorr_example_1.ipynb) radiance measured by a satellite sensor.

### Why is this important?

Radiative transfer code (e.g. 6S, MODTRAN, etc.) take a [long time](link) to execute. The use of an iLUT boost performance speeds by a few orders of magnitude with a minimal effect on accuracy (i.e. [within X %](link)). 

### What about MODTRAN?

6S shows good agreement ([i.e. < 0.7 %](http://6s.ltdri.org/files/publication/Kotchenova_et_al_2006.pdf)) with MODTRAN. Some studies indicate that 6S has an edge in terms of accuracy; these include [Monte Carlo](http://6s.ltdri.org/files/publication/Kotchenova_et_al_2008.pdf) and [Ground-Truth](https://www.researchgate.net/publication/263620472_Evaluation_of_atmospheric_correction_models_and_Landsat_surface_reflectance_product_in_an_urban_coastal_environment) approaches. 

NASA and the USGS use 6S for [Landsat](http://landsat.usgs.gov/CDR_LSR.php) and [MODIS](http://6s.ltdri.org/) surface reflectance products.
