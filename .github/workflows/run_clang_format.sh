#!/bin/bash

hashCommit=$1

echo "--- Fetching commits to base PR ---"
prCommits=`gh pr view $prId --json commits | jq '.commits | length'`
fetchDepthToPrBase=`expr $prCommits + 2`
echo "fetchDepthToPrBase: $fetchDepthToPrBase"
git fetch --no-tags --prune --progress --no-recurse-submodules --deepen=$fetchDepthToPrBase

echo "--- Running Clang Format Script ---" 
python3 run_clang_format.py $hashCommit || exit $?

echo "Done!"
