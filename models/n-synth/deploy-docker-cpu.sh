#!/bin/bash

echo '-------------------'
echo 'Building Container'
echo '------------------'
docker build . \
      -t 'reidsteven75/sound-gen-n-synth-cpu' \
      --build-arg TENSORFLOW_IMAGE=tensorflow/tensorflow:1.13.1-py3 \
      --build-arg COMPUTE_TYPE=cpu 

echo '-------------------'
echo 'Deploying Container'
echo '-------------------'
docker push 'reidsteven75/sound-gen-n-synth-cpu'