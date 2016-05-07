import numpy as np
import validations

STDEV_ERRORKEY = 'STDEV ERROR'
def StDev(data_array, error_obj=None):
  """Calculate Standard Deviation from array of numeric datapoints."""

  #Validate array.
  sum_variance = 0.0
  validated = True
  err_is_object = not isinstance(error_obj, type(None))
  if validations.isList(data_array):
    if not validations.isNumeric(data_array):
      validated = False
      if err_is_object:
          error_obj.Add(STDEV_ERRORKEY, 'Array contents must be numeric.')
  elif err_is_object:
    error_obj.Add(STDEV_ERRORKEY, 'Input must be a list or tuple.')
    validated = False
  else:
    validated = False

  # Calculate Standard Deviation.
  if validated:
    periods = len(data_array)
    if periods > 1:
      mean = np.mean(data_array)
      for val in data_array:
        sum_variance += pow(val - mean, 2)
      stdev = pow(pow(periods-1, -1) * sum_variance, .5)
    else:
      mean = float(data_array[0])
      stdev = 0.0

    return stdev, periods, mean
  elif error_obj:
    return error_obj
  else:
    return False

def StDevSumSq(sumsq, mean, periods):
  """Calculate StDev based on SumSq, mean, periods."""
  numer = sumsq - pow(mean, 2) * periods
  denom = periods - 1
  return pow(numer / denom, .5)

def SumSq(stdev, mean, periods):
  """Calculate Sum of Squares given St Dev, Mean, and Periods."""
  return pow(stdev, 2) * (periods-1) + pow(mean, 2)* periods

def SumSq_array(data_array):
  """Calculate Sum of Squares given an array of numerical values."""
  sumsq = 0.0
  if validations.isNumeric(data_array):
    for val in data_array:
      sumsq += pow(val, 2)
  return sumsq

def ReStDev(new_data, old_stdev, old_mean, old_periods, error_obj=None):
    """Calculate St. Deviation using existing stdev/mean/period values.

    Without having to calculate ENTIRE raw_data. (faster than StDev)
    """
    err_is_object = not isinstance(error_obj, type(None))
    def Calc(val, old_stdev, old_mean, old_periods):
      sumsq = SumSq(old_stdev, old_mean, old_periods)
      new_periods = old_periods + 1
      new_mean = ((old_mean * old_periods) + val) / new_periods
      new_sumsq = sumsq + pow(val, 2)
      new_stdev = StDevSumSq(new_sumsq, new_mean, new_periods)
      return new_stdev, new_mean, new_periods

    if validations.isNumeric(new_data):
      if validations.isList(new_data):
        for data in new_data:
          old_stdev, old_mean, old_periods = Calc(data, old_stdev, old_mean, old_periods)
        new_stdev, new_mean, new_periods = old_stdev, old_mean, old_periods
      else:
        new_stdev, new_mean, new_periods = Calc(new_data, old_stdev, old_mean, old_periods)
    elif err_is_object:
      error_obj.Add(STDEV_ERRORKEY, 'Input(s) must be numeric.')
      return error_obj
    else:
      return False

    return new_stdev, new_periods, new_mean

def numberFormat(val, dec_places=2, error=(None, None)):
    error_obj, error_key = error[0], error[1]
    ERRORMSG_RA_NUMFORMAT='test'

    if validations.isNumeric(val) and validations.isNumeric(dec_places):
      factor =  pow(10, dec_places)
      return float(int(val * factor)) / factor
    else:
      error_obj.Add(error_key, ERRORMSG_RA_NUMFORMAT.format(val))

def numberFormat_list(val, dec_places=None, error=(None, None)):
  if validations.isList(val) and validations.isNumeric(val):
    return [x for numberFormat(x, dec_places, error)]

