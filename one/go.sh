#!/bin/bash

#kill "$(pgrep -f stacklessmud.py)"
cd stackless
kill "$(cat nolimyn.pid)"

py stacklessmud.py &
