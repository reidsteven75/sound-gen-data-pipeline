#!/bin/bash

echo '-------------------'
echo 'Building Container'
echo '------------------'
docker build . \
      -t 'reidsteven75/sound-gen-g-synth' \
      --build-arg TENSORFLOW_IMAGE=tensorflow/tensorflow:1.13.1-gpu-py3 \
      --build-arg COMPUTE_TYPE=gpu 

echo '-------------------'
echo 'Deploying Container'
echo '-------------------'
docker push 'reidsteven75/sound-gen-g-synth'