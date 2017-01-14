#!/bin/sh

python ych_parselog.py  $1 ./

python plot_learning_curve.py $1 ./tmp.png
 
