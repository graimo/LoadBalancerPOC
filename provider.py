#import threading
import time
import multiprocessing


class Provider:
  _idCounter = 0
  _busy = False
  _processes = []
  _alive = True

  def __init__(self):
    Provider._idCounter += 1
    self._id = "Provider"+str(Provider._idCounter)
  def get(self):
    return self._id

#check function as requested
  def check(self):
    return self._alive

#helper function to actually do the job
  def worker(self,job):
    time.sleep(4)
    print(self.get(),":",job)

#returns nb of processes. TODO: improve it by checking the state of the process
  def getNbJobs(self):
    return len(self._processes)

  def doJob(self,job):
    #print("I got a job..")
    p = multiprocessing.Process(target=self.worker, args=([job]))
    p.daemon = True
    p.start()
    self._processes.append(p)
  #True if the object is a provider -- not strictly needed, but inserted for readability
  def isProviderType(provider):
    return type(provider) is Provider
  
  #only for test purpose
  def simulateOutOfService(self,seconds):
    self._alive = False
    time.sleep(seconds)
    self._alive = True
