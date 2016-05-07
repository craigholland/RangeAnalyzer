import signal_math_func as sig
import datetime as dt
import validations
class StressTest(object):

  def __init__(self, input_val):
    self.iterations = 0
    self.pivotpoint = 50
    self.pivotrange = 10
    self.AddValueCounter = 0
    self.SigObj = sig.RangeAnalysis([])
    self.SigObj.Reset()
    if validations.isNumeric(input_val):
      self.iterations = input_val


  def Start(self):
    self.starttime = dt.datetime.now()
    for i in xrange(self.iterations):
      self.Test()
    self.endtime = dt.datetime.now()

  def Test(self):
    pivot = self.pivotpoint
    for i in xrange(1, 1+self.pivotrange):
      self.SigObj.AddValue([j for j in xrange(pivot - i*2, pivot + i*2)])
      pivot +=1
      self.AddValueCounter +=1

  def Report(self):
    print 'Test Iterations: {0}'.format(self.iterations)
    print 'Values Added: {0}'.format(self.AddValueCounter)
    print 'Start Time: {0}'.format(self.starttime)
    print 'End Time: {0}'.format(self.endtime)
    results = self.endtime - self.starttime
    print 'Total Elapsed Time (sec): {0}'.format(results.total_seconds())
    proc_speed = self.iterations / results.total_seconds()
    print 'Processing Speed (Set): {0} iterations/sec'.format(proc_speed)
    print 'Processing Speed (Churn): {0} Values Added/sec'.format(self.AddValueCounter/results.total_seconds())


