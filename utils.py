#!/usr/bin/python3

def searchVMs(trace, trace_len):

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
    return vmList

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