#!/usr/bin/env python3

# Script that recursively runs clang-format on all files under g_folders
# then checkouts a different git commits; does the same; then compares
# both runs.
#
# The idea is that the new commit does not introduce changes that
# haven't been formatted by clang format.

import os
import subprocess
import sys
import threading

print("Arguments:\n\t{0}\n".format(sys.argv))

if len(sys.argv) != 2:
    print("Usage:\n\tpython3 run_clang_format.py base_commit_hash")
    exit(1)

g_folders = [
    'src',
]

g_exceptions = {'stb_image_write.h', 'stb_image.h',
                'MurmurHash3.cpp', 'GLX_backdrop.h',
                'glcorearb.h', 'glext.h', 'wglext.h'}

g_threadCount = os.cpu_count()
print("System has " + str(g_threadCount) + " CPU threads")
# g_threadCount *= 2


def split_list(alist, wanted_parts=1):
    """
    Utility function to split an array into multiple arrays
    """
    length = len(alist)
    return [alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
            for i in range(wanted_parts)]


def collectCppFilesForFormatting():
    """
    Collects & returns a list of all files we need to analyze
    """
    global g_folders
    global g_exceptions
    pathsToParse = []
    for folder in g_folders:
        for root, dirs, filenames in os.walk(os.path.join('../../', folder)):
            for fileName in filenames:
                fullpath = os.path.join(root, fileName)
                ext = os.path.splitext(fileName)[-1].lower()
                if(ext == '.cpp' or ext == '.h' or ext == '.inl'):
                    if(fileName not in g_exceptions):
                        pathsToParse.append(fullpath)
    return pathsToParse


def runClangThread(pathsToParseByThisThread, outChangelist):
    """
    Thread that runs clang format on the list of files given to it
    """
    for fullpath in pathsToParseByThisThread:
        process = subprocess.Popen(
            ['clang-format-13', '--dry-run', fullpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        (output, err) = process.communicate()
        process.wait()
        process.stdout.close()
        process.stderr.close()
        numLines = err.count("\n") + 0
        print(fullpath + ' line changes: ' + str(numLines))
        outChangelist.append((fullpath, numLines))


def runClangMultithreaded(pathsToParse):
    """
    Dispatches one thread for each block files
    """
    global g_threadCount
    changeList = [None] * g_threadCount
    for i in range(g_threadCount):
        changeList[i] = []
    pathsToParseByEachThread = split_list(pathsToParse, g_threadCount)
    threads = []
    for i, pathsToParseByThread in enumerate(pathsToParseByEachThread):
        newThread = threading.Thread(
            target=runClangThread, args=(pathsToParseByThread, changeList[i]))
        newThread.start()
        threads.append(newThread)

    # Wait for threads to finish
    for thread in threads:
        thread.join()

    fullChangeList = {}
    for i in range(g_threadCount):
        for change in changeList[i]:
            fullChangeList[change[0]] = change[1]
    return fullChangeList


pathsToParse = collectCppFilesForFormatting()
prChangeList = runClangMultithreaded(pathsToParse)

# Change to base
process = subprocess.Popen(['git', 'checkout', 'asd'])

pathsToParse = collectCppFilesForFormatting()
baseChangeList = runClangMultithreaded(pathsToParse)

bHasErrors = False
for fullpath, prNumLines in prChangeList:
    try:
        baseNumLines = baseChangeList[fullpath]
        if prNumLines > baseNumLines:
            print("[CLANG FORMAT]: {0} has more lines to format PR: {1} vs BASE: {2}".format(
                fullpath, prNumLines, baseNumLines))
            bHasErrors = True
    except IndexError:
        if prNumLines != 0:
            print("[CLANG FORMAT]: {0} is a new file with lines to format PR: {1}".format(
                fullpath, prNumLines))
            bHasErrors = True

if bHasErrors:
    exit(1)
