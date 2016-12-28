#python3
from datetime import datetime
from nbt import nbt
from subprocess import call
import json
import calendar
import time
import os.path

# screen -S M -X stuff "pardon user ^M"

ITERATIONS_BETWEEN_MESSAGES = 8
TIME_TO_SLEEP = 60
LIVES_TO_GIVE = 1
MESSAGE_FILE = "serverMessages.txt"
BAN_LIST_FILE = "serverBanStats.json"

class BanCounter():
    logFile = "bancounter.log"

    def __init__(self):
        self.logger = open(BanCounter.logFile, 'a')
        self.logger.write("[{0}][init] BanCounter initialized.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        self.logger.flush()

        if os.path.isfile(BAN_LIST_FILE):
            f = open(BAN_LIST_FILE, 'r')
            fileContents = f.read()
            self.banJson = json.loads(fileContents)
            f.close()
        else:
            f = open(BAN_LIST_FILE, 'w+')
            f.write("[]")
            f.flush()
            f.close()
            f = open(BAN_LIST_FILE, 'r')
            contents = f.read()
            self.banJson = json.loads(contents)
        self.logger.write("[{0}][init] BanCounter loaded json: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.banJson))
        self.logger.flush()

    def dumpList(self):
        self.logger.write("[{0}][dumpList] Dumping json: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.banJson))
        self.logger.flush()
        print(self.banJson)

    def checkDeaths(self, bannedUUID):
        self.logger.write("[{0}][checkDeaths] Checking death for: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), bannedUUID))
        for user in self.banJson:
            if user['uuid'] == bannedUUID:
                self.logger.write("[{0}][checkDeaths] Deaths: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), user['ban-count']))
                if user['ban-count'] >= 24:
                    self.logger.flush()
                    return 24
                else:
                    self.logger.flush()
                    return user['ban-count']
        self.logger.write("[{0}][checkDeaths] No deaths: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 0))
        self.logger.flush()
        return 0

    def addDeath(self, bannedUUID):
        self.dumpList()
        self.logger.write("[{0}][addDeath] Adding death for: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), bannedUUID))
        for user in self.banJson:
            if user['uuid'] == bannedUUID:
                self.logger.write("[{0}][addDeath] Adding death from: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), user['ban-count']))
                user['ban-count'] = user['ban-count'] + 1
                self.writeFile()
                self.logger.flush()
                return
        self.logger.write("[{0}][addDeath] Creating death object for: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), bannedUUID))
        newJsonString = {}
        newJsonString['uuid'] = bannedUUID
        newJsonString['ban-count'] = 1
        jObject = json.dumps(newJsonString)
        print(jObject)
        print(newJsonString)
        self.banJson.append(newJsonString)
        self.logger.write("[{0}][addDeath] Created object: {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), newJsonString))
        self.logger.flush()
        self.writeFile()
        self.dumpList()

    def writeFile(self):
        self.logger.write("[{0}][writeFile] Writing to file : {1}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.banJson))
        self.logger.flush()
        f = open(BAN_LIST_FILE, 'w')
        f.write(json.dumps(self.banJson))
        f.close()

    def updateJson(self):
        f = open(BAN_LIST_FILE, 'r')
        fileContents = f.read()
        newBanJson = json.loads(fileContents)
        self.logger.write("[{0}][updateJson] Updating json from: {1} , to: {2}.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.banJson, newBanJson))
        self.banJson = newBanJson
        f.close()

class MessageSender():

    def __init__(self):
        self.messageCount = 0
        self.currentMessage = 0
        self.messageSet = set()

    def checkMessages(self):
        fileLocation = MESSAGE_FILE
        with open(fileLocation, 'r') as file:
            for line in file:
                if line not in self.messageSet:
                    self.messageSet.add(line)
        self.messageCount = len(self.messageSet)

    def sendMessage(self):
        messageString = "date"
        counter = 0
        for x in self.messageSet:
            if self.currentMessage == counter:
                while x[len(x)-1].isspace():
                    x = x[:len(x)-1]
                messageString = 'screen -S M -X stuff "say {0} ^M"'.format(x)
                call(messageString, shell=True)
                print(messageString)
                self.currentMessage = self.currentMessage + 1
                if self.currentMessage == self.messageCount:
                    self.currentMessage = 0
                break
            else:
                counter = counter + 1


class NbtEditor():

    def addLives(self, uuid, logWriter):
        fileLocation = "cringe/playerdata/{0}.dat".format(uuid)
        nbtfile = nbt.NBTFile(fileLocation, 'rb')
        print(nbtfile['BQ_LIVES']['lives'])
        logWriter.write("[{2}][addLives] Adding lives for {0}. Current lives {1}.\n".format(uuid, nbtfile['BQ_LIVES']['lives'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        nbtfile['BQ_LIVES']['lives'].value = LIVES_TO_GIVE
        logWriter.write("[{2}][addLives] Added lives for {0}. Current lives {1}.\n".format(uuid, nbtfile['BQ_LIVES']['lives'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        nbtfile.write_file(fileLocation)
        logWriter.write("[{1}][addLives] Wrote to file with updated lives for {0}.\n".format(uuid, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        logWriter.flush()


class LocalBanned():
    fileLocation = "banned-player-local.json"

    def __init__(self):
        if os.path.isfile(LocalBanned.fileLocation):
            f = open(LocalBanned.fileLocation, 'r')
            fileContents = f.read()
            self.jsonFile = json.loads(fileContents)
            f.close()
        else:
            f = open(LocalBanned.fileLocation, 'w')
            f.write("[]")
            f.flush()
            f.close()
            f = open(LocalBanned.fileLocation, 'r')
            fileContents = f.read()
            self.jsonFile = json.loads(fileContents)
        print(self.jsonFile)

    def addBanned(self, uuid, timestamp):
        ob = {}
        ob['uuid'] = uuid
        ob['bantime'] = timestamp
        self.jsonFile.append(ob)
        self.writeFile()

    def getBannedTime(self, uuid):
        self.updateJson()
        for x in self.jsonFile:
            if x['uuid'] == uuid:
                return x['bantime']
        print("User not found? How could this happen... Returning 0")
        return 0

    def removeUser(self, uuid):
        print("before removing user")
        self.dumpJson()
        newJ = []
        for x in self.jsonFile:
            if x['uuid'] != uuid:
                newJ.append(x)
                return
        self.jsonFile = newJ
        print("after removing")
        self.dumpJson()
        self.writeFile()

    def updateJson(self):
        f = open(LocalBanned.fileLocation, 'r')
        fileContents = f.read()
        self.jsonFile = json.loads(fileContents)
        f.close()

    def writeFile(self):
        print("Before writing")
        self.dumpJson()
        f = open(LocalBanned.fileLocation, 'w')
        f.write(json.dumps(self.jsonFile))
        f.flush()
        f.close()
        self.updateJson()
        print("After writing")
        self.dumpJson()

    def dumpJson(self):
        print(self.jsonFile)

    def getJson(self):
        return self.jsonFile

class BannedPurger():
    logFile = "unbanLog.log"

    def __init__(self):
        self.logWriter = open(BannedPurger.logFile, 'a')
        self.logWriter.write("[{0}][init] BannedPurger initialized and script started.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        self.logWriter.flush()
        self.nbtManager = NbtEditor()

    def parseBanned(self, bCounter, localBans):
        self.bDict = dict()
        self.logWriter.write("[{1}][parseBanned] Parsing banned JSON. Current dictionary {0}.\n".format(self.bDict, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
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
            if x['reason'].startswith("Death in Hardcore"):
                if x['reason'] == "Death in Hardcore":
                    self.logWriter.write("[{3}][parseBanned] Adding user to local ban list: {0} {1} {2}.\n".format(name, uuid, timeString, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    localBans.addBanned(uuid, timeString)
                self.bDict[name]=[uuid, timeString]
                self.logWriter.write("[{3}][parseBanned] Adding to dictionary: {0} {1} {2}.\n".format(name, uuid, timeString, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                banHours = (bCounter.checkDeaths(uuid) + 1) * 7200
                timePassed = int(calendar.timegm(time.gmtime())) - localBans.getBannedTime(uuid)
                m, s = divmod(banHours - timePassed, 60)
                h, m = divmod(m, 60)
                banString = 'screen -S M -X stuff "ban {0} Death in Hardcore. You are still banned for {1} hours {2} minutes.^M"'.format(name, h, m)
                call(banString, shell=True)
                print(banString)
                self.logWriter.write("[{3}][parseBanned] Sending to screen: {0}.\n".format(banString, uuid, timeString, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        self.logWriter.flush()

        js = localBans.getJson()
        print(js)
        for x in js:
            chk = 1
            for j in fileJson:
                if j['uuid'] == x['uuid']:
                    chk = 0
                    break
            if chk == 1:
                print("UUID not found: ", x['uuid'])
                localBans.removeUser(x['uuid'])


    def checkUsers(self, bCounter, localBans):
        self.logWriter.write("[{0}][checkUsers] Checking for bans.\n".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        for x in self.bDict:
            uuid = self.bDict[x][0]
            self.logWriter.write("[{3}][checkUsers] Checking user {0} with UUID {1}. Banned time {2}, current time {4}.\n".format(x, uuid, localBans.getBannedTime(uuid), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), int(calendar.timegm(time.gmtime()))))
            bannedTime = (bCounter.checkDeaths(uuid) + 1) * 7200
            if int(calendar.timegm(time.gmtime())) - localBans.getBannedTime(uuid) > bannedTime:
                bCounter.addDeath(uuid)
                localBans.removeUser(uuid)
                self.logWriter.write("[{2}][checkUsers] Removing ban for {0} with UUID {1}.\n".format(x, uuid, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                print(self.bDict[x][0], self.bDict[x][1])
                self.nbtManager.addLives(uuid, self.logWriter)
                unbanString = 'screen -S M -X stuff "pardon {0} ^M"'.format(x)
                self.logWriter.write("[{1}][checkUsers] Trying to unban with string: {0}.\n".format(unbanString, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                call(unbanString, shell=True)
                self.logWriter.write("[{2}][checkUsers] Removed ban and added lives for {0} with UUID {1}.\n".format(x, uuid, time.localtime()))
        self.logWriter.write("[{1}][checkUsers] Finished checkUsers. Current dictionary {0}.\n".format(self.bDict, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        del self.bDict
        self.logWriter.flush()


# Running part


bParser = BannedPurger()
mSender = MessageSender()
bCounter = BanCounter()
lBanned = LocalBanned()
mCounter = 0
while 1:
    bCounter.updateJson()
    bParser.parseBanned(bCounter, lBanned)
    bParser.checkUsers(bCounter, lBanned)
    print("Sleeping...")
    time.sleep(TIME_TO_SLEEP)
    mCounter = mCounter + 1
    if mCounter == ITERATIONS_BETWEEN_MESSAGES:
        mSender.checkMessages()
        mSender.sendMessage()
        mCounter = 0
