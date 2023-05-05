#!/bin/bash

GPIO_CTRL=./aw9523b.py

# init gpio expander
${GPIO_CTRL} -i || exit 1

# auto test mode
${GPIO_CTRL} -a