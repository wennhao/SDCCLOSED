#instalation of the RPLidar A1
## information 

this script works on python not on python3

Examples:

- COM3 (_Windows_)
- /dev/ttyUSB0 (_Linux_)
- /dev/tty.usbserial-0001 (_macOS_)

##Setup


```shell
# clone repository
$ git clone https://github.com/Lupin3000/RPLidar.git

# change directory
$ cd RPLidar/
```
# create virtualenv
$ python -m venv venv

# activate virtualenv
$ venv\Scripts\activate

# install packages
$ pip install -r requirements.txt

# show script help
$ python device_info.py -h

##Examples how to run on a 

# display rplidar information and health status (macOS)
$ python device_info.py '/dev/tty.usbserial-0001'

# display rplidar information and health status (Linux)
$ python device_info.py '/dev/ttyUSB0'

# display rplidar information and health status (Windows)
$ python device_info.py 'COM4'


# stop virtualenv
(venv) $ deactivate
 