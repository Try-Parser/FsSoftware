# FsSoftware

## Raspberry pi 3 + GT-521F52 Scanner

### Python3.6.3

#### - Installation 
````
  sudo apt-get update && apt-get upgrade

  sudo apt-get install build-essential checkinstall
  
  sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
  
  wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz

  tar xvf Python-3.6.3.tgz
  cd Python-3.6.3/

  ./configure --enable-optimizations --with-ssl

  make && make altinstall
````

#### - Installation of libs
````
    pip3.6 install 'pyserial==3.4' && pip3.6 install 'websocket-client==0.48.0'
    pip3.6 install 'RPi.GPIO==0.6.5'
    pip3.6 install 'pyyaml==3.12'
    pip3.6 install 'requests==2.21.0'
````

#### - Daemonize
````
    sudo crontab -e
    @reboot sudo python3.6 /opt/FsSoftware/EzABS.py > /opt/FsSoftware/raw_log.txt 2> /opt/FsSoftware/err_logs.txt
    
    sudo vim /home/pi/.config/lxsession/LXDE-pi/autostart
    @chromium-browser --start-fullscreen http://192.168.0.253:80/display
````

#### - Resources Link

[Data Sheet] ( https://cdn.sparkfun.com/assets/learn_tutorials/7/2/3/GT-521F52_Programming_guide_V10_20161001.pdf )

[Wiring] ( https://cdn.sparkfun.com/assets/learn_tutorials/7/2/3/GT-521FX2_datasheet_V1.1__003_.pdf )
