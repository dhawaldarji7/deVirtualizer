#!/usr/bin/python3

import os

def printVMInfo(vm, index):
    print("\nVM number: {}  VM_ENTRY: {}  VM_EXIT: {}".format(index, vm[0], vm[1]))

def readVMTrace(vm):

    # Open trace of each VM. VM trace format VM_startAddress_endAddress.txt
    vm_file = "VM_" + vm[0] + "_" + vm[1] + ".txt"
    vmDir = "VM_" + vm[0] + "_" + vm[1]
    vmRead = open("./output/VMs/" + vmDir + "/" + vm_file, "r")
    return vmRead.readlines()

def checkIfRegPresent(traceLine):
    '''Checks if any of the registers is present in the instruction line or not'''
    registers = ["EAX", "EBX", "ECX", "EDX"] # all available registers
    traceLineSplit = traceLine.split(" ")   # split trace line into tokens
    return any(r == traceLineSplit[7].strip("\n") for r in registers) 

def checkIfHandlerPresent(handlers, line):
    for h in handlers:
        if h in line:
            return h, True
    return "", False