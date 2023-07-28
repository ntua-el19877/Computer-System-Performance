"""
Επιδοση εργασια 2
Λουκάς Άγγελος 03119877
Μαντζαφίνης Αλέξανδρος 03118057
Ομάδα 21

"""


import math
import random
from matplotlib import pyplot as plt
import numpy as np
from tqdm import tqdm

class server:
    def __init__(self):
        self.ArrivalTime =[]   
        self.EndTime=[]
        self.PercentageAtInterrupt=[]
        self.PercentageDone=[]
        self.DiskType=[]
        self.DiskPercentageDone=[]
        self.JobStage=[]
        self.BalkingTime=[]
        self.OutPercentageDone=[]
        self.IndividualTimes=[]  #0:cpu 1:disk1  2:disk2 3:out
        self.N=0
        self.arrival_rate=1.65
        self.NumOfCycles=1000
        self.clockNow=0.0
        self.Event=0
        self.JobsCleared=[]

        self.JobsAtCpu=0
        self.JobsBalked=0
        self.JobsFinished=0

        self.CpuValue=18
        self.DiskAValue=28
        self.DiskBValue=34
        self.OutValue=416

        self.d1Free=True
        self.d2Free=True
        self.OutFree=True
        self.d1Q=[]
        self.d2Q=[]
        self.oQ=[]


    def Poisson_arrivals(self):
        X=-self.NumOfCycles*math.log(random.random())/self.arrival_rate
        return X

    def category(self):
        p_A = 19/31
        x=random.random()
        if x <= p_A:
            return "A"
        else:
            return "B"
        
    def getBalkingTime(self):
        a=1.5
        b=30
        x=random.random()
        h1=a/b*(x/b)**(a-1)
        h2=math.exp(-(x/b)**a)
        return 1000_000*h1*h2

    def addJob(self,Arrival=math.inf):
        if Arrival==math.inf:
            Arrival=self.Poisson_arrivals()
        self.ArrivalTime.append(Arrival+self.clockNow)
        self.EndTime.append(-1)
        self.PercentageAtInterrupt.append(random.random()*self.CpuValue)
        self.PercentageDone.append(0.0)
        self.DiskType.append(self.category())
        self.DiskPercentageDone.append(0.0)
        self.JobStage.append(1)
        self.BalkingTime.append(self.getBalkingTime()+self.clockNow)
        self.OutPercentageDone.append(0.0)
        self.N+=1
        self.JobsAtCpu+=1
        self.IndividualTimes.append([0.0,0.0,0.0,0.0])

    def getEventTime(self,index):
        '''
        Finds how long it takes till it reaches an self.Event point for the job index

        Returns _time that is Δt type
        '''
        # if in a queue return inf
        if index in self.d1Q or index in self.d2Q or index in self.oQ:
            return math.inf
        else:
            try:
                # cpu phase
                if self.JobStage[index]==1:
                    _time=(self.PercentageAtInterrupt[index]-self.PercentageDone[index])*self.JobsAtCpu
                # disk phase
                elif self.JobStage[index]==2:
                    if self.DiskType[index]=='A':
                        _diskValue=self.DiskAValue
                    else:
                        _diskValue=self.DiskBValue
                    _time=(_diskValue-self.DiskPercentageDone[index])
                # cpu return phase
                elif self.JobStage[index]==3:
                    _time=(self.CpuValue-self.PercentageDone[index])*self.JobsAtCpu
                # out phase
                elif self.JobStage[index]==4:
                    _time=self.OutValue-self.OutPercentageDone[index]
                # finished phase
                elif self.JobStage[index]==5 or self.JobStage[index]==6:
                    return math.inf
                #check for balking
            except:
                print("Error at time calculation")
            if _time+self.clockNow>self.BalkingTime[index]:
                _time=self.BalkingTime[index]-self.clockNow
            # balking should have happened
            if _time<0:
                _time=0
            return _time

    def updateLists(self,NewTime,ValueNotUpdate=-1):
        '''
        Updates all the job values with new ones given the time difference of NewTime-self.clockNow

        NewTime is t type
        '''

        for i in range(len(self.ArrivalTime)):
            if not( i in self.d1Q or i in self.d2Q or i in self.oQ) and i!=ValueNotUpdate:
                if self.JobStage[i]==1 or self.JobStage==3:
                    self.PercentageDone[i]+=(NewTime-self.clockNow)/self.JobsAtCpu
                    self.IndividualTimes[i][0]+=NewTime-self.clockNow
                elif self.JobStage[i]==2:
                    self.DiskPercentageDone[i]+=(NewTime-self.clockNow)
                    if self.DiskType=='A':
                        self.IndividualTimes[i][1]+=NewTime-self.clockNow
                    elif self.DiskType=='B':
                        self.IndividualTimes[i][2]+=NewTime-self.clockNow
                elif self.JobStage[i]==4:
                    self.OutPercentageDone[i]+=(NewTime-self.clockNow)
                    self.IndividualTimes[i][3]+=NewTime-self.clockNow
        return

    def reachEvent(self,_EventIndex,_NextEvent):
        '''
        Updates the job till it reaches an self.Event.

        _NextEvent is Δt type
        '''
        # balking
        if _NextEvent+self.clockNow>=self.BalkingTime[_EventIndex]:
            self.JobsBalked+=1
            # update queued indexes
            if self.JobStage[_EventIndex]==2:
                if self.DiskType[_EventIndex]=='A':  
                    if self.d1Q:
                        self.d1Q.pop(0)
                    else: 
                        self.d1Free=True
                    self.IndividualTimes[_EventIndex][1]+=_NextEvent
                elif self.DiskType[_EventIndex]=='B': 
                    if self.d2Q:
                        self.d2Q.pop(0)
                    else:
                        self.d2Free=True
                    self.IndividualTimes[_EventIndex][2]+=_NextEvent
            elif self.JobStage[_EventIndex]==1 or self.JobStage[_EventIndex]==3:
                self.JobsAtCpu-=1
                self.IndividualTimes[_EventIndex][0]+=_NextEvent
            elif self.JobStage[_EventIndex]==4:
                if self.oQ:
                    self.oQ.pop(0)
                else:
                    self.OutFree=True
                self.IndividualTimes[_EventIndex][3]+=_NextEvent

            
            self.JobStage[_EventIndex]=6
            
            self.EndTime[_EventIndex]=_NextEvent+self.clockNow
            # stop job


            return
        
        self.JobStage[_EventIndex]+=1
        # next stage
        if self.JobStage[_EventIndex]==2:
            if self.DiskType[_EventIndex]=='A':
                if not self.d1Free:
                    self.d1Q.append(_EventIndex)
                else:
                    self.d1Free=False
            if self.DiskType[_EventIndex]=='B':
                if not self.d2Free:
                    self.d2Q.append(_EventIndex)
                else:
                    self.d2Free=False
            self.JobsAtCpu-=1
            self.IndividualTimes[_EventIndex][0]+=_NextEvent
        elif self.JobStage[_EventIndex]==3:
            self.JobsAtCpu+=1
            # get next item in disk
            if self.DiskType[_EventIndex]=='A':
                if self.d1Q:
                    self.d1Q.pop(0)
                else:
                    self.d1Free=True
                self.IndividualTimes[_EventIndex][1]+=_NextEvent
            if self.DiskType[_EventIndex]=='B':
                if self.d2Q:
                    self.d2Q.pop(0)
                else:
                    self.d2Free=True
                self.IndividualTimes[_EventIndex][2]+=_NextEvent
        elif self.JobStage[_EventIndex]==4:
            if self.OutFree:
                self.OutFree=False
            else:
                self.oQ.append(_EventIndex)
            self.JobsAtCpu-=1
            self.IndividualTimes[_EventIndex][0]+=_NextEvent
        elif self.JobStage[_EventIndex]==5:
            if self.oQ:
                self.oQ.pop(0)
            else:
                self.OutFree=True
            self.IndividualTimes[_EventIndex][3]+=_NextEvent
            self.JobsFinished+=1
            self.EndTime[_EventIndex]=self.clockNow+_NextEvent
        return

    def checkCycle(self):
        if self.d1Free and self.d2Free and self.JobsAtCpu==0 and self.OutFree:
            self.oldCycles.append(self.clockNow-self.oldCycles[-1])
            self.getR_Cycle()
            return 1
        return 0

    def getR(self):
        Rcpu=0.0
        Rd1=0.0
        Rd2=0.0
        Rout=0.0

        countcpu=0
        countout=0
        countd1=0
        countd2=0

        for i,job in enumerate(self.JobsCleared):
            if not job[6]==6:       #self.JobStage
                Rcpu+=job[9][0]
                Rout+=job[9][3]
                if job[4]=='A':
                    Rd1+=job[9][1]
                    countd1+=1
                elif job[4]=='B':
                    Rd2+=job[9][2]
                    countd2+=1
                countcpu+=1
                countout+=1

        for i,job in enumerate(self.IndividualTimes):
            Rcpu+=job[0]
            Rout+=job[3]
            if self.DiskType[i]=='A':
                Rd1+=job[1]
                countd1+=1
            elif self.DiskType[i]=='B':
                Rd2+=job[2]
                countd2+=1
            countcpu+=1
            countout+=1

        return Rcpu/countcpu,Rd1/countd1,Rd2/countd2,Rout/countout

    def getR_Cycle(self):
        Rcpu=0.0
        Rd1=0.0
        Rd2=0.0
        Rout=0.0

        countcpu=0
        countout=0
        countd1=0
        countd2=0

        for i,job in enumerate(self.JobsCleared):
            if not job[6]==6:       #self.JobStage
                Rcpu+=job[9][0]
                Rout+=job[9][3]
                if job[4]=='A':
                    Rd1+=job[9][1]
                    countd1+=1
                elif job[4]=='B':
                    Rd2+=job[9][2]
                    countd2+=1
                countcpu+=1
                countout+=1

        for i,job in enumerate(self.IndividualTimes):
            Rcpu+=job[0]
            Rout+=job[3]
            if self.DiskType[i]=='A':
                Rd1+=job[1]
                countd1+=1
            elif self.DiskType[i]=='B':
                Rd2+=job[2]
                countd2+=1
            countcpu+=1
            countout+=1

        self.oldResponseTimes.append([Rcpu,Rd1,Rd2,Rout,countcpu,countd1,countd2,countout])

        if countcpu==0:
            countcpu=1
            Rcpu=0
        if countd1==0:
            countd1=1
            Rd1=0
        if countd2==0:
            countd2=1
            Rd2=0
        if countout==0:
            countout=1
            Rout=0
        return Rcpu/countcpu,Rd1/countd1,Rd2/countd2,Rout/countout

    def calcR(self,i):
        Rcpu=self.oldResponseTimes[i+1][0]-self.oldResponseTimes[i][0]
        Rd1=self.oldResponseTimes[i+1][1]-self.oldResponseTimes[i][1]
        Rd2=self.oldResponseTimes[i+1][2]-self.oldResponseTimes[i][2]
        Rout=self.oldResponseTimes[i+1][3]-self.oldResponseTimes[i][3]

        count0=self.oldResponseTimes[i+1][4]-self.oldResponseTimes[i][4]
        count1=self.oldResponseTimes[i+1][5]-self.oldResponseTimes[i][5]
        count2=self.oldResponseTimes[i+1][6]-self.oldResponseTimes[i][6]
        count3=self.oldResponseTimes[i+1][7]-self.oldResponseTimes[i][7]

        if count0==0:
            count0=1
            Rcpu=0
        if count1==0:
            count1=1
            Rd1=0
        if count2==0:
            count2=1
            Rd2=0
        if count3==0:
            count3=1
            Rout=0

        return Rcpu/count0+Rd1/count1+Rd2/count2+Rout/count3

    def main(self):
        time_cpu=0.0
        time_d1=0.0
        time_d2=0.0
        time_out=0.0

        cpu_Event=[]
        d1_Event=[]
        d2_Event=[]
        out_Event=[]

        self.addJob()
        self.clockNow=self.ArrivalTime[0]
        self.Event+=1
        Cycle=0
        self.oldCycles=[self.clockNow]
        self.oldResponseTimes=[]
        self.oldResponseTimes.append([0,0,0,0,0,0,0,0])
    
        while(Cycle<1000):
            

            _Events=[]

            cpu_Event.append(self.JobsAtCpu)
            if self.d1Free:
                d1_Event.append(len(self.d1Q)+1)
            else:
                d1_Event.append(0)
            if self.d2Free:
                d2_Event.append(len(self.d2Q)+1)
            else:
                d2_Event.append(0)
            if self.OutFree:
                out_Event.append(len(self.oQ)+1)
            else:
                out_Event.append(0)

            if Cycle%20 ==0 and Cycle!=0:
            # check the confidence interval every 20 cycles
                count=0
                Rcpu,Rd1,Rd2,Rout=self.getR()
                y_bar=Rcpu+Rd1+Rd2+Rout

                c_bar=0
                for i in range(len(self.oldCycles)-1):
                    c_bar+=self.oldCycles[i+1]-self.oldCycles[i]
                c_bar=c_bar/(len(self.oldCycles)-1)

                self.N = Cycle - 1

                sy = 0
                sc = 0
                syc = 0

                for i in range(1,Cycle):
                    yi=self.calcR(i)
                    ci=self.oldCycles[i+1]-self.oldCycles[i]
                    sy += ( yi- y_bar) ** 2
                    sc += (ci - c_bar) ** 2
                    syc += (yi - y_bar) * (ci - c_bar)

                sy /= self.N - 1
                sc /= self.N - 1
                syc /= self.N - 1
                R = y_bar / c_bar
                s = sy - 2 * R * syc + R ** 2 * sc
                
                # z for 0.95
                z1_a_2 =  1.960
                confidence_interval = z1_a_2 * float(np.sqrt(s)) / (c_bar * float(np.sqrt(self.N)))
                if confidence_interval / R < 0.1:
                    print("DIEEEEEETHHHHH")
                    break



            for i in range(len(self.ArrivalTime)):
                _Events.append(self.getEventTime(i))

            # _NextEvent is Δt type
            if _Events:
                _NextEvent = min(_Events)
            else:
                _NextEvent=math.inf
            _NextArrival=self.Poisson_arrivals()

            #time under utilization
            if self.JobsAtCpu>0:
                time_cpu+=min(_NextArrival,_NextEvent)
            if not self.d1Free:
                time_d1+=min(_NextArrival,_NextEvent)
            if not self.d2Free:
                time_d2+=min(_NextArrival,_NextEvent)
            if not self.OutFree:
                time_out+=min(_NextArrival,_NextEvent)

            # self.Event happens before next arrival
            if _NextArrival>_NextEvent:
                # get which job has the next self.Event
                _EventIndex = _Events.index(_NextEvent)

                self.reachEvent(_EventIndex,_NextEvent)
                self.updateLists(_NextEvent+self.clockNow,_EventIndex)
                self.clockNow=_NextEvent+self.clockNow
                self.Event+=1
                if self.JobStage[_EventIndex]>4:
                    self.JobsCleared.append([
                            self.ArrivalTime.pop(_EventIndex),\
                            self.EndTime.pop(_EventIndex),\
                            self.PercentageAtInterrupt.pop(_EventIndex),\
                            self.PercentageDone.pop(_EventIndex),\
                            self.DiskType.pop(_EventIndex),\
                            self.DiskPercentageDone.pop(_EventIndex),\
                            self.JobStage.pop(_EventIndex),\
                            self.BalkingTime.pop(_EventIndex),\
                            self.OutPercentageDone.pop(_EventIndex),\
                            self.IndividualTimes.pop(_EventIndex)\
                                ])

            else:
                
                self.updateLists(_NextArrival+self.clockNow)
                # NextJob comes before any other self.Event
                self.addJob(Arrival=_NextArrival)
                self.clockNow=_NextArrival+self.clockNow
                self.Event+=1
            
            Cycle+=self.checkCycle()


        Rcpu,Rd1,Rd2,Rout=self.getR()
        R=Rcpu+Rd1+Rd2+Rout
        pjf=round(self.JobsBalked/len(self.JobsCleared)*100,3)
        cu=round(time_cpu/self.clockNow*100,3)
        d1u=round(time_d1/self.clockNow*100 ,3)
        d2u=round(time_d2/self.clockNow*100 ,3)
        ou=round(time_out/self.clockNow*100,3)
        mjrtc=round(Rcpu,3)
        mjrtd1=round(Rd1,3)
        mjrtd2=round(Rd2,3)
        mjrto=round(Rout,3)
        mjrt=round(R,3)
        return [Cycle,self.Event,pjf,cu,d1u,d2u,ou,mjrtc,mjrtd1,mjrtd2,mjrto,mjrt]

epanal=1

L=[0,0,0,0,0,0,0,0,0,0,0,0,0]
with tqdm(total=epanal, ncols=80) as pbar: 
    for i in range(epanal):
        _temp=server()
        L=[x + y for x, y in zip(L, _temp.main())]
        pbar.update(1)

for i in range(len(L)):
    L[i]=round(L[i]/epanal,3)

print('\self.N')
print('-'*40)
print(f"Number of cycles:               {L[0]}")
print(f"Number of events:               {L[1]}")
print('-'*40)
print(f"Percentage of jobs that failed: {L[2]} %")
print(f"Cpu util:                       {L[3]} %")
print(f"Disk 1 util:                    {L[4]} %")
print(f"Disk 2 util:                    {L[5]} %")
print(f"Out util:                       {L[6]} %")
print('-'*40)
print(f"Mean Job responce time Cpu:     {L[7]} msec")
print(f"Mean Job responce time Disk 1:  {L[8]} msec")
print(f"Mean Job responce time Disk 2:  {L[9]} msec")
print(f"Mean Job responce time Out:     {L[10]} msec")
print(f"Mean Job responce time:         {L[11]} msec")
print('-'*40)