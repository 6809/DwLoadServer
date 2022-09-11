# DWLOAD Server

DWLOAD server implemented in Python (OpenSource, GPL v3 or above).

Connect your Dragon 32 into your PC and LOAD/SAVE basic listings.

![Dragon32DriveWire1small.jpeg](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DwLoadServer/Dragon32DriveWire1small.jpeg "Dragon32DriveWire1small.jpeg")


## Quickstart

```bash
~$ git clone https://github.com/6809/DwLoadServer.git
~$ cd DwLoadServer
~/DwLoadServer$ ./devshell.py run serial
```


## features

* load/save files via DWLOAD
* on-the-fly converting ASCII BASIC listing (see below)
* dynamic "AUTOLOAD.DWL" (see below)
* backup all files on save
* Support [USB Adapter](http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter) and [Becker TCP/IP Interface](http://www.6809.org.uk/xroar/doc/xroar.shtml#Becker-port).

### current state

Tested DWEEBS:

| DWEEB      | example                     | Description                                  |
| ---------- | --------------------------- | -------------------------------------------- |
| **DLOAD**  | `DLOAD`                     | Load `AUTOLOAD.DWL` (Used on Dragon startup) |
| **SAVE**   | `DLOAD"SAVE""MYFILE.BAS"`   | Save BASIC listing                           |
| **RESAVE** | `DLOAD"RESAVE""MYFILE.BAS"` | Save BASIC listing                           |

Implemented DriveWire Transactions:

| hex | dez | DW name           | Description                                                              |
|-----| --- | ----------------- | ------------------------------------------------------------------------ |
| $00 | 0   | OP_NOP            | NOP Transaction -> ignored                                               |
| $01 | 1   | OP_NAMEOBJ_MOUNT  | Mount a file to a virtual drive number                                   |
| $02 | 2   | OP_NAMEOBJ_CREATE | (Does in this implementation the same as OP_NAMEOBJ_MOUNT)               |
| $d2 | 210 | OP_READEX         | Send 256 bytes sector from the DWLOAD server to the client               |
| $57 | 87  | OP_WRITE          | Write 256 bytes sector of data from the client into a file on the server |

### TODO

* enhance `AUTOLOAD.DWL.py`, see: [http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4977](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4977)
* compare checksum
* write unittests

### pyscripts

There is a general machanism to generate DLOAD responses via Python:

* Store in server root a python script, e.g.: "FOO.BAR.py"
* DLOAD the file (without .py extension) on client, e.g.: `DLOAD"FOO.BAR"`

The script will be called via subprocess and it must write the Dragon DOS binary data back to stdout.

Currently, there is only one _pyscript_ file: `AUTOLOAD.DWL.py` (see below)

#### dynamic "AUTOLOAD.DWL"

There exist a way to generate a dynamic DWLOAD menu.
Just copy the file [/dwload-demo-files/AUTOLOAD.DWL.py](https://github.com/6809/DwLoadServer/blob/master/dwload-demo-files/AUTOLOAD.DWL.py) into your server root.

The _pyscript_ reads the server root directory and list all files into the DLOAD menu.
e.g. the server root looks like this:
```
/HOME/FOO/DWLOAD-FILES
  +--- AUTOLOAD.DWL.py
  +--- HEXVIEW.BAS
  +--- TEST.BAS
  \--- SAVE
```

The generated listing looks like this:
```
10 CLS
20 PRINT" *** DYNAMIC MENU ***  14:11:18"
30 PRINT"/HOME/FOO/DWLOAD-FILES"
40 PRINT" 0 - HEXVIEW.BAS"
50 PRINT" 1 - TEST.BAS"
60 PRINT" 2 - SAVE"
70 PRINT"PLEASE SELECT (X FOR RELOAD) !"
80 A$=INKEY$:IF A$="" GOTO 80
90 IF A$="X" THEN DLOAD
100 IF A$="0" THEN DLOAD"HEXVIEW.BAS"
110 IF A$="1" THEN DLOAD"TEST.BAS"
120 IF A$="2" THEN DLOAD"SAVE"
130 GOTO 10
```

s.: [http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4977](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4977)

You must only call **DLOAD** on you Dragon to get this menu. Because a **DLOAD** will request **AUTOLOAD.DWL** and the Python server will all **.py** and call **AUTOLOAD.DWL.py** if exist.

This feature make the following file:

| [/dwload_server/hooks/dynamic_dwl.py](https://github.com/6809/DwLoadServer/blob/master/dwload_server/hooks/dynamic_dwl.py)           | general API to 'pyscript' files |
| [/dwload_server/pyscripts/autoload_dwl.py](https://github.com/6809/DwLoadServer/blob/master/dwload_server/pyscripts/autoload_dwl.py) | generates the DWLOAD menu       |

### on-the-fly converting ASCII BASIC listing

The server read/save ASCII BASIC listing and send/store them to the DWLOAD client on-the-fly.
So you can edit listings on your PC and try them on your Dragon without any external conventions!

e.g.: save
```
10 PRINT"HELLO WORLD!"
DLOAD"SAVE""HELLO.BAS"
DWLOAD
!
OK
```

The server will create two files:

| filename  | format               | description                                                      |
| --------- | -------------------- | ---------------------------------------------------------------- |
| HELLO.DWL | raw tokenized binary | Dragon DOS Binary Format data from the Dragon (256 Bytes padded) |
| HELLO.BAS | ASCII listing        | on-the-fly converted ASCII BASIC listing                         |

e.g. load (and execute):
```
DLOAD"HELLO.BAS"
!HELLO WORLD!
OK
```

(Note: the first `!` is from DWLOAD ROM routine)

The server will read the `HELLO.BAS` ASCII listing and convert is on-the-fly to the needed Dragon DOS Binary Format
and send this back to the Dragon.

This feature make the following files:

| [/dwload_server/hooks/read_ascii.py](https://github.com/6809/DwLoadServer/blob/master/dwload_server/hooks/read_ascii.py) | read ASCII listing and send as binary to client |
| [/dwload_server/hooks/save_ascii.py](https://github.com/6809/DwLoadServer/blob/master/dwload_server/hooks/save_ascii.py) | save binary from client as ASCII on server      |

## installation

Clone sources and bootstrap via [dev-shell](https://github.com/jedie/dev-shell), e.g.:

```bash
~$ git clone https://github.com/6809/DwLoadServer.git
~$ cd DwLoadServer
~/DwLoadServer$ ./devshell.py

...

Developer shell - DWLOAD Server - v0.4.0


Documented commands (use 'help -v' for verbose/'help <topic>' for details):

dev-shell commands
==================
fix_code_style      poetry   pytest     tox
list_venv_packages  publish  pyupgrade  update

DWLOAD Server Commands
======================
run

Uncategorized
=============
alias  help  history  macro  quit  set  shortcuts


(dwload_server) run --help
Usage: run [-h] [--root-dir ROOT_DIR] [--log-level {0, 10, 20, 30, 30, 40, 50, 50, 99, 100}] {becker, serial} ...

optional arguments:
  -h, --help            show this help message and exit
  --root-dir ROOT_DIR
  --log-level {0, 10, 20, 30, 30, 40, 50, 50, 99, 100}
                        Logging level: 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL/FATAL (default: 20)

Interface:
  {becker, serial}
    becker              Use the Becker interface
    serial              Use the serial interface

(dwload_server) run serial
```

You can also run as cli, e.g.: Start serial DWLOAD server:
```bash
~/DwLoadServer$ ./devshell.py run serial
```


## History

* [**dev**](https://github.com/6809/DwLoadServer/compare/v0.5.0...main)
  * ...tbc...
* [11.09.2022 - v0.5.0](https://github.com/6809/DwLoadServer/compare/v0.4.0...v0.5.0)
  * Modernize project
  * Easier bootstrap via dev-shell
* [20.11.2014 - v0.4.0](https://github.com/6809/DwLoadServer/compare/v0.3.0...v0.4.0)
  * dynamic `AUTOLOAD.DWL` via Python script
* [19.11.2014 - v0.3.0](https://github.com/6809/DwLoadServer/compare/v0.2.0...v0.3.0)
  * Convert "ASCII BASIC listing" <-> "Dragon DOS Binary" on-the-fly while read/write
* [17.11.2014 - v0.2.0](https://github.com/6809/DwLoadServer/compare/v0.1.1...v0.2.0)
  * Support Becker and Serial interface.
* 14.11.2014 - v0.1.0 - Create bootstrap file that work under linux and windows.
* 12.11.2014 - v0.0.1 - send a file works rudimentary
* 30.09.2014 - Idea was born: [Forum post 11893](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4946#p11893)

## Links

|                   |                                                                                                                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Forum Thread (en) | [worldofdragon.org](https://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4946)                                                                                            |
| Forum Thread (de) | [forum.classic-computing.de](https://forum.classic-computing.de/forum/index.php?thread/20839-dwload-drivewire-for-everybody-daten%C3%BCbertragung-pc-dragon-32-64/&postID=245227) |
| PyPi              | [https://pypi.python.org/pypi/dwload_server/](https://pypi.python.org/pypi/dwload_server/)                                                                                        |
| Github            | [https://github.com/6809/DwLoadServer](https://github.com/6809/DwLoadServer)                                                                                                      |

some project related links:

* About DWLOAD: [http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4964](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4964)
* DWEEBS application Thread: [http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4968](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4968)
* Dragon 32/64 DriveWire Adapter: [http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter](http://archive.worldofdragon.org/index.php?title=Dragon_32/64_Drivewire_Adapter)
* Drivewire for dummies: [http://archive.worldofdragon.org/index.php?title=Drivewire_for_dummies](http://archive.worldofdragon.org/index.php?title=Drivewire_for_dummies)
* [http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/](http://sourceforge.net/p/drivewireserver/wiki/DriveWire_Specification/)
* [http://sourceforge.net/p/drivewireserver/wiki/](http://sourceforge.net/p/drivewireserver/wiki/)
