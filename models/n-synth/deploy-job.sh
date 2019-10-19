#!/bin/bash

paperspace jobs create \
    --machineType 'GPU+' \
    --container 'reidsteven75/sound-gen-n-synth:latest'\
    --command 'python generate.py'\
    --workspace './job'