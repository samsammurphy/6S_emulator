# -*- coding: utf-8 -*-
"""

The Earth's orbit is elliptical, ESUN varies as a function of Earth-Sun distance

ESUN = f(d)

which causes the dependent variables Edir,Edif and Lp to vary also.

Edir = f(d)
Edif = f(d)
Lp   = f(d)

The effect on ESUN is fairly straight-forward (i.e. inverse power law), however,
what we really want to know is how the dependents behave with distance.

To do this we first recall that Earth-sun distance is itself a function of time

d = f(t)

or, more specifically, day of year

d = f(doy)

It follows that the depedents are therefore functions of day of year

Edir = f(doy)
Edif = f(doy)
Lp   = f(doy)

Which is a more convenient way of looking at the problem because we can run the
radiative transfer code once and then modify it.

Here we will investigate if a simple harmonic can be used to fit x = f(doy)

x = a.cos(doy / (b.pi)) + c

where x is normalized (Edir or Edif or Lp). The advantage of normalizing
is twofold

1) it allows comparison of the different atmospheric conditions 
(does the function at least have the same shape? answer = yes)

2) the normalized function is the correction coefficient required to convert
Edir, Edif and Lp at perihelion (i.e. as in the LUTs) to their actual value
at a given Earth-sun distance as determined by the day of year.

'create_time_series.py' ran multiple 6S runs to cover the parameter space. 
here we just call the pickle files saved by that modules

"""

import os, glob
import pickle
import pylab as plt
import numpy as np
import math
from scipy.optimize import curve_fit

# normalizes variable to its maximum value in a time series
def normalize_var(listvar):
  arr = np.array(listvar)
  normVar = arr / np.max(arr)
  
  return normVar
  
# reads a given run into a dictionary
def read_run(fname):
  file = pickle.load(open(fname,'rb'))
  
  run = {
  'aero': file['inputs']['aero'],
  'solz': file['inputs']['solz'],
  'view': file['inputs']['view'],
  'band': file['inputs']['band'],
  'H2O': file['inputs']['H2O'],
  'O3': file['inputs']['O3'],
  'AOT': file['inputs']['AOT'],
  'doy': file['outputs'][0],
  'rad': file['outputs'][1],
  'Edir': file['outputs'][2],
  'Edif': file['outputs'][3],
  'Lp': file['outputs'][4]
  }

  return run

#normalizes the outputs
def normalize_run(run):
  
  norm = {
  'rad' : normalize_var(run['rad']),
  'Edir': normalize_var(run['Edir']),
  'Edif': normalize_var(run['Edif']),
  'Lp'  : normalize_var(run['Lp'])
  }

  return norm

# define a cosine function
def cos_function(x, a,b,c):
  cosFunction = a*np.cos(x/(b*math.pi)) + c
  return cosFunction

def fit_cosine(x,y):
  
  amplitude = (max(y)-min(y))
  centre_line = (amplitude/2) + min(y)
  params, stats = curve_fit(cos_function, x,y, p0 = [2,20,centre_line])
  yy = cos_function(x,params[0],params[1],params[2])
  
  return yy, params, stats

#***********************************************************************
# MAIN
#***********************************************************************
  
os.chdir('/home/sam/git/atmcorr_py6s/z/experimental/harmonic_investigation/time_series')
fnames = glob.glob('*.p')
fnames.sort()


label = 'Edif'

# define cumulative array (to calculate mean valid value)
cum = np.zeros(24)

for fname in fnames:
  run = read_run(fname)                    # load and parse data 
  if np.max(run[label]) >= 1:              # only fit non-negligable values
    norm = normalize_run(run)              # normalize outputs from this run
    plt.plot(run['doy'],norm[label],'.k')  # update time series data plot
    cum += norm[label]                     # save cumulative values

# plot mean valid value
mean = cum/np.max(cum) 
plt.plot(run['doy'],mean,'b')  

# plot model of time series data
y, params, stats = fit_cosine(run['doy'],mean)
plt.plot(run['doy'],y,'r') 
plt.title(label)
plt.show() 

print('model parameters = ',params)


# Edir
# model parameters =  [  0.0327505   18.99181408   0.96804793]

# Edif
# model parameters =  [  0.03275025  18.99238934   0.96805088]

# Lp
# model parameters =  [  0.0327459   18.99219987   0.96804217]
















