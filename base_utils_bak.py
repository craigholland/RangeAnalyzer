import numpy as np
import validations

class RollingList(object):
  """A List that has a maximum number of indexes.

  Newest additions are added to the end of the list until list_limit value
  is reached.  At that point, the zero-index is removed as new values continue
  to be added to the end.
  """

  def __init__(self, input_data=None):
    self._rollinglist = []
    self._list_limit = 10

    # Default setting only allows for numerical values.
    self._only_numerical_values = True

    if input_data:
      self.Add(input_data)

  def __len__(self):
    return len(self._rollinglist)

  @property
  def get(self):
    if len(self)>0:
      return self._rollinglist[len(self)-1]
    return None

  @property
  def limit(self):
    return self._list_limit

  @property
  def list(self):
    return self._rollinglist

  def AllowAllValues(self):
    self._only_numerical_values = False

  def AllowOnlyNumbers(self, cleanse = False):
    self._only_numerical_values = True
    if cleanse:
      for i, val in enumerate(self._rollinglist):
        if not validations.isNumeric(val):
          self._rollinglist.pop(i)

  def SetLimit(self, val):
    if validations.isNumeric(val):
      self._list_limit = val
      while len(self) > val:
        self._rollinglist.pop(0)

  def Delete(self):
    self._rollinglist.pop(0)
  delete = Delete

  def Add(self, val):
    if validations.isNumeric(val) and self._only_numerical_values:
      if validations.isList(val):
        for x in val:
          self.Add(x)
      else:
        self._rollinglist.append(val)
        if len(self) > self.limit:
          self.Delete()
    elif not self._only_numerical_values:
      self._rollinglist.append(val)

  add = Add

  def Copy(self):
    copy = []
    for val in self._rollinglist:
      copy.append(val)
    return copy
  copy = Copy

  def Reset(self):
    self.__init__()


class MovingAverage(object):
  """Moving Averages Constructor class"""
  _DEFAULT_SCOPES = {
    '9-period MA':9,
    '20-period MA':20
  }
  def __init__(self):
    self.scopes = self._DEFAULT_SCOPES

    # Incoming raw Data
    self.data = RollingList()
    self.data.SetLimit(self.maxscope)

    # Output
    self.vals = RollingList()
    self.vals._only_numerical_values = False

    self.scopevalues = sorted([val for val in self.scopes.itervalues()])

  def __len__(self):
    return len(self.vals)

  @property
  def maxscope(self):
    max_val = 0
    for k, v in self.scopes.iteritems():
      if v > max_val:
        max_val = v
    return max_val

  @property
  def get(self):
    if len(self)>0:
      return self.vals.list[len(self)-1]
    return None

  @property
  def list(self):
    return self.vals.list

  def Reset(self, default_scopes=False):
    if default_scopes:
      self.__init__()
    else:
      # Incoming raw Data
      self.data = RollingList()
      self.data.SetLimit(self.maxscope)

      # Output
      self.vals = RollingList()
      self.vals.data_validation_switch = False

  def AddScope(self, label=None, value=None):
    if label and validations.isNumeric(value):
      self.scopes[label] = value
    else:
      pass # Error exception handling here

  def DelScope(self, val):
    if isinstance(val, str):
      self.scopes.pop(val, None)

    if validations.isNumeric(val):
      for k, v in self.scopes.iteritems():
        if val == v:
          self.scopes.pop(k, None)

  def Add(self, val):
    if validations.isNumeric(val):
      if validations.isList(val):
        for x in val:
          self.Add(x)
      else:
        self.data.add(val)
        self._calcAverages()
  add = Add

  def _calcAverages(self):
    temp_list = self.data.copy()
    temp_list.reverse()
    averages = []
    for scope, val in self.scopes.iteritems():
      if len(temp_list) >= val:
        avg = np.mean(temp_list[:val])
      else:
        avg = 'NA'
      averages.append((scope, val, avg))
    self.vals.add(tuple(averages))











