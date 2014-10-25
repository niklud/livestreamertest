from __future__ import division
import threading
import time
import os
from subprocess import Popen
from livestreamer import Livestreamer
import random
import ConfigParser
import datetime

path = os.path.dirname(__file__)



class Channel(threading.Thread):
    quality = 'high'
    wait = 10
    warningLevel = 1
    sleep = 0

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        threadID = self.threadID
        warned = 0
        warnedQuality = 0
        streaming = 0
        startStream = 0
        end_after_done = 0
        currently_dling = 0


        time.sleep(5.00 * float(threadID) / float(ChannelParser.currentSize))
        config = ChannelParser.config
        reason = ''
        print 'added: Section ' + str(threadID) + ', channel ' + config.get(str(threadID), 'channel')
        while True:
            if MainClass.die:  #do main() want you dead?
                reason = 'die == true'
                break
            if not config.has_section(str(threadID)):  #is section still in config
                reason = 'config.has_section == False'
                break
            channel = config.get(str(threadID), 'channel')
            warning_level = int(config.get(str(threadID), 'warning level'))
            wait = int(config.get(str(threadID), 'wait'))
            quality = config.get(str(threadID), 'quality')
            if self.do_sleep():
                continue
            try:  # check for available stream
                livestreamer = Livestreamer()
                plugin = livestreamer.resolve_url(channel)
                plugin = plugin.get_streams()
                keys = plugin.keys()
            except:  #another channel was using plugin causing error, to lazy to make a real lock function
                time.sleep(random.uniform(0.0, 2.0))
                if ChannelParser.printLevel == 1:
                    print 'plugin error: ' + str(threadID) + ', ' + channel
                continue
            if ChannelParser.printLevel == 1:
                print 'checked: ' + str(threadID) + ', ' + channel
            if not keys:  #check if stream is available
                if threadID in ChannelParser.streaming:
                    if warnedQuality and not streaming:
                        warnedQuality = 0
                    ChannelParser.streaming.remove(threadID)
                if streaming:
                    st = datetime.datetime.now().strftime('%H:%M')
                    print '[' + st + '] stream ended: ' + str(threadID) + ', ' + channel
                    currently_dling = 0
                streaming = 0
                warned = 0
                self.sleep += (wait * 10 + 6.00)
                continue
            else:
                streaming = 1

            if quality in keys:  #start or ignore stream
                if not warned:
                    ChannelParser.prev_start = threadID
                if not threadID in ChannelParser.streaming:
                    ChannelParser.streaming.append(threadID)
                warnedQuality = 0
                if warning_level > 1 or startStream:
                    if ChannelParser.dl_stream == 1:
                        if currently_dling == 1:
                            self.sleep += 4.00
                            continue
                        st = datetime.datetime.now().strftime('%H:%M')
                        st2 = datetime.datetime.now().strftime('%d-%m-%Y %H-%M')
                        channel_name = channel.split('/')[-1]
                        args = ' -o ' + ' "' + config.get('config', 'path') + channel_name + '  ' + st2 + '.mkv" ' + channel + ' ' + quality
                        ChannelParser.prev_enabled = threadID
                        print '[' + st + '] starting dl: ' + str(threadID) + ', ' + channel + '\a'
                        args_to_start = 'start "' + channel_name + '" /MIN cmd /C livestreamer.exe ' + args
                        os.system(args_to_start)
                        currently_dling = 1
                        continue
                    else:
                        args = channel + ' ', quality
                        st = datetime.datetime.now().strftime('%H:%M')
                        ChannelParser.prev_enabled = threadID
                        to_print = '[' + st + '] starting stream: ' + str(threadID) + ', ' + channel
                        if warning_level > 1:
                            to_print += '\a'
                        print to_print
                        livestreamer_process = Popen(['livestreamer.exe', args])
                        livestreamer_process.wait()
                        st = datetime.datetime.now().strftime('%H:%M')
                        print '[' + st + '] ending stream: ' + str(threadID) + ', ' + channel
                        self.sleep += 10.00
                        continue
                elif warning_level:
                    if not warned:
                        st = datetime.datetime.now().strftime('%H:%M')
                        print '[' + st + '] stream started: ' + str(threadID) + ', ' + channel + '\a'
                        warned = 1
                        self.sleep += 10
                    else:
                        self.sleep += wait * 10 + 6.00
                else:
                    if not warned:
                        warned = 1
                        st = datetime.datetime.now().strftime('%H:%M')
                        print '[' + st + '] ignored: ' + str(threadID) + ', ' + channel
                    continue
            else:  #quality not in list, show alternatives
                if warning_level:
                    if not warnedQuality:
                        warnedQuality = 1
                        print 'warning: ' + str(
                            threadID) + ', ' + channel + ' does not support ' + quality + '\n' + 'supported formats: ' + ','.join(
                            keys)
                        self.sleep += 10
                    continue
                else:
                    self.sleep += wait * 10 + 2.00
        print 'thread ' + str(threadID) + ' ended: from ' + reason

    def do_sleep(self):
        if ChannelParser.startStream == self.threadID:
            startStream = 1
            self.sleep = 0
            ChannelParser.startStream = -1
        if ChannelParser.endStream == self.threadID:
            startStream = 0
            ChannelParser.endStream = -1
            currently_dling = 0
            if (self.warning_level == 2):
                self.sleep += 21600
        if ChannelParser.sleep:  #do main() want all channels to sleep
            self.sleep += 2.00
        if self.sleep >= 2.00:  #do needed sleep
            time.sleep(2.25 + random.uniform(-0.25, 0.25))
            self.sleep -= 2.00
            return True
        return False

class ChannelParser:
    newThreads = []
    currentSize = 0
    sleep = 0
    config = ConfigParser.RawConfigParser()
    nextSection = 0
    startStream = -1
    endStream = -1
    streaming = []
    printLevel = 0
    prev_start = -1
    prev_enabled = -1
    dl_stream = 1


    @staticmethod
    def updateCurrentSize():
        config = ChannelParser.config
        i = -1
        j = 0
        while True:
            if j >= 10:
                break
            if config.has_section(str(i)):
                i += 1
                j = 0
            else:
                i += 1
                j += 1
        return i - 10

    @staticmethod
    def updateNextSection():
        config = ChannelParser.config
        i = 0
        while True:
            if config.has_section(str(i)):
                i += 1
            else:
                return i

    @staticmethod
    def updateVars():  #load channels from file
        ChannelParser.config.read('channels.ini')
        ChannelParser.currentSize = ChannelParser.updateCurrentSize()
        ChannelParser.nextSection = ChannelParser.updateNextSection()

    @staticmethod
    def writeVar(section, var, value):
        config = ChannelParser.config
        config.set(section, var, value)
        with open('channels.ini', 'wb') as configfile:
            config.write(configfile)

    @staticmethod
    def writeChannelSection(section, values):
        config = ChannelParser.config
        config.add_section(section)
        config.set(section, 'channel', values[0])
        if len(values) > 3:
            config.set(section, 'wait', values[1])
            config.set(section, 'quality', values[2])
            config.set(section, 'warning level', values[3])
        else:
            config.set(section, 'wait', config.get('defaults', 'wait'))
            config.set(section, 'quality', config.get('defaults', 'quality'))
            config.set(section, 'warning level', config.get('defaults', 'warning level'))
        ChannelParser.newThreads.append(section)
        with open('channels.ini', 'wb') as configfile:
            config.write(configfile)

    @staticmethod
    def removeSection(section):
        config = ChannelParser.config
        if config.has_section(section):
            config.remove_section(section)
            with open('channels.ini', 'wb') as configfile:
                config.write(configfile)
        else:
            print 'config does not contain: ' + str(section)

    @staticmethod
    def list():
        config = ChannelParser.config
        for i in range(0, ChannelParser.currentSize + 1):
            if config.has_section(str(i)):
                print 'Section ' + str(i) + ', channel ' + config.get(str(i), 'channel')

    @staticmethod
    def listAll():
        config = ChannelParser.config
        print 'Section | Enabled | Wait | Quality | Channel'
        for i in range(0, ChannelParser.currentSize + 1):
            if config.has_section(str(i)):
                print '    ' + str(i) + '    |    ' + config.get(str(i), 'warning level') + '   |   ' + config.get(
                    str(i), 'wait') + '   |   ' + config.get(str(i), 'quality') + '   |   ' + config.get(str(i),
                                                                                                         'channel')

    @staticmethod
    def listStreams():
        config = ChannelParser.config
        print 'currently streaming:'
        for i in ChannelParser.streaming:
            if config.has_section(str(i)):
                print 'Section ' + str(i) + ', ' + config.get(str(i), 'channel')

    @staticmethod
    def toString():
        print 'currentSize: ' + str(ChannelParser.currentSize)
        print 'sleep: ' + str(ChannelParser.sleep)
        print 'nextSection: ' + str(ChannelParser.nextSection)


class MainClass:
    die = 0

    @staticmethod
    def run():

        config = ChannelParser.config
        newThreads = ChannelParser.newThreads
        ChannelParser.updateVars()
        ChannelParser.toString()
        threads = []
        IOThread = BasicIO(0)
        IOThread.start()
        for i in range(0, ChannelParser.currentSize):  #new threads for all sections
            if config.has_section(str(i)):
                tempThread = Channel(i)
                tempThread.start()
                threads.append(tempThread)
        try:  #keep main() running, updating channel threads and creating new threads
            while not MainClass.die:
                time.sleep(2)
#                ChannelParser.updateVars()
                while newThreads:  # while there are sections that not have threads
                    i = newThreads.pop(0)
                    tempThread = Channel(i)
                    tempThread.start()
                    threads.append(tempThread)
        except:  #kill threads
            MainClass.die = 1
            raise


class BasicIO(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        while not MainClass.die:
            line = raw_input('')
            if not line:
                continue
            line = line.split()
            wordOne = line[0]
            rest = line[1:]
            if wordOne == 'start' or wordOne == 'enable':
                if len(line) > 1:
                    ChannelParser.startStream = int(line[1])
                else:
                    print 'argument?'
            elif wordOne == 's':
                if ChannelParser.prev_start > 0:
                    ChannelParser.startStream = ChannelParser.prev_start
            elif wordOne == 'end' or wordOne == 'disable':
                if len(line) > 1:
                    ChannelParser.endStream = int(line[1])
                else:
                    print 'argument?'
            elif wordOne == 'e' or wordOne == 'a':
                if ChannelParser.prev_enabled > 0:
                    ChannelParser.endStream = ChannelParser.prev_enabled
            elif wordOne == 'add':
                ChannelParser.updateVars()
                ChannelParser.writeChannelSection(str(ChannelParser.nextSection), rest)
            elif wordOne == 'list':
                if rest:
                    if rest[0] == 'streams':
                        ChannelParser.listStreams()
                    else:
                        ChannelParser.listAll()
                else:
                    ChannelParser.list()
            elif wordOne == 'remove':
                if len(line) > 1:
                    ChannelParser.removeSection(line[1])
            elif wordOne == 'change':
                if len(line) > 3 and line[2] in ['wait', 'quality', 'warning', 'channel']:
                    if line[2] == 'warning':
                        line[2] = 'warning level'
                    ChannelParser.writeVar(line[1], line[2], line[3])
                else:
                    print 'argument?'
            elif wordOne == 'die' or wordOne == 'q':
                MainClass.die = 1
            elif wordOne == 'sleep':
                ChannelParser.sleep = not ChannelParser.sleep
            elif wordOne == 'print':
                if rest:
                    ChannelParser.printLevel = int(rest[0])
            elif wordOne == 'dl':
                if rest:
                    ChannelParser.startStream = int(rest[0])
                    ChannelParser.dl_stream = 1
                elif ChannelParser.dl_stream == 0:
                    ChannelParser.dl_stream = 1
                    print 'dl started'
                else:
                    ChannelParser.dl_stream = 0
                    print 'dl ended'
            elif wordOne == 'help':
                print '\n'
                print '  start/enable $section  |  yay'
                print '  s                      |  start last online stream'
                print '  end/disable $section  |  zzzz'
                print '  a/e                      |  disable last enabled stream'
                print '  add $channel/$channel $wait $quality $warningLevel  |  add channel with default or args'
                print '  list/list all/list streams  |  list channels/list everything in config/list currently streaming'
                print '  remove $section  |  removes section from config'
                print '  change $section $var $value  |  change value | $var - wait, quality, warning, channel'
                print '  die/q  |  kill everything nicely'
                print '  sleep  |  nothing happens'
                print '  print $level  |  level 1 for listing when channels are checked'
                print '  dl     | dl $channel   | dl all or dl specific channel'
            else:
                print 'try again'


def main():
    MainClass().run()


if __name__ == "__main__":
    main()

