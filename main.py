from provider import *
from loadbalancer import *
import time
#sleep to improve readability
print("###### TEST START ######")
LB = LoadBalancer()
print("###### REGISTER 10 PROVIDERS ######")
for i in range(10):
  LB.register(Provider())
  time.sleep(2)

#Cluster Capacity limit: There will be 1 error because we have 30 workers
print("###### CLUSTER CAPACITY TEST ######")
for i in range(31):
  LB.do_job(i)

time.sleep(6)

#if we call the get method multiple times with an interval of less then 2s we get a random provider, if less than 3s a round-robin
print("###### TEST RANDOM GET AND ROUND ROBIN ######")
for sec in [1,1,2,2,1,2,2,2,2,2,2,2,2,2,2]:
  LB.get()
  time.sleep(sec)

print("######PROVIDER OUT OF SERVICE: TEST 1######")
#simulation of a provider out of service and reintegration
LB._registeredProviders[0].simulateOutOfService(3)
time.sleep(10)
print("######PROVIDER OUT OF SERVICE: TEST 2######")
#simulation of a provider out of service and exclusion
LB._registeredProviders[0].simulateOutOfService(10)
time.sleep(10)



print("######PROVIDER: MANUAL INCLUSION AND EXCLUSION######")
#manual exclusion and inclusion
p1 = LB._registeredProviders[0]
time.sleep(2)
LB.unregister(p1)
time.sleep(2)
LB.register(p1)
print("######BLACKLIST TEST######")
#blacklist and unblacklist
LB.blacklist(p1)
time.sleep(2)
LB.register(p1)
time.sleep(2)
LB.unBlacklist(p1)
time.sleep(2)
LB.register(p1)
