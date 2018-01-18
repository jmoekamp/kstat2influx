#!/usr/bin/python

import subprocess
import time
import platform
import requests
import sys
import ConfigParser

configfilename=sys.argv[1]
config = ConfigParser.ConfigParser()
config.read(configfilename)

payload="" 
linecount=0

ip=config.get('main','ip')
db=config.get('main','db')
username=config.get('main','username')
password=config.get('main','password')
debug=config.getboolean('main','debug')

timestamp=int(time.time()*1000*1000*1000)
if debug:
 print timestamp 

hostname=platform.node()
if debug:
 print hostname

kstat = subprocess.Popen('kstat -p'.split(), stdout=subprocess.PIPE)
output = kstat.communicate()[0]
kstat.stdout.close()

lines=output.splitlines() 

for line in lines:
 if "class" in line:
  continue 
 if "snaptime" in line:
  continue
 if "crtime" in line:
  continue
 linecount=linecount+1
 kstatkeyvalue=line.split("\t")
 kstatkeyvalue[0]=kstatkeyvalue[0].replace(" ","_")
 kstatkeyvalue[0]=kstatkeyvalue[0].replace(",","_")
 kstatkeyvalue[0]=kstatkeyvalue[0].replace("!","_")
 kstatkeyvalue[0]=kstatkeyvalue[0].replace("=","_")
 kstatkey=kstatkeyvalue[0].split(":")
 module=kstatkey[0]
 instance=kstatkey[1]
 name=kstatkey[2]
 statistic=kstatkey[3]
 value=kstatkeyvalue[1]
 if value=="":
  continue 
 if value.upper().isupper():
  payload=payload+"kstat,host="+hostname+",module="+module+",instance="+instance+",name="+name+",statistic="+statistic+" valuestring=\""+value+"\" "+str(timestamp)+"\n" 
 else: 
  value=value.replace(",",".")
  payload=payload+"kstat,host="+hostname+",module="+module+",instance="+instance+",name="+name+",statistic="+statistic+" value="+value+" "+str(timestamp)+"\n"
 if linecount==500:
  r = requests.post('http://'+ip+':8086/write?db='+db,auth=(username, password), data=payload)
  if debug:
   if r.text!="":
    print (r.text) 
  payload=""   
  linecount = 0
   
