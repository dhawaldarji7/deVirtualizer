#!/usr/bin/python3

def printVMInfo(vm, index):
    print("\nVM number: {}  VM_ENTRY: {}  VM_EXIT: {}".format(index, vm[0], vm[1]))

def readVMTrace(vm):
    # Open trace of each VM. VM trace format VM_startAddress_endAddress.txt
    vm_file = "VM_" + vm[0] + "_" + vm[1] + ".txt"
    vmRead = open("./output/" + vm_file, "r")
    return vmRead.readlines()

def checkIfRegPresent(traceLine):
    '''Checks if any of the registers is present in the instruction line or not'''
    registers = ["EAX", "EBX", "ECX", "EDX"] # all available registers
    check = False
    traceLineSplit = traceLine.split(" ")   # split trace line into tokens
    check = any(r == traceLineSplit[7].strip("\n") for r in registers)
    return check  