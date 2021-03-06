#!/usr/bin/env python
"""
utilities for larch
"""
from __future__ import print_function
import re
import sys

def PrintExceptErr(err_str, print_trace=True):
    " print error on exceptions"
    print('\n***********************************')
    print(err_str)
    #print 'PrintExceptErr', err_str
    try:
        print('Error: %s' % sys.exc_type)
        etype, evalue, tback = sys.exc_info()
        if print_trace == False:
            tback = ''
        sys.excepthook(etype, evalue, tback)
    except:
        print('Error printing exception error!!')
        raise
    print('***********************************\n')

def strip_comments(sinp, char='#'):
    "find character in a string, skipping over quoted text"
    if sinp.find(char) < 0:
        return sinp
    i = 0
    while i < len(sinp):
        tchar = sinp[i]
        if tchar in ('"',"'"):
            eoc = sinp[i+1:].find(tchar)
            if eoc > 0:
                i = i + eoc
        elif tchar == char:
            return sinp[:i].rstrip()
        i = i + 1
    return sinp


RESERVED_WORDS = ('and', 'as', 'assert', 'break', 'class', 'continue',
                  'def', 'del', 'elif', 'else', 'eval', 'except', 'exec',
                  'execfile', 'finally', 'for', 'from', 'global', 'if',
                  'import', 'in', 'is', 'lambda', 'not', 'or', 'pass',
                  'print', 'raise', 'return', 'try', 'while', 'with',
                  'group', 'end', 'endwhile', 'endif', 'endfor', 'endtry',
                  'enddef', 'True', 'False', 'None')

NAME_MATCH = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$").match
VALID_NAME_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._'
def isValidName(name):
    "input is a valid name"
    if name in RESERVED_WORDS:
        return False
    tnam = name[:].lower()
    return NAME_MATCH(tnam) is not None

def fixName(name):
    "try to fix string to be a valid name"
    if isValidName(name):
        return name

    if isValidName('_%s' % name):
        return '_%s' % name
    chars = []
    for s in name:
        if s not in VALID_NAME_CHARS:
            s = '_'
        chars.append(s)
    name = ''.join(chars)
    # last check (name may begin with a number or .)
    if not isValidName(name):
        name = '_%s' % name
    return name

def isNumber(num):
    "input is a number"
    try:
        cnum = complex(num)
        return True
    except ValueError:
        return False

def isLiteralStr(inp):
    "is a literal string"
    return ((inp.startswith("'") and inp.endswith("'")) or
            (inp.startswith('"') and inp.endswith('"')))


def find_delims(s, delim='"',match=None):
    """find matching delimeters (quotes, braces, etc) in a string.
    returns
      True, index1, index2 if a match is found
      False, index1, len(s) if a match is not found
    the delimiter can be set with the keyword arg delim,
    and the matching delimiter with keyword arg match.

    if match is None (default), match is set to delim.

    >>> find_delims(mystr, delim=":")
    >>> find_delims(mystr, delim='<', match='>')
    """
    esc = "\\"
    if match is None:
        match = delim
    j = s.find(delim)
    if j > -1 and s[j:j+len(delim)] == delim:
        p, k = None, j
        while k < j+len(s[j+1:]):
            k = k+1
            if s[k:k+len(match)] == match and p != esc:
                return True, j, k+len(match)-1
            p = s[k:k+1]
    return False, j, len(s)

