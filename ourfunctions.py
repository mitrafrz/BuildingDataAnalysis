import numpy as np
import pandas as pd
#df=pd.read_csv('info.csv') #the main dataframe, containing information of the building's units
df=pd.read_excel('data1.xlsx')
df

#creating functions that return different ratios (in form of float values), for different uses
def r(i:int,RelatedUnits:list): #returns the ratio of unit i's residents, to the sum of residents of all the units belonging to RelatedUnits list
    #filtering out the unwanted units (not included in RelatedUnits) from the main dataframe (df), into a new one (dp)
    dp=df[df['Unit'].isin(list(RelatedUnits))]
    return dp['Residents'][i-1]/sum(dp['Residents'])

def a(i:int,RelatedUnits:list): #returns the ratio of unit i's area, to the sum of areas of all the units belonging to RelatedUnits list
    dp=df[df['Unit'].isin(list(RelatedUnits))]
    return dp['Area'][i-1]/sum(dp['Area'])

def e(i:int,RelatedUnits:list): #used for equal distribution; returns the ratio of counts of unit i (1), to the sum of counts of all units belonging to RelatedUnits list
    return 1/len(RelatedUnits)

#creating functions that mostly recall the previous ones, 
#in case a specific default (of above functions) is not chosen for the attempted distribution
def water(i:int,RelatedUnits:list):
    return r(i,RelatedUnits)

def gas(i:int,RelatedUnits:list):
    dp=df[df['Unit'].isin(list(RelatedUnits))]
    dp['gas']=dp['Area']*np.sqrt(dp['Residents'])  #taking both area and residents into account, with residents playing a less important role
    return (dp['gas'][i-1])/sum(dp['gas'])

def electricity(i:int,RelatedUnits:list):
    return e(i,RelatedUnits)

def avarez(i:int,RelatedUnits:list):
    return e(i,RelatedUnits)

def parking(i:int,RelatedUnits:list): #returns the ratio of unit i's share of parking lots, to the sum of all lots belonging to the units in RelatedUnits list
    dp=df[df['Unit'].isin(list(RelatedUnits))]
    return dp['Parking'][i-1]/sum(dp['Parking'])

def elevator(i:int,RelatedUnits:list): #returns the ratio of the floor number of unit i, to the sum of floor numbers of the units in RelatedUnits list
    dp=df[df['Unit'].isin(list(RelatedUnits))]
    return dp['Floor'][i-1]/sum(dp['Floor'])

#creating a function with arguments of an array of dates, and two other dates as the beggining and end of the interval
#returning an array of bools, showing wether or not each date is inside the given interval
def tarikh_filter(tarikh_array,start,end):
    l=[]
    for tarikh in tarikh_array:
        if((tarikh[0]>start[0] or (tarikh[0]==start[0] and tarikh[1]>start[1]) or (tarikh[0]==start[0] and tarikh[1]==start[1] and tarikh[2]>=start[2]))
        and (tarikh[0]<end[0] or (tarikh[0]==end[0] and tarikh[1]<end[1]) or (tarikh[0]==end[0] and tarikh[1]==end[1] and tarikh[2]<=end[2])) ):
            l.append(1)
        else:
            l.append(0)
    return(np.array(l).astype(bool))


#functions for date conversion
def tojalali(x):
 l1=x.split('/')
 gy=int(l1[0])
 gm=int(l1[1])
 gd=int(l1[2])
 g_d_m=[0,31,59,90,120,151,181,212,243,273,304,334]
 if(gy>1600):
  jy=979
  gy-=1600
 else:
  jy=0
  gy-=621
 if(gm>2):
  gy2=gy+1
 else:
  gy2=gy
 days=(365*gy) +(int((gy2+3)/4)) -(int((gy2+99)/100)) +(int((gy2+399)/400)) -80 +gd +g_d_m[gm-1]
 jy+=33*(int(days/12053))
 days%=12053
 jy+=4*(int(days/1461))
 days%=1461
 if(days > 365):
  jy+=int((days-1)/365)
  days=(days-1)%365
 if(days < 186):
  jm=1+int(days/31)
  jd=1+(days%31)
 else:
  jm=7+int((days-186)/30)
  jd=1+((days-186)%30)
 if jm in range(1,10):
     jm = '0'+str(jm)
 if jd in range(1,10):
     jd = '0'+str(jd) 
 
 return str(jy)+'/'+str(jm)+'/'+str(jd)


###########################
 

def togregorian(x):
 l1=x.split('/')
 jy=int(l1[0])
 jm=int(l1[1])
 jd=int(l1[2])
 if(jy>979):
  gy=1600
  jy-=979
 else:
  gy=621
 if(jm<7):
  days=(jm-1)*31
 else:
  days=((jm-7)*30)+186
 days+=(365*jy) +((int(jy/33))*8) +(int(((jy%33)+3)/4)) +78 +jd
 gy+=400*(int(days/146097))
 days%=146097
 if(days > 36524):
  gy+=100*(int(--days/36524))
  days%=36524
  if(days >= 365):
   days+=1
 gy+=4*(int(days/1461))
 days%=1461
 if(days > 365):
  gy+=int((days-1)/365)
  days=(days-1)%365
 gd=days+1
 if((gy%4==0 and gy%100!=0) or (gy%400==0)):
  kab=29
 else:
  kab=28
 sal_a=[0,31,kab,31,30,31,30,31,31,30,31,30,31]
 gm=0
 while(gm<13):
  v=sal_a[gm]
  if(gd <= v):
   break
  gd-=v
  gm+=1
  
 if gm in range(1,10):
     gm = '0'+str(gm)
 if gd in range(1,10):
     gd = '0'+str(gd) 
  
 return str(gy)+'/'+str(gm)+'/'+str(gd)
