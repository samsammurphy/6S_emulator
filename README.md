## Open-source atmospheric correction 

If you need to convert **radiance to surface reflectance** then this repo might might be for you.

### What is a 6S emulator?

[6S](http://modis-sr.ltdri.org/pages/6SCode.html) is a radiative transfer code used for atmospheric correction. 

The emulator aims to do the same job **100x** faster!!

### Usage

The jupyter notebook has a basic example of atmospheric correction.

### Concept Overview

The 6S emuator is based on the use of interpolated look-up tables. They radiative transfer type results but much faster. To acheive this speed increase the look-up tables are built in advance. This takes a long time (i.e. hours) but only needs to be done once, for a given satellite mission. 

This enables folks to atmospherically correct any satellite data for free!

The computer processing requirements are also very modest (i.e. most of the expensive work is done in advance) which means this solution could run on-board your own cubesat and perform on-the-fly atmospheric correction!



