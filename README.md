livestreamertest
================

**Livestreamertest** (rename pending) is a collaboration project by Acca and BluABK.<br><br>
This application consolidates all your twitch streams in one place, and then listens for when they go live.
It is in a sense, an extension of Livestreamer.
In addition to seeing when people go live, it supports the following:
- Streaming it directly to your mediaplayer (using RTMPDump and Livestreamer).
- Downloading it as a file to your disk, which can be played as it downloads.
- Putting streams on ignore indefinitely or for an extended period of time.
- All the features listed in the table below:

###Available commands and parameters

| Command                                                    | Description                                    |
|:-----------------------------------------------------------|:-----------------------------------------------|
| start&#124;enable [section]                                | start stream                                   |
| s                                                          | start last online stream                       |
| end&#124;disable [section]                                 | stop stream                                    |
| a&#124;e                                                   | disable last run stream                        |
| add [channel] [wait quality warn]                          | add channel                                    |
| list&#124;list [all&#124;streams&#124;dl]                  | channels&#124;config&#124;streaming&#124;dling |
| remove [section]                                           | removes section from config                    |
| change [section] [wait&#124;warn&#124;qual&#124;ch] value  | change value                                   |
| change [wait&#124;qual&#124;warn&#124;ch] value            | change value                                   |
| die&#124;q                                                 | kill everything nicely                         |
| sleep                                                      | nothing happens                                |
| print [level]                                              | debug info (1&#124;2)                          |
| dl [ch]                                                    | dl (channel)                                   |

### Requirements

This application requires the following to be installed on your system:
- <a href="https://github.com/chrippa/livestreamer">Chrippa's Livestreamer</a>
- Python 2.7.4 (Other versions may require minor script modification)


### Additional notes
We made this first and foremost for personal use as the need presented itself, but we're open to suggestions on changes and improvement ;P

#### Aditionally Additional notes
Acca is too lazy to remove this comment about him being lazy ~
