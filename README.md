## Open-source atmospheric correction 

If you need to convert **radiance to surface reflectance** then this repo might might be for you.

### What is a 6S emulator?

[6S](http://modis-sr.ltdri.org/pages/6SCode.html) is a radiative transfer code used for atmospheric correction. 

The emulator aims to do the same job but **100x** faster!!

### Installation

All dependencies are shipped in a [docker](https://www.docker.com/) container. 

1) download and run the container

`$ docker run -it samsammurphy/ee-python3-jupyter-atmcorr:v1.0`

2) test it works 

(some default test)

### Example usage

example 1: jupyter notebook

1) run the container and connect to port 8888

`docker run -i -t -p 8888:8888 18f5f8bb35d0`

2) open up a jupyter notebook

`jupyter notebook path_to_illustrative_notebook --ip='*' --port=8888 --allow-root`

example 2: connect to local drive

`docker run (local drive connection)`

example 3: use with Google Earth Engine

1) run container

2) earthengine authenticate

3) (optional) commit to new container to save authentication and run that instead

4) open earthengine notebook
