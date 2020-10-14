from provider import *
from loadbalancer import *
import time
#sleep to improve readability
print("###### TEST START ######")
print("###### Step 1 ######")
print("generate a provider and invoke get method")
p1 = Provider()
print(p1.get())
LB = LoadBalancer()
print("###### Step 2 ######")
print("###### TRY TO REGISTER 11 PROVIDERS ######")
print("Note: 10 is the maximum number of accepted providers")
for i in range(11):
  LB.register(Provider())
  time.sleep(2)


#if we call the get method multiple times with an interval of less then 2s we get a random provider, if less than 3s a round-robin
print("###### Step 3-4 ######")
print("###### TEST RANDOM AND ROUND ROBIN GET######")
for sec in [1,1,2,2,1,2,2,2,2,2,2,2,2,2,2]:
  LB.get()
  time.sleep(sec)


print("###### Step 5 ######")
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


print("###### Step 6-7 ######")
print("###### Heartbeat checker ######")
print("######PROVIDER OUT OF SERVICE: TEST 1######")
#simulation of a provider out of service and reintegration
prov = LB._registeredProviders[0]
prov.simulateOutOfService(3)
time.sleep(10)
print("######PROVIDER OUT OF SERVICE: TEST 2######")
#simulation of a provider out of service and exclusion
prov.simulateOutOfService(10)
time.sleep(10)

LB.register(prov)

print("###### Step 8 ######")
#Cluster Capacity limit: There will be 1 error because we have 30 workers
print("###### CLUSTER CAPACITY TEST ######")
for i in range(31):
  LB.do_job(i)