#!/bin/bash

echo "--- Installing System Dependencies ---"
sudo apt-get update
sudo apt-get install -y clang-format-13

echo "--- Fetching commits to base PR ---"
prCommits=`gh pr view $prId --json commits | jq '.commits | length'`
fetchDepthToPrBase=`expr $prCommits + 2`
echo "fetchDepthToPrBase: $fetchDepthToPrBase"
git fetch --no-tags --prune --progress --no-recurse-submodules --deepen=$fetchDepthToPrBase

echo "--- Running Clang Format Script ---" 
python3 run_clang_format.py $2 || exit $?

echo "Done!"
