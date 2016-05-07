
def isNumeric(data, NoEmptyList = True):
  """Truth value testing to check if value is float/int.

  Data can be singular value or list/tuple of values.  Function
  can handle nested sets, but empty lists will return False (unless
  NoEmptyList is switched to False)
  """
  def isValNumeric(val):
    try:
      float(val)
      if isinstance(val, bool):
        return False
      return True
    except ValueError:
      return False
  if isinstance(data, list) or isinstance(data, tuple):
    result = True
    if data or not NoEmptyList:
      for idx in data:
        result = result and isNumeric(idx)
    else:
      result = False
    return result
  else:
    return isValNumeric(data)

def isList(val):
  if isinstance(val, list) or isinstance(val, tuple):
    return True
  return False




