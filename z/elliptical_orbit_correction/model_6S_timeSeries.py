# -*- coding: utf-8 -*-
"""

model_6S_timeSeries.py, Sam Murphy (2016-11-09)

"""

import os, glob
import pickle
import pylab as plt
import numpy as np
import math
from scipy.optimize import curve_fit

# reads a 6S time series (24 days of year)
def read_6S_time_series(fname):
  file = pickle.load(open(fname,'rb'))
  
  run = {
  'aero': file['inputs']['aero'], # aerosol model
  'solz': file['inputs']['solz'], # solar zenith
  'view': file['inputs']['view'], # view zenith
  'band': file['inputs']['band'], # waveband 
  'H2O': file['inputs']['H2O'],   # water vapoour
  'O3': file['inputs']['O3'],     # ozone
  'AOT': file['inputs']['AOT'],   # aerosol optical thickness
  'alt': file['inputs']['alt'],   # altitude 
  'doy': file['outputs'][0],      # days of year
  'rad': file['outputs'][1],      # radiance
  'Edir': file['outputs'][2],     # direct solar irradiance
  'Edif': file['outputs'][3],     # diffuse solare irradiance
  'Lp': file['outputs'][4]        # path radiance
  }

  return run

# normalizes variable in a time series
def normalize_var(listvar):
  arr = np.array(listvar)
  maxV = np.max(arr)
  return arr / maxV     
  
# normalizes all variables in all time series
def normalize_time_series(indir):

  os.chdir(indir)
  fnames = glob.glob('*.p')
  fnames.sort()
  
  # normalized list
  nEdir = []
  nEdif = []
  nLp = []
  
  for i, fname in enumerate(fnames):
  
    #6S run
    run = read_6S_time_series(fname) 
    
    if np.max(run['Lp']) > 1:
      """
      This minimum path radiance constraint avoids small SWIR values, which 
      can i) 'blow up' on division, ii) result in NaN output from 6S
      """
      
      nEdir.append(normalize_var(run['Edir']))
      nEdif.append(normalize_var(run['Edif']))
      nLp.append(normalize_var(run['Lp']))
      
  return (run['doy'],nEdir,nEdif,nLp)

def doy_stats(nVals):
  
  stats = []
  
  for i in range(24):# 24 days of year (i.e. 4th and 20th of each month)
    v = [vals[i] for vals in nVals]
    stats.append( ( np.mean(v), np.min(v), np.max(v) ) )
    
  return stats

def all_stats(nEdir,nEdif,nLp):
  
  # stats for each doy
  stats_Edir = doy_stats(nEdir)
  stats_Edif = doy_stats(nEdif)
  stats_Lp = doy_stats(nLp)
  
  # parse mean values
  mean_Edir = [stats[0] for stats in stats_Edir]
  mean_Edif = [stats[0] for stats in stats_Edif]
  mean_Lp   = [stats[0] for stats in stats_Lp]
  # parse min values
  min_Edir = [stats[1] for stats in stats_Edir]
  min_Edif = [stats[1] for stats in stats_Edif]
  min_Lp   = [stats[1] for stats in stats_Lp]
  # parse max values
  max_Edir = [stats[2] for stats in stats_Edir]
  max_Edif = [stats[2] for stats in stats_Edif]
  max_Lp   = [stats[2] for stats in stats_Lp]
     
  # combine stats (ease of viewing)
  mean = np.mean([mean_Edir,mean_Edif,mean_Lp],axis=0)
  mn = np.min([min_Edir,min_Edif,min_Lp],axis=0)
  mx = np.max([max_Edir,max_Edif,max_Lp],axis=0)
  
  return {
  'mean':mean,'min':mn,'max':mx, 
  'mean_Edir': mean_Edir,'mean_Edif': mean_Edif,'mean_Lp':   mean_Lp,
  'min_Edir': min_Edir,'min_Edif': min_Edif,'min_Lp': min_Lp,
  'max_Edir': max_Edir,'max_Edif': max_Edif,'max_Lp': max_Lp
        }
        
def plot_stats(doy, stats):
  
  # plots
#  plt.plot(doy,stats['min_Edir'],'_b')
#  plt.plot(doy,stats['min_Edif'],'_b')
#  plt.plot(doy,stats['min_Lp']  ,'_b')
#  
#  plt.plot(doy,stats['max_Edir'],'_r')
#  plt.plot(doy,stats['max_Edif'],'_r')
#  plt.plot(doy,stats['max_Lp']  ,'_r')
#  
#  plt.plot(doy,stats['mean_Edir'],'og')
#  plt.plot(doy,stats['mean_Edif'],'og')
#  plt.plot(doy,stats['mean_Lp']  ,'og')

  plt.plot(doy,stats['min'],'_b',mew=2)
  plt.plot(doy,stats['max'],'_r',mew=2)
  plt.plot(doy,stats['mean'],'og',markeredgecolor='none')

def cos_function(x, a,b,c):
  return a*np.cos(x/(b*math.pi)) + c
  
def fit_cosine(x,y):
  
  amplitude = (max(y)-min(y))
  centre_line = (amplitude/2) + min(y)
  params, stats = curve_fit(cos_function, x,y, p0 = [2,20,centre_line])
  yy = cos_function(x,params[0],params[1],params[2])
  
  return yy, params, stats

def plot_model(params):
  x = np.linspace(1,366,366) # all days of year
  y = cos_function(x, params[0],params[1],params[2])
  plt.plot(x,y,'-',color='gray')  
  plt.xlim(1,366)
  plt.xlabel('Day of Year')
  plt.ylabel('Normalized Output')
  
def main():
  indir = '/home/sam/git/atmcorr/z/elliptical_orbit_correction/SixS_timeSeries'
  
  # read 6S runs and normalize outputs
  doy, nEdir,nEdif,nLp = normalize_time_series(indir)
  
  # get stats of outputs (i.e. instead of plotting thousands of points)
  stats = all_stats(nEdir,nEdif,nLp)
  
  # fit model to mean
  y, params, model_stats = fit_cosine(doy,stats['mean'])
  
  # plot model
  plot_model(params)
  plot_stats(doy, stats)

if __name__ == '__main__':
  main()
