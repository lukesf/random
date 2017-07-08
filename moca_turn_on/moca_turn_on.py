#!/usr/bin/python
import requests
import os
import time

#test_host = "10.0.0.170" 
test_host = "WECB-0590.local" 
cmd = "ping -c 1 -w 4 -t 5 " + test_host + "  > /dev/null 2>&1"
#print cmd
response = os.system(cmd)

#and then check the response...
if response == 0:
  print test_host, 'is up!'
  exit(0)
else:
  print test_host, 'is down!'

# test host is down :(
# Attempt to turn on Moca on the xfinity router...

# Fill in your details here to be posted to the login form.
payload = {
    'username': 'admin',
    'password': 'mypasswd'
}

myheaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}

# Use 'with' to ensure the session context is closed after use.
#with requests.Session() as s:
s = requests.Session()
p = s.post('http://10.0.0.1/check.php', headers=myheaders, data=payload)
# print the html returned or something more intelligent to see if it's a successful login page.
#print(p.text)
print(p.status_code)

# An authorised request.
# get csrf token
mylink = 'http://10.0.0.1/actionHandler/ajax_at_a_glance.php'
r = s.get(mylink, headers=myheaders)
#print(r.status_code)
#print ("r",r.headers)
#print (r.text)
mycookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(s.cookies))
#print ("Mycookies",mycookies)

# add token to req header  
myheaders['x-csrf-token']=r.headers['x-csrf-token']
myheaders['Referer']=mylink

# goto moca page
mylink2 = 'http://10.0.0.1/moca.php'
r2 = s.post(mylink2,headers=myheaders,data=payload,cookies =mycookies)
print(r2.status_code)
#print (r.text)

myheaders['x-csrf-token']=r.headers['x-csrf-token']
myheaders['Referer']=mylink2

# set moca
myurl = "http://10.0.0.1/actionHandler/ajaxSet_moca_config.php"

mydata = { "configInfo": '{"moca_enable": "true", "thisUser": "admin"}' }
m = requests.post(myurl, data=mydata, headers=myheaders, cookies=mycookies)
print(m.status_code)
#print(m.text)

if m.status_code == 200:
  print 'That may have worked!'
else:
  print "Web interface update didn't work!"

time.sleep(30)

## Ping to see...
cmd = "ping -c 1 -w 4 -t 5 " + test_host + "  > /dev/null 2>&1"
#print cmd
response = os.system(cmd)

#and then check the response...
if response == 0:
  print "Yay, that did the trick", test_host, 'is up!'
else:
  print "Balls, ", test_host, 'is down!'
