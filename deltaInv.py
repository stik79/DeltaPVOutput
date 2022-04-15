import struct,sys,re
from crc import CRC16
from struct import *
class DeltaInverter:

    inverterNum=0;

   #Known Commands
                 ##StrValue, Format, divisor, units
    
    cmds = {'\x10\x01': ('DC Cur1',0,10.0,'A'),
            '\x10\x02': ('DC Volts1',0,1,'V'),
            '\x10\x03': ('DC Pwr1',0,1,'W'),
            '\x10\x04': ('DC Cur2',0,10.0,'A'),
            '\x10\x05': ('DC Volts2',0,1,'V'),
            '\x10\x06': ('DC Pwr2',0,1,'W'),
            '\x10\x07': ('AC Current',0,10.0,'A'),
            '\x10\x08': ('AC Volts',0,1,'V'),
            '\x10\x09': ('AC Power',0,1,'W'),
            '\x11\x07': ('AC I Avg',0,10.0,'A'),
            '\x11\x08': ('AC V Avg',0,1,'V'),
            '\x11\x09': ('AC P Avg',0,1,'W'),
            '\x13\x03': ('Day Wh',0,1,'Wh'),
            '\x13\x04': ('Uptime',0,1,'min'),
            '\x00\x00': ('Inverter Type',9,0,''),
            '\x00\x01': ('Serial',1,0,''),
            '\x00\x08': ('Part',1,0,''),
            '\x00\x40': ('FW Version',10,0,''),
            '\x20\x05': ('AC Temp',0,1,'o'),
            '\x21\x06': ('DC Temp',0,1,'o')
            };


    #Constructor takes inverter number (incase you have more than 1)
    def __init__(self,inverter=1):
        self.inverterNum=inverter
        self.crcCalc = CRC16()

    #private to do the binary packing of the protocol
    def __buildCmd(self, cmd):
        l = len(cmd)
        crc = self.crcCalc.calcString( struct.pack('BBB%ds'%l,5,self.inverterNum,l,bytes(cmd,'utf-8')))
        lo = crc & (0xff);
        high = (crc>>8) & 0xff;
        return struct.pack('BBBB%dsBBB' %len(cmd),2,5,self.inverterNum,len(cmd),bytes(cmd,'utf-8'),lo,high,3);

    #retrieves the instruction for the given human readable command
    def __findCmd(self,strValue):
        for k,v in self.cmds.items():
            if(v[0]==strValue):
                return k
    #unpacks the given command into an {Instruction} {Value} {Units} string
    def __unpackFormatted(self,cmd):
        if not self.isValidResponse(cmd):
            return "Invalid Response"
        cmdcontents = cmd[1:-3]
        lendata = ord(cmdcontents[2])-2
        try:
            stringName,fmt,divisor,unit = self.cmds[cmdcontents[3:5].decode('utf-8')]
            if fmt==0: ##General Numbers
                resp,invNum,size,instruction,value = struct.unpack('>BBB2sH',cmdcontents)
                value = value / divisor
            elif fmt==1: ##ascii string
                resp,invNum,size,instruction,value = struct.unpack('>BBB2s%ds' %lendata,cmdcontents)
            elif fmt==9: ##Model
                resp,invNum,size,instruction,typeof,model,value = struct.unpack('>BBB2sBB%ds' % (lendata-2),cmdcontents)
                return self.cmds[instruction][0]+": Type:" + str(typeof) + " Model:"  +value
            elif fmt==10: ##FWVersion #
                resp,invNum,size,instruction,ver,major,minor = struct.unpack('>BBB2sBBB',cmdcontents)
                return self.cmds[instruction][0]+": " + str(ver) +"." + str(major)+ "."+ str(minor)
            else:
                resp,invNum,size,instruction,value = struct.unpack('>BBB2s%ds' % lendata,cmdcontents)
            return self.cmds[instruction][0] + ": " + str(value) + " "+unit
        except:
            return "Error parsing string, perhaps unknown instruction"
    
    #Returns the packed command to be sent over serial, 
    #Command includes STX, inverter number, CRC, ETX    
    def getCmdStringFor(self,cmd):
        return self.__buildCmd(self.__findCmd(cmd))

    #Returns a formatted human readble form of a response 
    def getFormattedResponse(self,cmd):
        return self.__unpackFormatted(cmd)

    #Returns a raw value from a response 
    def getValueFromResponse(self,cmd):
        return self.__unpackData(cmd)
 
    #prints out hex values of a command string and the related instruction
    def debugRequestString(self,cmdString):
            cmd = cmdString[4:6]
            strCmd = self.cmds[cmd][0]
            inverter = ord(cmdString[2])
            print(("%s on inverter %d:" % (strCmd,inverter)))
            for ch in cmdString:
                sys.stdout.write("%02X " % ord(ch))
            print ("")

    #checks for a valid STX, ETX and CRC
    def isValidResponse(self,cmd):
        if cmd[1]!= 0x06 or cmd[0]!=0x02 or cmd[len(cmd)-1]!=0x03:
            return False
        cmdcontents = cmd[1:-3]
        crc = self.crcCalc.calcString(cmdcontents)
        lo = crc & (0xff)
        high = (crc>>8) & 0xff
        crcByte = len(cmd)-3
        if cmd[crcByte]!=lo or cmd[crcByte+1]!=high:   
            return False
        return True

    #Returns a raw value from a response 
    def __unpackData(self,cmd):
        if not self.isValidResponse(cmd):
            return "Invalid Response"
        cmdcontents = cmd[1:-3]
        lendata = cmdcontents[2]-2
        try:
            stringName,fmt,divisor,unit = self.cmds[cmdcontents[3:5].decode('utf-8')]
            if fmt==0: ##General Numbers
                resp,invNum,size,instruction,value = struct.unpack('>BBB2sH',cmdcontents)
                value = value / divisor
            elif fmt==1: ##ascii string
                resp,invNum,size,instruction,value = struct.unpack('>BBB2s%ds' %lendata,cmdcontents)
            #    return self.cmds[instruction][0] + ": " + str(value) + " "+unit                 
            elif fmt==9: ##Model
                resp,invNum,size,instruction,typeof,model,value = struct.unpack('>BBB2sBB%ds' % (lendata-2),cmdcontents)
                return ": Type:" + str(typeof) + " Model:"  +value
            elif fmt==10: ##FWVersion #
                resp,invNum,size,instruction,ver,major,minor = struct.unpack('>BBB2sBBB',cmdcontents)
                return str(ver) +"." + str(major)+ "."+ str(minor)
            else:
                resp,invNum,size,instruction,value = struct.unpack('>BBB2s%ds' % lendata,cmdcontents)
            return str(value)
        except:
            return "Error parsing string, perhaps unknown instruction"
