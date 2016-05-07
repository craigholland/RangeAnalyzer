import numpy as np
import math_func_utils as utils
import base_utils as butils
import validations
from Error_collector import Errors

ERRORKEY_RANGEANALYSIS = 'RANGEANALYSIS'
ERRORKEY_ROLLINGLIST_DATA = 'RL_DATA'
ERRORKEY_ROLLINGLIST_MEAN = 'RL_MEAN'
ERRORKEY_ROLLINGLIST_STDEV = 'RL_STDEV'
ERRORKEY_ROLLINGLIST_PERCB = 'RL_PERCENTB'
ERRORKEY_MOVINGAVERAGE = 'MOVINGAVERAGE'
ERRORKEY_CALC = 'CALCULATIONS'

ERRORMSG_RA_INITFAIL = 'Failed Initialization: {0}'
ERRORMSG_RA_ADDFAIL = 'Failed Add. Data must be numeric: {0}'
ERRORMSG_RA_NORMALIZE = 'Failed Normalization. High Value cannot be less than Low Value. H:{0} L{0}:'
ERRORMSG_RA_NUMFORMAT = 'Cannot format number: {0}'


class RangeAnalysis(object):
  _RAW_DATA_MAX_LIMIT = 500
  _SUBLIST_MAX_LIMIT = 120

  _VOLATILITY_INDEX = [
    ('Increasing', 1),
    ('Channel - High', .67),
    ('Channel - Medium', .33),
    ('Channel - Low', .00001),
    ('Decreasing', 0)
  ]
  _DEFAULT_DECIMAL_LIMIT = 3

  def __init__(self, input_list=None):
    self.error = Errors()
    self.base_error_key = ERRORKEY_RANGEANALYSIS

    self._raw_data = butils.RollingList(err=(self.error, ERRORKEY_ROLLINGLIST_DATA))
    self._raw_data.SetLimit(self._RAW_DATA_MAX_LIMIT)

    self._mean = butils.RollingList(err=(self.error, ERRORKEY_ROLLINGLIST_MEAN))
    self._mean.SetLimit(self._SUBLIST_MAX_LIMIT)
    self._mean_lifetime = None

    self._movingaverage = butils.MovingAverage(error_key=ERRORKEY_MOVINGAVERAGE)
    self._movingaverage.SetLimit(self._SUBLIST_MAX_LIMIT)

    self._stdev = butils.RollingList(err=(self.error, ERRORKEY_ROLLINGLIST_STDEV))
    self._stdev.SetLimit(self._SUBLIST_MAX_LIMIT)
    self._stdev_lifetime = None

    self._percentBandwidth = butils.RollingList(err=(self.error, ERRORKEY_ROLLINGLIST_PERCB))
    self._percentBandwidth.SetLimit(self._SUBLIST_MAX_LIMIT)

    if input_list:
      self.Add(input_list)

  # Shortcuts and Basic Range Data.
  def __len__(self):
    return len(self.Data.list)
  
  @property
  def Data(self):
    return self._raw_data
  
  @property
  def list(self):
    return self.Data.list
  
  @property
  def periods(self):
    return self.Data.periods
  
  @property
  def get(self):
    if len(self):
      return self.list[-1]
    else:
      return None

  @property
  def low(self):
    return self.Data.low

  @property
  def high(self):
    return self.Data.high

  @property
  def range(self):
    return self.Data.range

  @property
  def low_curr(self):
    return self.Data.low_curr

  @property
  def high_curr(self):
    return self.Data.high_curr

  @property
  def range_curr(self):
    return self.Data.range_curr

  # First-order calculations.
  @property
  def Mean(self):
    return self._mean

  @property
  def mean(self):
    return self.Mean.get

  @property
  def mean_lifetime(self):
    return self._mean_lifetime

  @property
  def Movingaverage(self):
    return self._movingaverage

  @property
  def movingaverage(self):
    return self.Movingaverage.get

  # Second-order calculations.
  @property
  def Stdev(self):
    return self._stdev

  @property
  def stdev(self):
    return self.Stdev.get

  @property
  def stdev_lifetime(self):
    return self._stdev_lifetime

  # Third-order calculations.
  @property
  def Percentb(self):
    return self._percentBandwidth

  @property
  def percentb(self):
    return self.Percentb.get

  @property
  def bandwidth(self):
    if self.stdev:
      return 2* self.stdev
    else:
      return None

  @property
  def volatility(self):
    for label, idx in self._VOLATILITY_INDEX:
      if self.percentb >= idx:
        return label

  @property
  def volatility_index(self):
    for i, idx in enumerate(self._VOLATILITY_INDEX):
      if self.percentb >= idx[1]:
        return len(self._VOLATILITY_INDEX) - i

  def _Add(self, val):
    val = float(val)
    old_mean = self.mean if len(self.Mean) else 0
    self.Data.Add(val)
    
    periods = self.periods
    
    # First Order Ops.
    self._mean_lifetime = (old_mean * (periods -1) + val) / periods
    self.Mean.Add(self._mean_lifetime)
    
    self.Movingaverage.AddData(self.Data)
    
    # Second Order Ops.
    if len(self) > 1:
      if self.stdev:
        stdev = utils.ReStDev(val, self.stdev, self.mean, periods-1)
      else:
        stdev = utils.StDev(self.list)
    elif len(self):
      stdev = 0
    else:
      stdev = None
    self.Stdev.Add(stdev)

    # Third Order Ops.
    sd_high = self.Stdev.high
    sd_low = self.Stdev.low
    percb = utils.numberFormat(self.Normalize(sd_low, sd_high, self.stdev), 4)
    self.Percentb.Add(percb)

  def Add(self, data):
    """Receives singular value or list/tuple of values to add to raw_data."""

    if validations.isList(data) and validations.isNumeric(data):
      for x in data:
        self._Add(x)
    elif validations.isNumeric(data):
      self._Add(data)
    else:
      self.error.Add(self.base_error_key, ERRORMSG_RA_ADDFAIL.format(data))

  def Normalize(self, low_val, high_val, x):

    if high_val < low_val:
      self.error.Add(self.base_error_key, ERRORMSG_RA_NORMALIZE.format(high_val, low_val))
    elif high_val == low_val:
      return 0.0
    else:
      return (x - low_val) / (high_val - low_val)

  def NormalizeDataset_RL(self, num_list, sliding=True, forced_high = None, forced_low = None):
    """Normalize data in RollingList object.

    Sliding:
      True - High's/Low's re-defined during iteration of list.
      False - High/Low defined once in the context of the entire list.
    """

    normalized_list = []
    if validations.isList(num_list) and validations.isNumeric(num_list):
      if sliding:
        low, high = None, None
        for val in num_list:
          low = val if val < low or low is None else low
          high = val if val > high or high is None else high

          low = forced_low if forced_low is not None else low
          high = forced_high if forced_high is not None else high

          normalized_list.append(self.Normalize(low, high, val))
      else:
        low = np.min(num_list) if forced_low is not None else forced_low
        high = np.max(num_list) if forced_high is not None else forced_high
        for val in num_list:
          normalized_list.append(self.Normalize(low, high, val))

    return normalized_list








