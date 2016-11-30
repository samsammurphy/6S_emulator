#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validation_stats.py, Sam Murphy (2016-11-30)

Calculates validation statistics. Uses in both Deterministic and MonteCarlo
approaches

"""

import numpy as np

def reflectance_stats(ref, sixs_outputs, estimated_outputs):
  """
  Surface reflectance statistics. Compares 6S outputs to the estimated 
  (i.e. interpolated) outputs in terms of difference in surface reflectance.
  """
  
  def at_sensor_radiance(ref,Edir,Edif,tau2,Lp):
    return ref*tau2*(Edir + Edif)/np.pi + Lp
  
  def surface_reflectance(rad,Edir,Edif,tau2,Lp):
    return np.pi*(rad-Lp) / (tau2*(Edir+Edif))
    
  # convert to arrays (i.e. process input/output lists in one go with no loops)
  SixS = np.array(sixs_outputs)
  est = np.array(estimated_outputs)    
    
  # at-sensor radiance using 6S outputs
  radiance = at_sensor_radiance(ref,SixS[:,0],SixS[:,1],SixS[:,2],SixS[:,3])
  
  # reflectance value from estimated (i.e. interpolated) output
  interp_ref = surface_reflectance(radiance,est[:,0],est[:,1],est[:,2],est[:,3])
  
  # percentage difference from 6S reflectance
  pd = 100*(interp_ref-ref)/ref
  pd = pd[np.where(pd==pd)]    #ignore NaNs  
  
  # mean, std, min, max
  stats = (np.mean(pd),np.std(pd),np.min(pd),np.max(pd)) 
  
  # confidence percentiles (i.e. 90, 95 and 99%)
  q = np.percentile(abs(pd),[90,95,99])
  confidence = {'90':q[0],'95':q[1],'99':q[2]}
  
  # result  
  return {'ref':ref,'pd':pd,'stats':stats,'confidence':confidence}