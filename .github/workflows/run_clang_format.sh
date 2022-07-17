#!/bin/bash

echo "--- Installing System Dependencies ---"
sudo apt-get update
sudo apt-get install -y clang-format-13

echo "--- Running Clang Format Script ---" 
python3 run_clang_format.py $2 $3 || exit $?

echo "Done!"
