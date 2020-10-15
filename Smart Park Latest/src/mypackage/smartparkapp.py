"""
@author: Rajiv.S.Iyer

"""

import pyrebase
import json
import numpy as np
from datetime import datetime, date, timedelta


#Rajiv's Config

firebaseConfig = {
    "apiKey": "AIzaSyDr8BvwNs-JC6s1hSLjyugoqqFouyBZcA8",
    "authDomain": "smartpark-914f1.firebaseapp.com",
    "databaseURL": "https://smartpark-914f1.firebaseio.com",
    "projectId": "smartpark-914f1",
    "storageBucket": "smartpark-914f1.appspot.com",
    "messagingSenderId": "1035585402438",
    "appId": "1:1035585402438:web:6e5bcd1c9efc977799bc47",
    "measurementId": "G-3GYF51ZVT1"
  }

#Rajiv's Config 2
'''
firebaseConfig = {
    "apiKey": "AIzaSyAFZiL2lRvdhqhdgYskCCXsKFnIwrR2FTc",
    "authDomain": "smart-parking-f580f.firebaseapp.com",
    "databaseURL": "https://smart-parking-f580f.firebaseio.com",
    "projectId": "smart-parking-f580f",
    "storageBucket": "smart-parking-f580f.appspot.com",
    "messagingSenderId": "724535193663",
    "appId": "1:724535193663:web:385d64a54e034849a6088a",
    "measurementId": "G-SS1QJP0KXB"
  }
'''

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
#--------------------------------------------------------------------------------
#All Functions Start Here:

'''
Function: ReadConfigValues
Description: Reads the config table from firebase for pre-defined values
Globals config variables are updated
Parameters: None
Return: None
'''
def ReadConfigValues():
    ConfigDataDict = db.child("Config").get()
    LotOpenTime = ConfigDataDict['LotOpenTime']
    LotCloseTime = ConfigDataDict['LotCloseTime']
    dt_LotOpenTime = datetime.strptime(LotOpenTime, '%H:%M:%S')
    dt_LotCloseTime = datetime.strptime(LotCloseTime, '%H:%M:%S')
    MemShiftHours = ConfigDataDict['MemShiftHours']
    
'''
Function: IsCarParked.
Description: Check if a car is parked in the lot by checking the spots table for a
             matching license number with the status of "occupied".
Parameters: lic - license no.
Return: True = Car is Parked
        False = Car is not Parked
'''
def IsCarParked(lic):
    #Get the firebase spots table.
    SpotsData    = db.child("Spots").get()
    #Obtain Spots table as a list.
    SpotsList    = SpotsData.val()
    #Check if the status item in the dictionary value of the spots list item is marked as occupied of the passed license no.
    for i in range(len(SpotsList)):
        if SpotsList[i]['License'] == lic:
            if SpotsList[i]['Status'] == 'Occupied':
                return True
    #Returns false if none of the spots are occupied.
    return False

'''
Function: lookuplicense 
Description: To check if the detected license number is a member by checking the lic with member table.
             If it's a member then it returns a member dictionary object.
Parameters: License.
Return: If true, returns a member dictionary object else none.
'''
def lookuplicense(lic):
    data = db.child("Members").get()
    members=data.val()
    if lic in members:
        return members[lic]
    else:
        return None
    
'''
Function: RegisterCarEntry
Description: This method is called when a car enters the parking lot.
             If successful, the car is alloted a parking spot and registered as "Occupied". 
             If registration fails and error is shown then none returns. 
             Registration can fail if all spots are occupied. 
             Car which are non-members are marked as Outsiders in activity table and spots table.
             If the registration is successful, Local Car Image is uploaded.
Parameters: lic = license no.
            entry_timestamp = Python datetime.timestamp object.
            carlocalpath = local path to the car image file.
Return: spot item - A single spot object from spot table that the car was assigned to.
        None - If no spots are available, prints an error and returns none.
'''    
def RegisterCarEntry(lic,entry_timestamp,carlocalpath):
    
    # Calls the method to get next available spot.
    NextAvailableSpot=FindNextAvailableSpot(lic,entry_timestamp)
    
    # Exits method if none was found.
    if NextAvailableSpot == None:
        print("No spots are available, cannot register your entry")
        return None
    # Get Activity table as dictionary.
    ActivityData = db.child("Activity").get()
    ActivityDict = ActivityData.val()
    
    #Get Sots table as list.
    SpotsData    = db.child("Spots").get()
    SpotsList    = SpotsData.val()
    
    #Get Members table as dictionary.
    MemberData   = db.child("Members").get()
    MembersDict  = MemberData.val()
    
    #Create an empty dictionary for new entry.
    NewActivityRow = {}

    #Create a datetime object from timestamp(machine level long number which represents time).
    dt_entry = datetime.fromtimestamp(entry_timestamp)
    
    #Check if the car being registered is a member or not.
    if (lic in MembersDict): 
        
        #If member, get the reporting time from Members table.
        MemberReportDateTime=MembersDict[lic]['Report_DateTime']
        print('Member DateTime =' + MemberReportDateTime)
        
        #Converting entry time into string format for month, day and year.
        dt_entry_str=dt_entry.strftime("%d-%m-%Y")
        
        #Concatinating date of entry with reporting time of members which will be in string format.
        reportdatetime_str=dt_entry_str+" "+str(MemberReportDateTime).strip()
        print('Member Report DateTime String =' + reportdatetime_str)
        
        #Converting above object from string datatype to datetime datatype. 
        dt_memberreport=datetime.strptime(reportdatetime_str, '%d-%m-%Y %H:%M:%S')
        
        #Adds license no and name of the member to a dictionary. Later on it is appended as an entry to Activity table.
        NewActivityRow['Parker'] = MembersDict[lic]['Name'] 
    
    
    #if the detected license is not a member
    else:
        
        #Converting entry time from datetime format to string datatype. 
        reportdatetime_str=dt_entry.strftime('%d-%m-%Y %H:%M:%S')
        
        #Assigning entry time to report time for outsider(non-member)
        dt_memberreport=dt_entry
        
        #Naming the Parker as "Outsider" while creating entry onto new row.
        NewActivityRow['Parker'] = 'Outsider'
        
    #Making entry time in string format
    dt_entry_str = dt_entry.strftime('%d-%m-%Y %H:%M:%S')
    
    #Check if we this license no is already there in activty dictionary and if so retrieve the existing list of the license
    #else create a new list object which will be updated later to activity dictionary

    if (type(ActivityDict) == None):
        print("Check the state of Firebase Activity Table.")
        return
    if lic in ActivityDict:
        MemberActivityRowList=ActivityDict[lic]       
    else:
        MemberActivityRowList=[]

    #Assigning all the values to the keys of NewActivityRow dictionary(columns) for the given license no.
    #Naturally, Exit Time and Exit DateTime will be filled after calling exit car function.
    NewActivityRow["Report_DateTime"] = reportdatetime_str
    NewActivityRow["Entry_DateTime"]  = dt_entry_str
    NewActivityRow['Exit_Time']       = ""
    NewActivityRow['Exit_DateTime']   = ""
    NewActivityRow['License']         = lic
    NewActivityRow['Report_Time']     = dt_memberreport.timestamp()
    NewActivityRow['Entry_Time']      = dt_entry.timestamp()
    
    #Now we perform early and late calculations which will be later used for smart parking(only for members).
    #We represent early and late time in seconds for each day and assign them accordingly
    #EarlyLate(el) = Report Time - Entry Time
    el=dt_memberreport - dt_entry 
    
    #sec(seconds)
    sec=el.total_seconds()
    print('seconds:',sec)
    
    #If the seconds value is positive or 0 then the member has arrived early
    if sec>=0:
        activity_early = sec
        activity_late  = 0
        
    #If the seconds value is negative then the member has arrived late
    else:
        activity_early  = 0
        activity_late   = sec
        
    #Assigning all the values to the remaining keys of NewActivityRow dictionary for the given license no.
    NewActivityRow['Early'] = activity_early
    NewActivityRow['Late']  = activity_late
    carimageurl = UploadCarImage(lic,entry_timestamp,carlocalpath)
    NewActivityRow['CarImage_Path']   = carimageurl
    NewActivityRow['RecordNo']        = len(MemberActivityRowList)
    NewActivityRow['Spot']            =  NextAvailableSpot   
    l = len(MemberActivityRowList)
    
    #Adding New Activty Row as the newest entry to Activity Table
    #It will either append to an existing license dictionary or create a new list item if it's a new license 
    #that doesnt have a previous activity entry
    db.child("Activity").child(lic).child(l).set(NewActivityRow)
    
    #Updating the Spot Table after registering car entry
    #Note:- 'NextAvailableSpot-1' is done because spot number starts from 1 but indexing starts from 0
    if (NextAvailableSpot != None):
        SpotsList[NextAvailableSpot-1]['Status']  ='Occupied'
        SpotsList[NextAvailableSpot-1]['License'] =lic
        SpotsList[NextAvailableSpot-1]['Parking_Rownum'] = l
        SpotsList[NextAvailableSpot-1]['Entry_DateTime'] = dt_entry_str
        SpotsList[NextAvailableSpot-1]['Parker'] = NewActivityRow['Parker']
        db.child('Spots').child(NextAvailableSpot-1).set(SpotsList[NextAvailableSpot-1])
    
    #Here we calculate the median and average of late and early time for a member and record it into the Member's Table
    #To be used during smart parking allocation.
    if lic in MembersDict:

        MemberActivityRowList=ActivityDict[lic]
        print("Length of member activity row list: ",len("MemberActivityRowList")) 
        Early_list=[]
        Late_list=[]
        for ActivityRow in range(len(MemberActivityRowList)):
            ActivityItemDict = MemberActivityRowList[ActivityRow]
            #print(type(ActivityItemDict))
            activity_early = int(ActivityItemDict['Early'])
            #print(type(activity_early))
            activity_late  = int(ActivityItemDict['Late'])
            #print(type(activity_late))
            Early_list.append(activity_early)
            Late_list.append(activity_late)
            
        #Here we call numpy library methods to calcualte median and average.
        memMedianEarly=np.median(Early_list)
        memMedianLate=np.median(Late_list)
        memAvgEarly=np.average(Early_list)
        memAvgLate=np.average(Late_list)
        print(lic, 'earlymedian', memMedianEarly)
        print(lic, 'latemedian', memMedianLate)
        print(lic, 'earlyavg', memAvgEarly)
        print(lic, 'lateavg', memAvgLate)
        
        #We record the median and average to the Member table.
        if lic in MembersDict:
            db.child("Members").child(lic).child('Median_Early').set(memMedianEarly)
            db.child("Members").child(lic).child('Median_Late').set(memMedianLate)
            db.child("Members").child(lic).child('Avg_Early').set(memAvgEarly)
            db.child("Members").child(lic).child('Avg_Late').set(memAvgLate)
            
    print("********* Car Entry has been successfully registered. *********") 
    print("License: ", lic, " Entry Time: ", dt_entry_str)
    print("***********")
    print("Spot Details:")
    print(SpotsList[NextAvailableSpot-1])
    
    #We return the allocated spot to the caller if the car was successfully registered.
    return NextAvailableSpot

'''
Function: 
Description:
Parameters:
Return:
'''
def FindNextAvailableSpot(lic, entry_timestamp):
    SpotsData    = db.child("Spots").get()
    SpotsList    = SpotsData.val()
    MemberData = db.child("Members").get()
    MembersDict=MemberData.val()
    
    #Create two empty integer lists
    memberspots=[]
    outsiderspots=[]
    
    #Here we are updating integer lists of spot numbers. 
    for i in range(len(SpotsList)):
        if SpotsList[i]['Type']=='Member':
            
            #We want to store the spot number and not the index number into empty lists.
            memberspots.append(i+1)
            
        else:
            outsiderspots.append(i+1)
            
    print('Member Spots=',memberspots)
    print('Outsider Spots=',outsiderspots)
    
    #If Member
    if lic in MembersDict:
        MemberDic=MembersDict[lic]
        
        #Get his/her's pre-assigned spot number
        memspot=int(MemberDic['Assigned_Spot'])
        
        #Check if his/her's pre-assigned spot number is vacant
        #If yes, all good, return spot number to the caller.
        if ((SpotsList[memspot-1]['Status'])=='Vacant'):
            return memspot
        
        #The member's pre-assigned spot is not vacant,
        else:
            
            #Look for a vacant outisder spot
            for j in range(len(outsiderspots)):
                os=outsiderspots[j]
                
                #The first outsider vacant spot is returned
                if (SpotsList[os-1]['Status']=='Vacant'):
                    return os
                
            #If we reach here then there is no vacant outsider spot available.
            #So now we need to search for vacant spots of other members.
            vacantmemspots=[]
            
            #We build a dynamic integer list of vacant member spots. 
            for j in range(len(memberspots)):
                ms=memberspots[j]
                if (SpotsList[ms-1]['Status']=='Vacant'):
                    vacantmemspots.append(ms)
            print("No of vacant member spots= ", len(vacantmemspots))
            
            #If there are no vacant member spots then there are no vacant spots available and we return 'None'.
            if (len(vacantmemspots))==0:
                print("No spots are available. Parking lot is full")
                return None
            
            #Now we have to intelligently pick another member spot to this car if there are some vacant member spot/spots.
            else:
                print('The vacant member spots are= ', vacantmemspots)
                medlatelist=[]
                
                #We build a dynamic list of pre-calculated medians of the members whose spots are vacant
                #as per the vacantmemspots list
                for j in range(len(vacantmemspots)):
                    vs=vacantmemspots[j]
                    spotdict=SpotsList[vs-1]
                    spotreservedlic=spotdict['Reserved_Lic']
                    print("Members's license = ",spotreservedlic, "and reserved spot = ", vs)
                    medlatelist.append(MembersDict[spotreservedlic]['Median_Late'])
                print(medlatelist)
                
                #We find out the lowest median value of late by using min(minimum) method.
                #The lowest median value indicates that this member has arrived late frequenty.
                #Late entries are all negative numbers and we try to pick the worst offender whose median value is most -ve.
                mini=min(medlatelist)
                for j in range(len(medlatelist)):
                    if medlatelist[j]==mini:
                        return vacantmemspots[j]
                return vacantmemspots[0]
            
    #Else looking for a spot for an outsider license number
    else:
        #Check if any of the pre-assigned outsider spots are vacant, if so return that spot.
        for j in range(len(outsiderspots)):
            os=outsiderspots[j]
            if (SpotsList[os-1]['Status']=='Vacant'):
                return os
            
        #Now there are no outsider spots available so we have to choose one of the member's spots to allocate to an outsider car.
        memspotsnotarrived=[]
        print('Member Spots for allocation to outsiders', memberspots)
        for j in range(len(memberspots)):
                ms=memberspots[j]
                spotdict=SpotsList[ms-1]
                if (spotdict['Status']=='Vacant'):
                    spotreservedlic=spotdict['Reserved_Lic']
                    print(spotreservedlic)
                    MemberReportDateTime=MembersDict[spotreservedlic]['Report_DateTime']
                    dt_entry = datetime.fromtimestamp(entry_timestamp)
                    entrydate_str=dt_entry.strftime("%d-%m-%Y")
                    reportdatetime_str=entrydate_str+" "+str(MemberReportDateTime).strip()
                    dt_memberreport=datetime.strptime(reportdatetime_str, '%d-%m-%Y %H:%M:%S')
                    print('Entry DateTime=',dt_entry)
                    print('Member reporting DateTime=', dt_memberreport)
                
                    if dt_entry > dt_memberreport:  #parking allowed
                        memspotsnotarrived.append(ms)
                    else:
                        print('Outsider has arrived before the reporting time.')
                else:
                    print('Occupied Member Spot = ',ms)
                    
        #Now we are looking for member who have not arrived before/ on their reporting time and they are late
        #Because their reporting time has already passed the current entry time of the outsider.
        #We then choose one of those late arrival members based on their median late scores similar to member to member allocation logic above. 
        if len(memspotsnotarrived) > 0:
            print('Members who have not arrived in their spots= ',memspotsnotarrived)
            medlatelist=[]
            for j in range(len(memspotsnotarrived)):
                notarrivedspot=memspotsnotarrived[j]
                spotdict=SpotsList[notarrivedspot-1]
                spotreservedlic=spotdict['Reserved_Lic']
                print(spotreservedlic)
                medlatelist.append(MembersDict[spotreservedlic]['Median_Late'])
            print(medlatelist)
            mini=min(medlatelist)
            for j in range(len(medlatelist)):
                if medlatelist[j]==mini:
                    return memspotsnotarrived[j]
            return memspotsnotarrived[0] 
        else:
            print("No spots are available. Parking lot is full")
            return None
    return None 

'''
Function: 
Description:
Parameters:
Return:
'''
def RegisterCarExit(lic, exit_timestamp):
    ActivityData = db.child("Activity").get()
    ActivityDict=ActivityData.val()
    SpotsData    = db.child("Spots").get()
    SpotsList    = SpotsData.val()
    MemberData   = db.child("Members").get()
    MembersDict  = MemberData.val()
    if lic in ActivityDict:
        MemberActivityRowList=ActivityDict[lic]       
    else:
        print("Car Not Found in the Activity log! Fatal Error! Car Entry not registered before: ",
             lic)
        return None
    ActivityRow = len(MemberActivityRowList) - 1
    ActivityItemDict = MemberActivityRowList[ActivityRow]

    if ActivityItemDict['Exit_DateTime'].strip() != "":
        print("The car has already exited or exit time wasn't empty: ",lic)
        print(ActivityItemDict)
        return None

    dt_exit = datetime.fromtimestamp(exit_timestamp)
    dt_exittime_str=dt_exit.strftime('%d-%m-%Y %H:%M:%S')
    entrytime_timestamp = ActivityItemDict['Entry_Time']

    if  exit_timestamp < entrytime_timestamp:
        print("ERROR! Lic No. " + lic + " Exit Time " + dt_exittime_str + " appears to be less than " + "Entry Time " + ActivityItemDict['Entry_DateTime'])
        return None

    spot = int(ActivityItemDict['Spot'])
    spotstatus = SpotsList[spot-1]['Status']  
    spotlic = SpotsList[spot-1]['License'] 
    if spotstatus != 'Occupied':
        print("Spot allocated doesn't seem occupied. Check data: ", lic)
        print(SpotsList[spot -1])
        return None
    if spotlic != lic:
        print("Spot seems to be occupied but license doesn't match. Occupied license: ", spotlic,
              "The exit time car license passed is: ", lic)
        print(SpotsList[spot -1])
        return None
    
    ActivityItemDict['Exit_DateTime'] = dt_exittime_str
    ActivityItemDict['Exit_Time'] = exit_timestamp
    db.child("Activity").child(lic).child(ActivityRow).set(ActivityItemDict)
    SpotsList[spot-1]['Status'] = 'Vacant' 
    SpotsList[spot-1]['Exit_DateTime'] = dt_exittime_str
    db.child('Spots').child(spot-1).set(SpotsList[spot-1])
    print("******** Car Exit has been successfully registered. ********")
    print("License: ", lic, " Exit Time: ", dt_exittime_str)
    print("********")
    print("Spot Details:")
    print(SpotsList[spot-1])
    return

'''
Function: 
Description:
Parameters:
Return:
'''              
def UploadCarImage(lic,entry_timestamp,carlocalpath):
    storage = firebase.storage()

    #time = datetime.now()
    dt_time = datetime.fromtimestamp(entry_timestamp)
    print ("Current date and time : ")
    datetime_str = dt_time.strftime("%d-%m-%y_%I_%M_%S_%p")
   # time_image = dt_time.strftime("%d%b_%I-%M%p")
    

    date_str = dt_time.strftime("%d-%m-%y")
    local_image_filename = "CAP_{}.png".format(datetime_str)
    remote_img_path = "{0}/{1}/{2}/{3}".format("Captures",date_str,lic,local_image_filename)


  #  local_file_path = "Images/nissan-micra.jpg"
  # storage_file_path = "Captures/"
    fbupload = storage.child(remote_img_path).put(carlocalpath)
    
    image_url = "gs://"+fbupload['bucket']+"/"+fbupload['name']

    print("Image loaded from Local path:",carlocalpath," Being Uploaded to:",image_url)

    return image_url

'''
Function: 
Description:
Parameters:
Return:
'''
def CalcAllMemberMedianAndAverage():
    MemberData = db.child("Members").get()
    MembersDict=MemberData.val()
    ActivityData = db.child("Activity").get()
    ActivityDict=ActivityData.val()
    for lic in ActivityDict:
        MemberActivityRowList=ActivityDict[lic]
        Early_list=[]
        Late_list=[]
        for ActivityRow in range(len(MemberActivityRowList)):
            ActivityItemDict = MemberActivityRowList[ActivityRow]
            #print(type(ActivityItemDict))
            activity_early = int(ActivityItemDict['Early'])
            #print(type(activity_early))
            activity_late  = int(ActivityItemDict['Late'])
            #print(type(activity_late))
            Early_list.append(activity_early)
            Late_list.append(activity_late)
        memMedianEarly=np.median(Early_list)
        memMedianLate=np.median(Late_list)
        memAvgEarly=np.average(Early_list)
        memAvgLate=np.average(Late_list)
        print(lic, 'earlymedian', memMedianEarly)
        print(lic, 'latemedian', memMedianLate)
        print(lic, 'earlyavg', memAvgEarly)
        print(lic, 'lateavg', memAvgLate)
        print("___________________")
        if lic in MembersDict:
            db.child("Members").child(lic).child('Median_Early').set(memMedianEarly)
            db.child("Members").child(lic).child('Median_Late').set(memMedianLate)
            db.child("Members").child(lic).child('Avg_Early').set(memAvgEarly)
            db.child("Members").child(lic).child('Avg_Late').set(memAvgLate)
            
#---------------------------------------------------------------------------------

#Following functions are for data cleanup and data preparations

'''
Function: 
Description:
Parameters:
Return:
'''
def UpdateAllMemberActivityTimeValues():
    ActivityData = db.child("Activity").get()
    ActivityDict=ActivityData.val()
    for m in ActivityDict:
        MemberActivityRowsList=ActivityDict[m]
        #print(type(MemberActivityRowsList))
        print ("Member:",m)
        for i in range(len(MemberActivityRowsList)):
            ActivityRowDict = MemberActivityRowsList[i]
            print(type(ActivityRowDict))
            print("Activity Row Dic:",ActivityRowDict)
            lic = ActivityRowDict['License']
            print("License:",lic)
            if (lookuplicense(lic) != None):
                Report_DateTime = ActivityRowDict['Report_DateTime']
                Entry_DateTime  = ActivityRowDict['Entry_DateTime']
                Exit_DateTime   = ActivityRowDict['Exit_DateTime']
                print("Report date:",Report_DateTime,"Entry date:",Entry_DateTime,"Exit date:",Exit_DateTime)
                print("The Rpt,Entry,Exit:",Report_DateTime,Entry_DateTime,Exit_DateTime)
                if (isinstance(Report_DateTime,str) and isinstance(Entry_DateTime,str)):
                    datetime_rdt = datetime.strptime(str(Report_DateTime.strip()), '%d-%m-%Y %H:%M:%S')
                    datetime_edt = datetime.strptime(str(Entry_DateTime.strip()), '%d-%m-%Y %H:%M:%S')
                    el=datetime_rdt-datetime_edt             
                    sec=el.total_seconds()
                    print('sec:',sec)
                    if sec>=0:
                        activity_early = sec
                        activity_late  = 0
                    else:
                        activity_early  = 0
                        activity_late   = sec
                    ActivityRowDict['Report_DateTime'] = str(Report_DateTime).strip()
                    ActivityRowDict['Entry_DateTime']  = str(Entry_DateTime).strip()
                    
                    ActivityRowDict['Early'] = activity_early
                    ActivityRowDict['Late']  = activity_late
                    ActivityRowDict['Report_Time'] = datetime_rdt.timestamp()
                    ActivityRowDict['Entry_Time']  = datetime_edt.timestamp()

                if (isinstance(Exit_DateTime,str)and str(Exit_DateTime.strip())!= ""):
                    datetime_exitdt = datetime.strptime(str(Exit_DateTime.strip()), '%d-%m-%Y %H:%M:%S')
                    ActivityRowDict['Exit_Time'] = datetime_exitdt.timestamp()
                    ActivityRowDict['Exit_DateTime']   = str(Exit_DateTime).strip()
                
                db.child("Activity").child(m).child(i).set(ActivityRowDict)
                
'''
Function: 
Description:
Parameters:
Return:
'''                
def CleanupAllActivityRecords():
    ActivityData = db.child("Activity").get()
    ActivityDict=ActivityData.val()
    for m in ActivityDict:
        MemberActivityRowsList=ActivityDict[m]
        print(type(MemberActivityRowsList))
        print ("Member:",m)
        for i in range(len(MemberActivityRowsList)-1):
            ActivityRowDict     = MemberActivityRowsList[i]
            ActivityNextRowDict = MemberActivityRowsList[i+1]
            print("i=",i)
            print(m,"\t",ActivityRowDict['License'],"\t",ActivityRowDict['Entry_Time'],"\t",ActivityRowDict['Exit_Time'])
            Exit_Time       = ActivityRowDict['Exit_Time']
            Exit_DateTime   = ActivityRowDict['Exit_DateTime']
            Entry_TimeNext      = ActivityNextRowDict['Entry_Time']
            Entry_DateTimeNext  = ActivityNextRowDict['Entry_DateTime']
            if (isinstance(Exit_DateTime,str) and Exit_DateTime.strip()==""):
                    print("Found a empty Exit Date record!!!!!",m,"i=",i)
                    ActivityRowDict['Exit_Time']       = Entry_TimeNext
                    ActivityRowDict['Exit_DateTime']   = Entry_DateTimeNext
                    db.child("Activity").child(m).child(i).set(ActivityRowDict)
    return

'''
Function: 
Description:
Parameters:
Return:
'''
def UpdateSpotStatusFromActivity():
    SpotsData    = db.child("Spots").get()
    SpotsList    = SpotsData.val()
    print(SpotsList)
    ActivityData = db.child("Activity").get()
    ActivityDict=ActivityData.val()
    for lic in ActivityDict:
        #MemberActivityRowsList = db.child("Activity").child(m).child(0).order_by_child('Entry_Time').get()
        #MemberActivityRowsList = queryRef.get()
        MemberActivityRowsList=ActivityDict[lic]
        print(type(MemberActivityRowsList))
        print ("Member:",lic)
        i = len(MemberActivityRowsList)
        if (i>0):
            ActivityRowDict     = MemberActivityRowsList[i-1]  #last item in the rowlist
            #Report_Time     = ActivityRowDict['Report_Time']
            #Report_DateTime = ActivityRowDict['Report_DateTime']
            #Entry_DateTime  = ActivityRowDict['Entry_DateTime']
            Exit_Time       = ActivityRowDict['Exit_Time']
            Exit_DateTime   = ActivityRowDict['Exit_DateTime']
            Parker_spot     = int(ActivityRowDict['Spot'])
            if ((Parker_spot > 0) and (Parker_spot <= len(SpotsList))):
                
                if (isinstance(Exit_DateTime,str) and Exit_DateTime.strip()==""):
                    SpotsList[Parker_spot-1]['Parker']                = ActivityRowDict['Parker']
                    SpotsList[Parker_spot-1]['License']               = ActivityRowDict['License']
                    SpotsList[Parker_spot-1]['Entry_DateTime']        = ActivityRowDict['Entry_DateTime']
                    SpotsList[Parker_spot-1]['Exit_DateTime']         = ActivityRowDict['Exit_DateTime']
                    SpotsList[Parker_spot-1]['Activity_Rownum']        = ActivityRowDict['RecordNo']
                    SpotsList[Parker_spot-1]['Status']      = "Occupied"
                else:
                    #if (SpotsList[Parker_spot-1]['Status'] != "Occupied"):  #if its already occupied do not overwrite it. 
                        SpotsList[Parker_spot-1]['Parker']                = ActivityRowDict['Parker']
                        SpotsList[Parker_spot-1]['License']               = ActivityRowDict['License']
                        SpotsList[Parker_spot-1]['Entry_DateTime']        = ActivityRowDict['Entry_DateTime']
                        SpotsList[Parker_spot-1]['Exit_DateTime']         = ActivityRowDict['Exit_DateTime']
                        SpotsList[Parker_spot-1]['Activity_Rownum']        = ActivityRowDict['RecordNo']
                        SpotsList[Parker_spot-1]['Status']  = "Vacant"
                    
                print("**************************** Parking Spot :",Parker_spot," Status", SpotsList[Parker_spot-1]['Status'])
    print(SpotsList)
    db.child("Spots").set(SpotsList)
    return

