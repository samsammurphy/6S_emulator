#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonteCarlo_Histoplot.py

Plots histograms of 6S LUT performance (i.e. reflectance difference) 
separately for each Landsat 8 waveband that was tested


"""

import numpy as np
from matplotlib import pylab as plt
from matplotlib import rcParams

from MonteCarlo_Histoplot import load_performance_stats
from MonteCarlo_Histoplot import dref_slice
from MonteCarlo_Histoplot import color_from_channel

from matplotlib.lines import Line2D
  

def plot_histogram(ref,channel,ax):
  """
  Plots delta surface reflectance histograms
  """
  
  ax.set_xlim([-1.2,1.2])
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  ax.get_xaxis().tick_bottom()
  ax.get_yaxis().set_visible(False)
      
  # load performance statistics (all reflectances)
  drefs, refs = load_performance_stats(channel)
    
  # stats for this reflectance
  dref = dref_slice(drefs,refs,ref)
  
  # convert to percentage reflectance (as opposed to fractional reflectance)
  dref *= 100
 
  # perfornance histogram
  color = color_from_channel(channel)
  bins = np.linspace(-5,5,501)
  ax.hist(dref, bins, normed=1, facecolor=color)
    
  # percentiles
  p95, p99, p100 = np.percentile(abs(dref),[95,99,100])
  
  #95%
  ax.plot([-p95,-p95],ax.get_ylim(),color=color,ls='dotted')
  ax.plot([ p95, p95],ax.get_ylim(),color=color,ls='dotted') 
  
  #99%
  ax.plot([-p99,-p99],ax.get_ylim(),color=color,ls='dashed')
  ax.plot([ p99, p99],ax.get_ylim(),color=color,ls='dashed') 

  #100%
  ax.plot([-p100,-p100],ax.get_ylim(),color=color,ls='solid')
  ax.plot([ p100, p100],ax.get_ylim(),color=color,ls='solid') 
  
  
    
def main():
  
  # surface reflectance (SR)
  ref = 0.1

  # Global plot attributes
  rcParams['figure.figsize'] = 20, 12# custom figure size
  rcParams['lines.linewidth'] = 2
  rcParams['xtick.direction'] = 'out'# xticks that point down
  
  # subplots
  f, axs = plt.subplots(2, 3)  
  
  # plot histograms
  plot_histogram(ref,'blue',axs[0][0])
  plot_histogram(ref,'green',axs[0][1])
  plot_histogram(ref,'red',axs[0][2])
  plot_histogram(ref,'nir',axs[1][0])
  plot_histogram(ref,'swir1',axs[1][1])
  plot_histogram(ref,'swir2',axs[1][2])
  
  # save to file
  plt.savefig('/home/sam/Desktop/demo.png', transparent=True)
  
if __name__ == '__main__':
  main()