# importing the required module
import matplotlib.pyplot as plt 
import matplotlib as mpl
import argparse
import os
import sys
import re


# Helper functions

def AnalogInputRangeCheck (string) :
	value = int(string)
	if value < 0 or value > 11 :
		return False
	else:
		return True


# Main routine 

parser = argparse.ArgumentParser(description='Display a Chetco calibration table')

parser.add_argument('infile', nargs=1,  type=argparse.FileType('r'), 
					help='Configuration file, required ')
					
parser.add_argument('-dVal', nargs=1, type=argparse.FileType('w'), dest='outfile',
					help='direct DisplayValue table to the specified file ' )					
									
					

args = parser.parse_args()

Version = "1.0"

#  Globals 

Index = []
DisplayValue = []
GraphicIndex = []
N2k = []


# parse file 

ConfigFileList = args.infile[0].readlines()

# pull first line and check 

ConfigLine = ConfigFileList.pop(0)


Command = re.match(r'\[TABLE\]\[([0-9,A-F]{4})\]\[8\]\[256\]' , ConfigLine)

if not Command:
	print('Table header missing or in incorrect format..... Exiting')
	print(ConfigLine)
	exit()
	
BaseAddress = int(Command.group(1), 16)

# Validate base address
if BaseAddress % 2048 == 0:
	AnalogInput = int(BaseAddress / 2048) - 1
	if not AnalogInputRangeCheck(AnalogInput) :
		outstring = 'Analog Base address out of range ....... Exiting'
		print(outstring)
		exit()

#use regular expressions to parse the rest of the file

for ConfigLine in ConfigFileList:

	Command = re.match(r"db '(.{4})([0-9,A-F]{2})([0-9,A-F]{2})';(.*)" ,  ConfigLine)
		
# table line matced

	if Command:
		  DisplayValue.append(Command.group(1))
		  N2k.append(int(Command.group(2),16))
		  GraphicIndex.append(int(Command.group(3),16))
		  continue
		  
# Line unrecognized 
		
	else:
		outstring = 'Line: ' + ConfigLine + 'Not recognized  skipping'
		print(outstring)
		
# config file processing complete

if len(DisplayValue) != 256:
	outstring = 'Table length of ' + str(len(DisplayValue)) + ' is incorrect.  Should be' + \
	' 256.  Exiting ...... '
	print(outstring)
	exit()


#  Generate Display Value file

if args.outfile is not None:
	write_handle = args.outfile[0]
	outstring = 'Display Values from configuration file: ' + args.infile[0].name + '\r\n\r\n'
	write_handle.write(outstring)
	write_handle.write('  Index    Display Value\r\n')
	for n in range(0, 256):
		outstring =  str(n).rjust(8) + DisplayValue[n].rjust(8) + '\n'
		write_handle.write(outstring)
		
#  process plot

# Generate x axis
for x in range(0,256):
	Index.append(x * (2.5 / 255.0))

mpl.rcParams["savefig.directory"] = os.chdir(os.path.dirname(__file__))

fig = plt.figure()
man = plt.get_current_fig_manager()
man.canvas.set_window_title(args.infile[0].name)

plt.plot(Index, GraphicIndex, label='Graphic Index' , color='blue')
plt.plot(Index, N2k, label='N2k' , color='red')

plt.ylim(0,  255)
plt.xlim(0.0 , 2.5)

plt.title('Plot of calibration table: ' + args.infile[0].name + '\n Analog Input: ' + \
	str(AnalogInput))

# naming the x axis 
plt.xlabel('Analog Input Voltage') 
# naming the y axis 
plt.ylabel('Output Value') 

plt.legend()
  
# function to show the plot 
plt.show() 