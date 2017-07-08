# moca_turn_on

I use moca for a wifi repeater. xfinity turns off moca to prevent interference with their DVR. I don't use their DVR service. Instead I have a filter on the upstream cable. 
This script checks to see if I can see the repeater. If not it logs into the xfinity box and reenables moca. I call the script using a cron job to check every few minutes.
