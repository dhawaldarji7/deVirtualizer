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

def findDispatcher(vmTrace):

    # Analyze the VMs and search for dispatcher loops
    loops = []
    print("\nSearching for Dispatcher loop in the VM.")

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
                    done += 1
                    loopStartIndex = vmTrace.index(line)    # Start index of loop in trace

                # if done=2 then both start and end of a loop are found
                if done == 2:
                    break   # We have the loop contents and dont want the same loop again

        # Add the loop details in a set
        # structure = (startAddress, startIndex, endAddress, endIndex, numberOfIterationsOfLoop)            
        loopsFinal.add((loop[0], loopStartIndex, loopEnd, loopEndIndex , loop[1]))

    # print all the loops found inside the VM
    # print("\nDispatcher Loop found: %d \n" % len(loopsFinal))
    print("Dispatcher Loop found.")
    count = 1

    loopName = "DispatcherLoop"
    for loop in loopsFinal:
        # print("Loop number: %d" % count)
        print("Loop start address: %s \nLoop end address: %s \
        \nIterations of Loop: %d\n" % (loop[0], loop[2], int(loop[4]) - 1))
        writeLoop = open(loopName + str(count) + ".txt", "w")
        # We cant get the loop instructions using the start and end index
        for i in range(loop[1], loop[3] + 1):
            # print(vmTrace[i].strip("\n"))
            writeLoop.write(vmTrace[i])
        count+=1

def removeJunk(vmTrace):
    
    # Next we filter out some of the junk code from the VM
    # I found a pattern for junk code where each read/write operation is surrounded by a few junk instructions.
    # the block starts with moving the contents of EBP into a REG and ends at the next similar instruction.
    # Between these two instructions only the instruction using the REG or EBP are real ones.
    vmTraceLen = len(vmTrace)
    insIndex = 0    # Index to be used to skip through instructions
    noJunk = open("noJunkTrace.txt", "w")   # File to write the trace after junk removal

    while insIndex < vmTraceLen:
        line = vmTrace[insIndex]

        # Everything until the first junk block is copied as is for now
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

        if "JMP" in line:
            noJunk.write(line)

        # Get the start of the block
        elif "MOV" in line and "EBP" in line and "DWORD" not in line:
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

    noJunkTrace = open("noJunkTrace.txt", "r").readlines()
    noJunkTraceLen = len(noJunkTrace)
    print("Original VM trace length: %d \nVM trace length after junk removal: %d \
    \nNumber of junk instructions removed: %d \n" % (vmTraceLen, noJunkTraceLen, (vmTraceLen-noJunkTraceLen)))

    return noJunkTrace, noJunkTraceLen


