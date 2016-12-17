#python3
from datetime import datetime
from nbt import nbt
from subprocess import call
import json
import calendar
import time

# screen -S M -X stuff "pardon user ^M"

class NbtEditor():

    def addLives(self, uuid, logWriter):
        fileLocation = "cringe/playerdata/{0}.dat".format(uuid)
        nbtfile = nbt.NBTFile(fileLocation, 'rb')
        print(nbtfile['BQ_LIVES']['lives'])
        logWriter.write("[{2}][addLives] Adding lives for {0}. Current lives {1}.\n".format(uuid, nbtfile['BQ_LIVES']['lives'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        nbtfile['BQ_LIVES']['lives'].value = 2
        logWriter.write("[{2}][addLives] Added lives for {0}. Current lives {1}.\n".format(uuid, nbtfile['BQ_LIVES']['lives'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        nbtfile.write_file(fileLocation)
        logWriter.write("[{1}][addLives] Wrote to file with updated lives for {0}.\n".format(uuid, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))



class BannedPurger():
    bDict = dict()
    logFile = "unbanLog.log"

    def __init__(self):
        self.logWriter = open(BannedPurger.logFile, 'a')
        self.logWriter.write("[{0}][init] BannedPurger initialized and script started.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        self.nbtManager = NbtEditor()

    def parseBanned(self):
        self.logWriter.write("[{1}][parseBanned] Parsing banned JSON. Current dictionary {0}.\n".format(BannedPurger.bDict, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        fileLocation = "banned-players.json"
        f = open(fileLocation, 'r')
        fileContents = f.read()
        fileJson = json.loads(fileContents)
        pattern = ''
        for x in fileJson:
            name = x['name']
            uuid = x['uuid']
            timeString = x['created']
            timeString = int(time.mktime((datetime.strptime(timeString, "%Y-%m-%d %H:%M:%S %z")).timetuple()))
            if x['reason'] == "Death in Hardcore":
                BannedPurger.bDict[name]=[uuid, timeString]
                self.logWriter.write("[{3}][parseBanned] Adding to dictionary: {0} {1} {2}.\n".format(name, uuid, timeString, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))


    def checkUsers(self):
        self.logWriter.write("[{0}][checkUsers] Checking for bans.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        for x in BannedPurger.bDict:
            uuid = BannedPurger.bDict[x][0]
            etime = BannedPurger.bDict[x][1]
            self.logWriter.write("[{3}][checkUsers] Checking user {0} with UUID {1}. Banned time {2}, current time {4}.\n".format(x, uuid, etime, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), int(calendar.timegm(time.gmtime()))))
            if int(calendar.timegm(time.gmtime())) - BannedPurger.bDict[x][1] > 3600:
                self.logWriter.write("[{3}][checkUsers] Removing ban for {0} with UUID {1}.\n".format(x, uuid, etime, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                print(BannedPurger.bDict[x][0],BannedPurger.bDict[x][1])
                self.nbtManager.addLives(uuid, self.logWriter)
                unbanString = 'screen -S M -X stuff "pardon {0} ^M"'.format(x)
                self.logWriter.write("[{1}][checkUsers] Trying to unban with string: {0}.\n".format(unbanString, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                call(unbanString, shell=True)
                self.logWriter.write("[{3}][checkUsers] Removed ban and added lives for {0} with UUID {1}.\n".format(x, uuid, etime, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        self.logWriter.write("[{1}][checkUsers] Finished checkUsers. Current dictionary {0}.\n".format(BannedPurger.bDict, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))


# Running part
bParser = BannedPurger()
while 1:
    bParser.parseBanned()
    bParser.checkUsers()
    print("Sleeping...")
    time.sleep(60)
