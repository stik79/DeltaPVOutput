#A simple script to read values from a delta inverter and post them to 
#PVoutput.org

import time, subprocess,serial
from deltaInv import DeltaInverter
from time import localtime, strftime

#PVOutput.org API Values - UPDATE THESE TO YOURS!

#Array of SystemID's that correlate to the inverter number
#ie. the first systemID will be inverter 1, second inverter 2 etc
#the numebr of systemIDs must still be the same as the number of inverter- even if they
#are empty.
#an empty string means don't individually update this inverter on pvoutput.org - just do the totals

SYSTEMIDS=["",""]
#System ID of the total/avg values.
TOTALSYSTEMID=""
APIKEY=""

if __name__ == '__main__':

    #Edit your serial connection as required!!
    connection = serial.Serial('/dev/ttyUSB0',19200,timeout=0.2);
    localtime = time.localtime(time.time())   
 
    t_date = 'd={0}'.format(strftime('%Y%m%d'))
    t_time = 't={0}'.format(strftime('%H:%M'))

    totalWh =0
    totalPower =0
    avgACVolts=0
    avgTempDC=0
    validInv =0

    for index in range(len(SYSTEMIDS)):
	    inv = DeltaInverter(index+1) #init Inverter 1
	    #Get the Daily Energy thus far
	    cmd = inv.getCmdStringFor('Day Wh')
	    connection.write(cmd)
	    response = connection.read(100)
	    #if no response the inverter is asleep
	    if response:
		validInv+=1
        	value = inv.getValueFromResponse(response)
		totalWh+=int(value)
	        t_energy = 'v1={0}'.format(value)

		#instanteous power
	        cmd = inv.getCmdStringFor('AC Power')
        	connection.write(cmd)
	        response = connection.read(100)
	        value = inv.getValueFromResponse(response)
		totalPower+=int(value)
	        t_power = 'v2={0}'.format(value)

		#AC Voltage
	        cmd = inv.getCmdStringFor('AC Volts')
	        connection.write(cmd)
	        response = connection.read(100)
	        value = inv.getValueFromResponse(response)
		avgACVolts+=float(value)
	        t_volts = 'v6={0}'.format(value)

		#Temp - this appears to be onboard somewhere not the heatsink
	        cmd = inv.getCmdStringFor('DC Temp')
	        connection.write(cmd)
	        response = connection.read(100)
	        value = inv.getValueFromResponse(response)
		avgTempDC+=int(value)
	        t_temp = 'v5={0}'.format(value)
		if not SYSTEMIDS[index]=="":

			#Send it all off to PVOutput.org
		        cmd = ['/usr/bin/curl',
        		    '-d', t_date,
		            '-d', t_time,
		            '-d', t_energy,
		            '-d', t_power, 
		            '-d', t_volts,
		            '-d', t_temp,
		            '-H', 'X-Pvoutput-Apikey: ' + APIKEY, 
		            '-H', 'X-Pvoutput-SystemId: ' + SYSTEMID[index], 
		            'http://pvoutput.org/service/r1/addstatus.jsp']
		        ret = subprocess.call (cmd)
	    else:
        	print "No response from inverter %d - shutdown? No Data sent to PVOutput.org"% (index+1)
	
    if validInv !=0:
	print "%d awake Inverters" % validInv	
	avgACVolts=avgACVolts/validInv
	avgTempDC=avgTempDC/validInv

        t_energy = 'v1={0}'.format(totalWh)
        t_power = 'v2={0}'.format(totalPower)
        t_volts = 'v6={0}'.format(avgACVolts)
        t_temp = 'v5={0}'.format(avgTempDC)


	#Send it all off to PVOutput.org
        cmd = ['/usr/bin/curl',
   		    '-d', t_date,
	            '-d', t_time,
	            '-d', t_energy,
	            '-d', t_power, 
	            '-d', t_volts,
	            '-d', t_temp,
	            '-H', 'X-Pvoutput-Apikey: ' + APIKEY, 
	            '-H', 'X-Pvoutput-SystemId: ' + TOTALSYSTEMID, 
	            'http://pvoutput.org/service/r1/addstatus.jsp']
        ret = subprocess.call (cmd)
    else:
       	print "No response from any inverter - shutdown? No Data sent to PVOutput.org"
	

    connection.close()
