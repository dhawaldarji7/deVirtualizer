#!/usr/bin/python3

def checkIfRegPresent(traceLine):
    '''Checks if any of the registers is present in the instruction line or not'''
    registers = ["EAX", "EBX", "ECX", "EDX"] # all available registers
    check = False
    traceLineSplit = traceLine.split(" ")   # split trace line into tokens
    check = any(r == traceLineSplit[7].strip("\n") for r in registers)
    return check