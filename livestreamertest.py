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
    warning_level = 1
    sleep = 0
    warned = 0
    warned_quality = 0
    streaming = 0
    start_stream = 0
    end_after_done = 0
    currently_dling = 0
    channel = ""

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.thread_id = threadID
        self.config = ChannelParser.config

    def run(self):
        time.sleep(5.00 * float(self.thread_id) / float(ChannelParser.currentSize))
        reason = ''
        print 'added: Section ' + str(self.thread_id) + ', channel ' + self.config.get(str(self.thread_id), 'channel')

        while True:
            #do main() want you dead?
            if MainClass.die:
                reason = 'die == true'
                break
            #is section still in config
            if not self.config.has_section(str(self.thread_id)):
                reason = 'config.has_section == False'
                break
            self.update_vars()
            #sleep for set amount of time
            if self.do_sleep():
                continue
            #check for available stream
            try:
                livestreamer = Livestreamer()
                plugin = livestreamer.resolve_url(self.channel)
                plugin = plugin.get_streams()
                keys = plugin.keys()
            #another channel was using plugin causing error, to lazy to make a real lock function
            except:
                time.sleep(random.uniform(0.0, 2.0))
                if self.ChannelParser.printLevel == 1:
                    print 'plugin error: ' + str(self.thread_id) + ', ' + self.channel
                continue
            if ChannelParser.printLevel == 1:
                print 'checked: ' + str(self.thread_id) + ', ' + self.channel
            #check if stream is available
            if not keys:
                self.no_stream_avail()
                continue
            else:
                self.streaming = 1
            #start or ignore stream
            if self.quality in keys:
                if not self.warned:
                    ChannelParser.prev_start = self.thread_id
                if not self.thread_id in ChannelParser.streaming:
                    ChannelParser.streaming.append(self.thread_id)
                self.warned_quality = 0
                if self.warning_level > 1 or self.start_stream:
                    if ChannelParser.dl_stream == 1:
                        if self.currently_dling == 1:
                            self.sleep += 4.00
                            continue
                        st = datetime.datetime.now().strftime('%H:%M')
                        st2 = datetime.datetime.now().strftime('%d-%m-%Y %H-%M')
                        channel_name = self.channel.split('/')[-1]
                        args = ' -o ' + ' "' + self.config.get('config', 'path') + channel_name + '  ' + st2 + \
                               '.mkv" ' + self.channel + ' ' + self.quality
                        ChannelParser.prev_enabled = self.thread_id
                        print '[' + st + '] starting dl: ' + str(self.thread_id) + ', ' + self.channel + '\a'
                        args_to_start = 'start "' + channel_name + '" /MIN cmd /C livestreamer.exe ' + args
                        os.system(args_to_start)
                        self.currently_dling = 1
                        continue
                    else:
                        args = self.channel + ' ', self.quality
                        st = datetime.datetime.now().strftime('%H:%M')
                        ChannelParser.prev_enabled = self.thread_id
                        to_print = '[' + st + '] starting stream: ' + str(self.thread_id) + ', ' + self.channel
                        if self.warning_level > 1:
                            to_print += '\a'
                        print to_print
                        livestreamer_process = Popen(['livestreamer.exe', args])
                        livestreamer_process.wait()
                        st = datetime.datetime.now().strftime('%H:%M')
                        print '[' + st + '] ending stream: ' + str(self.thread_id) + ', ' + self.channel
                        self.sleep += 10.00
                        continue
                elif self.warning_level:
                    if not self.warned:
                        st = datetime.datetime.now().strftime('%H:%M')
                        print '[' + st + '] stream started: ' + str(self.thread_id) + ', ' + self.channel + '\a'
                        self.warned = 1
                        self.sleep += 10
                    else:
                        self.sleep += self.wait * 10 + 6.00
                else:
                    if not self.warned:
                        self.warned = 1
                        st = datetime.datetime.now().strftime('%H:%M')
                        print '[' + st + '] ignored: ' + str(self.thread_id) + ', ' + self.channel
                    continue
            #quality not in list, show alternatives
            else:
                if self.warning_level:
                    if not self.warned_quality:
                        self.warned_quality = 1
                        print 'warning: ' + str(
                            self.thread_id) + ', ' + self.channel + ' does not support ' + self.quality + '\n' + \
                            'supported formats: ' + ','.join(keys)
                        self.sleep += 10
                    continue
                else:
                    self.sleep += self.wait * 10 + 2.00
        print 'thread ' + str(self.thread_id) + ' ended: from ' + reason

    def update_vars(self):
        self.channel = self.config.get(str(self.thread_id), 'channel')
        self.warning_level = int(self.config.get(str(self.thread_id), 'warning level'))
        self.wait = int(self.config.get(str(self.thread_id), 'wait'))
        self.quality = self.config.get(str(self.thread_id), 'quality')

    def do_sleep(self):
        if ChannelParser.startStream == self.thread_id:
            self.start_stream = 1
            self.sleep = 0
            ChannelParser.startStream = -1
        if ChannelParser.endStream == self.thread_id:
            self.start_stream = 0
            ChannelParser.endStream = -1
            self.currently_dling = 0
            if (self.warning_level == 2):
                self.sleep += 21600
        #do main() want all channels to sleep
        if ChannelParser.sleep:
            self.sleep += 2.00
        #do needed sleep
        if self.sleep >= 2.00:
            time.sleep(2.25 + random.uniform(-0.25, 0.25))
            self.sleep -= 2.00
            return True
        return False

    def no_stream_avail(self):
        if self.thread_id in ChannelParser.streaming:
            if self.warned_quality and not self.streaming:
                self.warned_quality = 0
            ChannelParser.streaming.remove(self.thread_id)
        if self.streaming:
            st = datetime.datetime.now().strftime('%H:%M')
            print '[' + st + '] stream ended: ' + str(self.thread_id) + ', ' + self.channel
            self.currently_dling = 0
        self.streaming = 0
        self.warned = 0
        self.sleep += (self.wait * 10 + 6.00)


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

