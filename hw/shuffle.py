import random

def get_the_houmwrk(houmwrk, k):
     result=[]
     pom=houmwrk[:]
     random.shuffle(pom)
     for i in range(len(pom)-k):
          arr=[]
          arr.append(pom[i])
          arr2=[pom[i+1:i+k+1]]
          arr.append(arr2)
          result.append(arr)
     return result