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

        for loop in loopsFinal:
            print("Loop number: %d" % count)
            print("Loop start address: %s \nLoop end address: %s \
            \nIterations of Loop: %d\n" % (loop[0], loop[2], loop[4]))

            # We cant get the loop instructions using the start and end index
            for i in range(loop[1], loop[3] + 1):
                print(vmTrace[i].strip("\n"))
            count+=1


else:
    print("No VMs found!")







