from provider import *
import time
import random
import threading

class LoadBalancer:
  _registeredProviders = []
  _possiblyDeadProviders = {}
  _blacklist = []
  _maximumRegistered = 10
  _lastGetTime = 0
  _roundRobinCounter = -1
  _check_interval = 10
  _maxReqPerProvider = 3
  _queue = {}

  def __init__(self):
    print("Load Balancer created!")
    thread = threading.Thread(target=self.heartbeat_check, args=())
    thread.daemon = True
    thread.start()
  
  #this is a thread running in background
  def heartbeat_check(self):
    while True:
      for prov in self._registeredProviders:
        if not prov.check():
          self._possiblyDeadProviders[prov] = 0
          self.unregister(prov)
          print(prov.get(),"might be dead")
      time.sleep(5)
      #using copy to avoid changing size error in the iteration
      for prov in self._possiblyDeadProviders.copy():
        if prov.check():
          self._possiblyDeadProviders[prov] += 1
          if self._possiblyDeadProviders[prov] == 2:
            self.register(prov)
            del self._possiblyDeadProviders[prov]
            print(prov.get(),"reanimated!")
        else: 
          #Officially dead
          del self._possiblyDeadProviders[prov]
          print(prov.get(), "is dead")

  def get(self):
    print("Hi, I'm the load balancer!")
    #No reason to call the advancedGet if there are 0 providers
    if len(self._registeredProviders) > 0:
      self.advancedGet()

  def roundRobinGet(self):
    self._roundRobinCounter += 1
    if self._roundRobinCounter >= len(self._registeredProviders):
      self._roundRobinCounter = 0
    return self._registeredProviders[self._roundRobinCounter].get()
  
  def randomGet(self):
    prov = random.choice(self._registeredProviders)
    return prov.get()
#if get is called in less than 2sec do a random get
#if get is called in less than 3sec do a round-robin get
  def advancedGet(self):
    currentTime = time.time()
    if (currentTime - self._lastGetTime) < 2:
      print("random: ",self.randomGet())
    elif (currentTime - self._lastGetTime) < 3:
      print("round-robin:",self.roundRobinGet())
    self._lastGetTime = currentTime

#checks if provider is eligible for registration, if not prints why
  def isProviderEligible(self, provider):
    if not Provider.isProviderType(provider):
      print("Error: only Providers can be registered!")
      return False
    if len(self._registeredProviders) >= self._maximumRegistered:
      print("Error: the LoadBalancer is full!")
      return False
    if provider in self._blacklist:
      print("Error: provider blacklisted!")
      return False
    if provider in self._registeredProviders:
      print("Error:",provider.get(),"already registered")
      return False
    return True


  def register(self,provider):
    if self.isProviderEligible(provider):
      self._registeredProviders.append(provider)
      self._queue[provider] = provider.getNbJobs()
      print(provider.get(),"successfully registered")

  def unregister(self,provider):
    #fix to not break the round-robin in case we remove the provider the counter is pointing to
    if self._roundRobinCounter != -1:
      if provider is self._registeredProviders[self._roundRobinCounter]:
        self._roundRobinCounter -= 1
    self._registeredProviders.remove(provider)
    del self._queue[provider]
    print(provider.get(),"removed by the registered providers.")


  def blacklist(self,provider):
    if not Provider.isProviderType(provider):
      print("Error: only Providers can be blacklisted!")
      return
    if provider in self._blacklist:
      print(provider.get(),"already blacklisted!")
      return
    self._blacklist.append(provider)
    print(provider.get(),"blacklisted")
    if provider in self._registeredProviders:
      self._registeredProviders.remove(provider)
      print(provider.get(),"removed by the registered providers.")
  
  def unBlacklist(self,provider):
    if not Provider.isProviderType(provider):
      print("Error: only providers can be un-blacklisted")
      return
    if provider not in self._blacklist:
      print(provider.get(), "is not blacklisted yet.")
    else:
      self._blacklist.remove(provider)
      print(provider.get(),"successfully un-blacklisted!")
    
  #returns 0 if no provider is available, otherwise returns the most available one
  def dispatcher(self):
    prov = min(self._queue, key=self._queue.get)
    if self._queue[prov] >= self._maxReqPerProvider:
      print("Error: providers are full!")
      return 0
    return prov

#helper function to create a thread on which LoadBalancer listens - for future improvements
  def assign_job(self,job,provider):
    provider.doJob(job)

  def do_job(self,job):
    prov = self.dispatcher()
    if prov == 0:
      #providers are full
      return
    #print("Dispatching to",prov.get())
    t = threading.Thread(target=self.assign_job, args=(job,prov))
    t.deamon = True
    self._queue[prov] += 1
    t.start()



