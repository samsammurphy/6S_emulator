#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonteCarlo_Plot.py, Sam Murphy (2016-12-02)

Plots delta reflectance (dref) intervals at 95 % confidence for all surface 
reflectances
"""

import numpy as np
from matplotlib import pylab as plt
from matplotlib import rcParams
from MonteCarlo_Histoplot import load_performance_stats
from MonteCarlo_Histoplot import dref_slice
from MonteCarlo_Histoplot import color_from_channel

  
    
def plot_percentiles(channel,ax):
  """
  Plots 95% confidence dref intervals for all surface reflectances
  """
  
  # load performance statistics (all reflectances)
  drefs, refs = load_performance_stats(channel)
  
  # percentiles
  P = []
    
  for ref in refs:
    
    # stats for this reflectance
    dref = dref_slice(drefs,refs,ref)
    
    # convert to percentage reflectance (as opposed to fractional reflectance)
    dref *= 100
    
    # calculate 95th, 99th and 100th percentiles
    P.append(np.percentile(abs(dref),[95,99,100]))
      
  color = color_from_channel(channel)
  ax.plot(100*refs,[p[0] for p in P],color,ls='dotted')
  ax.plot(100*refs,[p[1] for p in P],color,ls='dashed')
  ax.plot(100*refs,[p[2] for p in P],color,ls='solid')
  ax.set_ylim([0,3])
        
    
def main():
  

  # Global plot attributes
  rcParams['figure.figsize'] = 20, 12# custom figure size
  rcParams['lines.linewidth'] = 4
  rcParams['xtick.direction'] = 'out'# xticks that point down
  rcParams['ytick.direction'] = 'out'# xticks that point down
  
  # subplots
  f, axs = plt.subplots(2, 3)  
  
  # plot histograms
  plot_percentiles('blue',axs[0][0])
  plot_percentiles('green',axs[0][1])
  plot_percentiles('red',axs[0][2])
  plot_percentiles('nir',axs[1][0])
  plot_percentiles('swir1',axs[1][1])
  plot_percentiles('swir2',axs[1][2])
  
  # save to file
  plt.savefig('/home/sam/Desktop/demo.png', transparent=True)
   
if __name__ == '__main__':
  main()