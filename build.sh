#!/usr/bin/env bash
apt-get update
apt-get install -y build-essential cmake python3-dev
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
