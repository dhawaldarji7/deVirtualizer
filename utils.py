#!/usr/bin/python3

def printVMInfo(vm, index):
    print("\nVM number: {}  VM_ENTRY: {}  VM_EXIT: {}".format(index, vm[0], vm[1]))

def readVMTrace(vm):
    # Open trace of each VM. VM trace format VM_startAddress_endAddress.txt
    vm_file = "VM_" + vm[0] + "_" + vm[1] + ".txt"
    vmRead = open(vm_file, "r")
    return vmRead.readlines()

def getMainHandler(vm, vmTrace):
    mainHandler = "MainHandler_" + "_" + vm[0] + ".txt"
    mainHandlerWrite = open(mainHandler, "w")

    # Writing the main handler of the VM
    print("\nWriting the Main Handler of the VM.")
    for line in vmTrace:
        if(vmTrace.index(line) != 0):
            # print(line.strip("\n"))
            mainHandlerWrite.write(line)
            if ("JMP" in line):
                break

def checkIfRegPresent(traceLine):
    '''Checks if any of the registers is present in the instruction line or not'''
    registers = ["EAX", "EBX", "ECX", "EDX"] # all available registers
    check = False
    traceLineSplit = traceLine.split(" ")   # split trace line into tokens
    check = any(r == traceLineSplit[7].strip("\n") for r in registers)
    return check