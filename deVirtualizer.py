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
import utils as u
import vmAnalyzer as a

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

vmList = a.searchVMs(trace, trace_len)

# Analyzing all the VMs found
if len(vmList):

    # Print the total number of VMs found
    print("\nNumber of VMs found:", len(vmList))
    i = 1

    # Print the VM number along with its entry and exit address
    for vm in vmList:
        u.printVMInfo(vm, i)
        i+=1

        vmTrace = u.readVMTrace(vm)
        
        a.getMainHandler(vm, vmTrace)

        a.findDispatcher(vmTrace)

        noJunkTrace, noJunkTraceLen = a.removeJunk(vmTrace)

        handlersUsed = []
        registers = ["EAX", "EBX", "ECX", "EDX"]
        for i in range(noJunkTraceLen):
            if "JMP" in noJunkTrace[i] and u.checkIfRegPresent(noJunkTrace[i]) and "JMP" in noJunkTrace[i+1]:
                print(noJunkTrace[i])
                # print(noJunkTrace[i+1])
            i += 1

else:
    print("No VMs found!")







