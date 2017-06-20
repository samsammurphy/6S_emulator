## Open-source atmospheric correction 

If you need to convert **radiance to surface reflectance** then this repo might might be for you.

### What is a 6S emulator?

[6S](http://modis-sr.ltdri.org/pages/6SCode.html) is a radiative transfer code used for atmospheric correction. 

The emulator aims to do the same job **100x** faster!!

### Installation

All dependencies are shipped in a [docker](https://www.docker.com/) container. 

1) download and run the container

`$ docker run -it samsammurphy/ee-python3-jupyter-atmcorr:v1.0`

2) clone the repo into the container

`# git clone https://github.com/samsammurphy/6S_emulator`

3) test it works 

jupyter notebook 6S_emulator/jupyter_notebooks/atmcorr_example.ipynb --ip='*' --port=8888 --allow-root


