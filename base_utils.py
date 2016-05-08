import numpy as np
import validations
import math_func_utils as utils
import Error_collector
from datetime import datetime as dt
import pickle


ALLOWED_RAWDATA_MARKET_VEHICLES = {
  'GENERAL': ['GENERAL'],
  'FOREX': ['EURUSD', 'USDJPY']
  
}

ERRORKEY_RD = 'RAWDATA'
ERRORMSG_RD_INITFAIL = 'Failed Initialization. Minimum requirement of valid data value.'
ERRORMSG_RD_BADMARKET = 'Unexpected Market.'
ERRORMSG_RD_BADVEHICLE = 'Unexpected Vehicle.'
ERRORMSG_RD_INVDATE = "Invalid Date."
ERRORMSG_RD_INVTIME = "Invalid Time."

class RawData(object):
  """Data structure for incoming raw data."""
  NUMERIC_ONLY = True
  DEFAULT_MARKET = 'GENERAL'
  DEFAULT_VEHICLE = 'GENERAL'
  
  def __init__(self, value=None, market=None, vehicle=None, date_stamp=None, time_stamp=None):
    self.valid_data = False
    self.value = value
    self.market = market
    self.vehicle = vehicle
    self.date_stamp = date_stamp
    self.time_stamp = time_stamp
    
    self.initError()
    self.insertDefaults()
    self.valid_data = self.dataCheck()

  def to_dict(self):
    return{
      'value': self.value,
      'market': self.market,
      'vehicle': self.vehicle,
      'date_stamp': self.date_stamp,
      'time_stamp': self.time_stamp
    }
  
  def insertDefaults(self):
    if self.market is None:
      self.market = self.DEFAULT_MARKET
    
    if self.vehicle is None and self.market == self.DEFAULT_MARKET:
      self.vehicle = self.DEFAULT_VEHICLE
    
    if self.date_stamp is None:
      self.date_stamp = dt.now().date()
          
    if self.time_stamp is None:
      self.time_stamp = dt.now().time()
    
  def valueCheck(self):
    return not((self.NUMERIC_ONLY and not validations.isNumeric(self.value)) or self.value is None)
  
  def initError(self):
    self._Error = Error_collector.Errors()

  def dataCheck(self):
    all_pass = True
    self.initError()
    if not self.valueCheck():
      self._Error.Add(ERRORKEY_RD, ERRORMSG_RD_INITFAIL)
      all_pass = False
    
    valid_market, valid_vehicle = False, False
    for market, vehicle_list in ALLOWED_RAWDATA_MARKET_VEHICLES.iteritems():
      if self.market == market:
        valid_market = True
        for vehicle in vehicle_list:
          if self.vehicle == vehicle:
            valid_vehicle = True
                    
    if not valid_market:
      self._Error.Add(ERRORKEY_RD, ERRORMSG_RD_BADMARKET)
      all_pass = False

    if not valid_vehicle:
      self._Error.Add(ERRORKEY_RD, ERRORMSG_RD_BADVEHICLE)
      all_pass = False
          
    if not issubclass(type(self.date_stamp), type(dt.now().date())):
      self._Error.Add(ERRORKEY_RD, ERRORMSG_RD_INVDATE)
      all_pass = False

    if not issubclass(type(self.time_stamp), type(dt.now().time())):
      self._Error.Add(ERRORKEY_RD, ERRORMSG_RD_INVTIME)
      all_pass = False
    
    return all_pass

  def __repr__(self):
    vals =  {
      'value': self.value,
      'market': self.market,
      'vehicle': self.vehicle,
      'date_stamp': self.date_stamp,
      'time_stamp': self.time_stamp
    }
    return '<RawData {0}>'.format(vals)

  @property
  def isValid(self):
    self.valid_data = self.dataCheck()
    return self.valid_data


class RollingList(object):
  """A List that has a maximum number of indexes.

  Newest additions are added to the end of the list until list_limit value
  is reached.  At that point, the zero-index is removed as new values continue
  to be added to the end.
  """
  _DEFAULT_MAX_LIST_LENGTH = 50


  def __init__(self, input_data=None, err=(None, None)):
    self.error = err[0]
    self.base_error_key = err[1]

    self._rollinglist = []
    self._listlimit = self._DEFAULT_MAX_LIST_LENGTH
    self._only_numerical = True
    self.periods = 0


    self._high = None
    self._low = None
    self._range = None

    # Accept Default values and add initial value/value-set
    if input_data:
      self.Add(input_data)

  def __len__(self):
    return len(self._rollinglist)

  @property
  def get(self):
    if len(self):
      return self._rollinglist[-1]
    else:
      return None

  @property
  def limit(self):
    return self._listlimit

  @property
  def list(self):
    return self._rollinglist

  @property
  def high(self):
    if self._only_numerical:
      return self._high
    else:
      return None

  @property
  def low(self):
    if self._only_numerical:
      return self._low
    else:
      return None

  @property
  def range(self):
    if self._only_numerical:
      return self._range
    else:
      return None

  @property
  def high_curr(self):
    if len(self) and self._only_numerical:
      return np.max(self._rollinglist)
    else:
      return None

  @property
  def low_curr(self):
    if len(self) and self._only_numerical:
      return np.min(self._rollinglist)
    else:
      return None

  @property
  def range_curr(self):
    if len(self) and self._only_numerical:
      return self.high_curr - self.low_curr

  def _Add(self, val):
    self._rollinglist.append(val)
    self.periods += 1

    if self._only_numerical and validations.isNumeric(val):
      self._high = val if val > self._high or self._high is None else self._high
      self._low = val if val < self._low or self._low is None  else self._low
      self._range = self.high - self.low if self.high and self.low else None

    if len(self) > self._listlimit:
      self._Delete(0)

  def _Delete(self, idx):
    if validations.isNumeric(idx):
      if idx < len(self):
        self._rollinglist.pop(idx)

  def AllowAllValues(self):
    self._only_numerical = False
    self._high = None
    self._low = None
    self._range = None

  def AllowOnlyNum(self, cleanse = True):
    self._only_numerical = True
    if validations.isNumeric(self._rollinglist):
      if cleanse:
        for i, val in enumerate(self._rollinglist):
          if not validations.isNumeric(val):
            self._rollinglist.pop(i)

      self._high = np.max(self._rollinglist)
      self._low = np.max(self._rollinglist)
      self._range = self.high - self.low
    else:
      self._high = None
      self._low = None
      self._range = None

  def SetLimit(self, val):
    if validations.isNumeric(val):
      self._listlimit = val

  def Add(self, val):
    if self._only_numerical and validations.isNumeric(val):
      if validations.isList(val):
        for x in val:
          self._Add(x)
      else:
        self._Add(val)
    elif not self._only_numerical:
      self._Add(val)

  def Reset(self):
    self._rollinglist = []

  def ResetLV(self):
    self._high = None
    self._low = None
    self._range = None

  def ResetAll(self):
    self.Reset()
    self.ResetLV()


class MovingAverage(RollingList):
  """Specialized RollingList object used for Moving Averages."""

  _DEFAULT_SCOPES = {
    '9-period MA':9,
    '15-period MA':15,
    '26-period MA': 26
  }

  def __init__(self, error_key=None):
    super(MovingAverage, self).__init__()
    self._scopes = self._DEFAULT_SCOPES
    self._only_numerical = False
    self.base_error_key = error_key

  @property
  def maxscope(self):
    return np.max(self._scopes.values())

  def AddScope(self, label=None, value=None):
    if label and validations.isNumeric(value):
      self._scopes[label] = value
    else:
      pass # Error exception handling here

  def DelScope(self, val):
    if validations.isNumeric(val):
      for k, v in self._scopes.iteritems():
        if val == v:
          self._scopes.pop(k, None)
    elif isinstance(val, str):
      self._scopes.pop(val, None)

  def AddData(self, RL_obj):
    """Receives RollingList object to calculate trailing MA values as per
    scope definitions.

    """
    if issubclass(type(RL_obj), RollingList):
      data_set = RL_obj.list
      new_data = []
      for label, scope_factor in self._scopes.iteritems():
        if len(data_set) >= scope_factor and validations.isNumeric(data_set):
          avg = utils.numberFormat(np.mean(data_set[-1 * scope_factor:]), 4)
        else:
          avg = 'NA'
        new_data.append((label, scope_factor, avg))
      self.Add(tuple(new_data))


