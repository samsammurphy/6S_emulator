#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonteCarlo_Histoplot.py

Plots histogram of percentage difference for a single surface reflectance
"""

import sys
import pickle
import numpy as np
from matplotlib import pylab as plt


def dref_slice(drefs, refs, ref):
  """
  Performance metric is delta reflectance (dref). It was calculated for a 
  range of true relfectance values. This returns stats for single true ref.
  """
  index = np.where(ref == refs)[0]
  if len(index) == 0:
    print('ref not available: {}'.format(ref))
    sys.exit()
  return np.array([ds[index][0] for ds in drefs])

def plot_histograms(dref,ref):
  """
  Plots two histograms 1) percentage difference, 2) delta reflectance
  """
  fig = plt.figure()
  ax1 = fig.add_subplot(211)
  ax2 = fig.add_subplot(212)
  
  # percentage difference histograms
  bins = np.linspace(-10,10,101)
  pd = 100*dref/ref
  ax1.hist(pd, bins, normed=1, facecolor='r')
  ax1.set_title('percentage difference')
  
  # dref histogram
  bins = ref*bins/100 # convert to reflectance values (but in same % range)
  ax2.hist(dref, bins ,normed=1, facecolor='r')
  ax2.set_xlim((min(bins),max(bins)))
  ax2.set_title('delta reflectance')
  
  fig.tight_layout()
  
  print(np.percentile(abs(pd),95))

def main():
  
  # surface reflectance (SR)
  ref = 0.5
  
  # load performance statistics
  fname = '/home/sam/git/6S_LUT/z/validation/MonteCarlo/stats/red/stats_1480633563.p'
  drefs, refs = pickle.load(open(fname,'rb'))
  
  # stats for this SR
  dref = dref_slice(drefs,refs,ref)

  # histogram plot
  plot_histograms(dref,ref)
  
if __name__ == '__main__':
  main()