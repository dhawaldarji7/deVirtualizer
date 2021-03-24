#!/usr/bin/python3

"""
A Deobfuscator for a Virtual Machine based Obfuscator
Author: Dhawal Darji

This tool tries to devirtualize and deobfuscate a virtual-machine(VM) based obfuscated code.
This tool is designed to analyze code obfuscated with the Fish-White VM from Oreans CodeVirtualizer
"""

import os
import sys
import argparse

# Read the run-trace file as a command line argument
ap = argparse.ArgumentParser()
ap.add_argument("-t", dest = 'tracefile', metavar="run_trace_file", required=True, help="the run trace file")
args = ap.parse_args()

# Read the trace file provided
try:
    trace_file = open(args.tracefile, "r")
    trace = trace_file.readlines()
except FileNotFoundError:
    print("File not found!!! Please enter correct file name.")
    exit(0)

# Get the total length of the trace
trace_len = len(trace)

vm_start = vm_end = ""
vm_start_lineno = vm_end_lineno = 0
startFound = endFound = False
vmCount, vmList = 0, []

# Look up the trace for Virtual Machine's
print("\nLength of original trace:", trace_len)
print("\nSearching the trace for VMs...!")
for i in range(0, trace_len):

    # Fish-White VMs start with a JMP instruction followed by PUSHFD instruction.
    if "JMP" in trace[i] and "PUSHFD" in trace[i+1]:
        vm_start = trace[i+1].split()[0]
        vm_start_lineno = i
        startFound = True

    # Fish-White VMs end with a POPFD followed by a RETN instruction.
    if "POPFD" in trace[i] and "RETN 0" in trace[i+1]:
        vm_end = trace[i+1].split()[0]
        vm_end_lineno = i
        endFound = True

    # If a VM is found, store it in a list with the 'start' and 'end' address.
    # Also write the VM into a different file with name as VM_START_END.txt
    # These files will be used to analyze the VM once we've detected all the VMs
    if startFound and endFound:
        startFound = False
        endFound = False
        vmList.append([vm_start, vm_end])
        vmCount += 1

        # Create a separate trace file for each VM. File Format VM_startAddress_endAddress.txt
        vm_file = "VM_" + vm_start + "_" + vm_end + ".txt"
        writeVM = open(vm_file, "w")
        for i in range(vm_start_lineno, vm_end_lineno + 1):
            writeVM.write(trace[i])
        vm_start_lineno = vm_end_lineno = 0
        writeVM.close()
print("VM search completed...!")

# Analyzing all the VMs found
if len(vmList):

    # Print the total number of VMs found
    print("\nNumber of VMs found:", len(vmList))
    i = 1

    # Print the VM number along with its entry and exit address
    for vm in vmList:
        print("\nVM number: {}  VM_ENTRY: {}  VM_EXIT: {}".format(i, vm[0], vm[1]))
        i+=1

        # Open trace of each VM. VM trace format VM_startAddress_endAddress.txt
        vm_file = "VM_" + vm[0] + "_" + vm[1] + ".txt"
        vmRead = open(vm_file, "r")
        vmTrace = vmRead.readlines()

        # Printing the main handler of the VM
        print("\nThe Main Handler of the VM:\n")
        for line in vmTrace:
            if(vmTrace.index(line) != 0):
                print(line.strip("\n"))
                if ("JMP" in line):
                    break


        # Analyze the VMs and search for junk loops
        loops = []
        print("\nSearching for loops in the VM...")

        # Loops in assembly language often use TEST instruction to loop on a certain condition
        for line in vmTrace:
            if 'TEST' in line:
                # If line contains TEST instruction append it to the loop list         
                loops.append(line.split()[0])

        # A loop is found only when the same TEST instruction is ran more than once
        # Hence we create a set of same TEST instructions executed more than once     
        loops = set([(l,loops.count(l)) for l in loops if loops.count(l) > 1])

        # Now we'll collect the actual loop contents 
        loopsFinal = set()

        # Iterate over all the loops found
        for loop in loops:
            done = 0    # Used to get a single loop only once
            for line in vmTrace:
                if loop[0] in line:
                    if ("JMP" in line): # Loops end with a JMP instruction to the TEST instruction
                        done += 1 
                        loopEnd = line.split()[0]   # End address of the loop
                        loopEndIndex = vmTrace.index(line)  # end index of loop in trace
                    else:
                        done +=1
                        loopStartIndex = vmTrace.index(line)    # Start index of loop in trace

                    # if done=2 then both start and end of a loop are found
                    if done == 2:
                        break   # We have the loop contents and dont want the same loop again

            # Add the loop details in a set
            # structure = (startAddress, startIndex, endAddress, endIndex, numberOfIterationsOfLoop)            
            loopsFinal.add((loop[0], loopStartIndex, loopEnd, loopEndIndex , loop[1]))

        # print all the loops found inside the VM
        print("\nLoops found: %d \n" % len(loopsFinal))
        count = 1

        loopName = "Loop"
        for loop in loopsFinal:
            print("Loop number: %d" % count)
            print("Loop start address: %s \nLoop end address: %s \
            \nIterations of Loop: %d\n" % (loop[0], loop[2], loop[4]))
            writeLoop = open(loopName + str(count) + ".txt", "w")
            # We cant get the loop instructions using the start and end index
            for i in range(loop[1], loop[3] + 1):
                # print(vmTrace[i].strip("\n"))
                writeLoop.write(vmTrace[i])
            count+=1

        # Next we filter out some of the junk code from the VM
        # I found a pattern for junk code where each read/write operation is surrounded by a few junk instructions.
        # the block starts with moving the contents of EBP into a REG and ends at the next similar instruction.
        # Between these two instructions only the instruction using the REG or EBP are real ones.
        vmTraceLen = len(vmTrace)
        insIndex = 0    # Index to be used to skip through instructions
        noJunk = open("noJunkTrace.txt", "w")   # File to write the trace after junk removal

        while insIndex < vmTraceLen:
            line = vmTrace[insIndex]

            # Everythin until the first junk block is copied as if for now
            # A junk block starts with MOV REG, EBP
            if "MOV" in line and "EBP" in line and "DWORD" not in line:
                ins = line.split()[2]   # MOV for junk blovk
                op1 = (line.split()[3]).split(",")[0]   # REG for junk block    
                op2 = (line.split()[3]).split(",")[1]   # EBP fro junk block

                # The first Junk block index will be stored so as to copy
                # the trace as is until the junk code start
                if "EBP" in op2:
                    junkIndex = insIndex
                    break
            insIndex += 1
        
        # Wrtie the trace from the first line until the start of junk code
        for i in range(0, junkIndex):
            noJunk.write(vmTrace[i])

        # print(insIndex)
        # noJunk.write("\nJunk Removed from below\n")

        # Start removing the junk instructions in each block
        while insIndex < vmTraceLen:
            line = vmTrace[insIndex]

            # Get the start of the block
            if "MOV" in line and "EBP" in line and "DWORD" not in line:
                ins = line.split()[2]
                op1 = (line.split()[3]).split(",")[0]
                op2 = (line.split()[3]).split(",")[1]

                if "EBP" in op2:
                    Reg = op1
                    junkBlock = True    # Start of the block found
                    # print(line)
                    noJunk.write(line) 
                    insIndex += 1

                    # iterate till the block ends
                    while junkBlock and insIndex < vmTraceLen:
                        line1 = vmTrace[insIndex]
                        insIndex += 1
                        if "EBP" not in line1: # Once the block starts EBP is not used until the next block

                            # Only instructions with REG are important
                            if Reg in line1 or "CMP" in line1 or "JE" in line1 or "JMP" in line1:
                                noJunk.write(line1)
                            # print(line1)
                        else:
                            # Junk block completed, move to next block
                            junkBlock = False
            insIndex += 1
        # noJunk.write("Junk removal complete.\n")
        noJunk.close()

        noJunk = open("noJunkTrace.txt", "r")

        # Write the remaining instructions after junk removal till the end of the vm run trace
        l = noJunk.readlines()[-2]
        lastAdd = l.split()[0]
        noJunkLastIndex = 0
        for line in vmTrace:
            if lastAdd in line:
                noJunkLastIndex = vmTrace.index(line)   # index of last instruction after junk removal
        noJunk.close()

        noJunk = open("noJunkTrace.txt", "a+")
        # append the remaining instructions of vm trace
        for i in range(noJunkLastIndex+1, vmTraceLen):
            noJunk.write(vmTrace[i])
        noJunk.close()

        noJunkTraceLen = len((open("noJunkTrace.txt", "r")).readlines())
        print("Original VM trace length: %d \nVM trace length after junk removal: %d \
        \nNumber of junk instructions removed: %d \n" % (vmTraceLen, noJunkTraceLen, (vmTraceLen-noJunkTraceLen)))



else:
    print("No VMs found!")







