#!/usr/bin/python3

def checkIfRegPresent(traceLine):
    registers = ["EAX", "EBX", "ECX", "EDX"]
    check = False
    traceLineSplit = traceLine.split(" ")
    check = any(r == traceLineSplit[7].strip("\n") for r in registers)
    return check