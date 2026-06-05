#!/bin/sh

for er in $(seq 0.01 0.01 0.06); do  
    for st in $(seq 10 10 40); do  
        ./client.py --error_rate $er --steps $st >> out.txt 2>&1
    done
done
