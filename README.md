# Overview
A sound generation data pipeline that can be run either locally or in the cloud.<br />
It can generate 2 or 4 dimension Sound Spaces with configurable resolution using 2 or 4 sounds input files<br />
The whole pipeline is containerized in Docker and can be invoked with `docker-compose` commands below<br />
The test dataset & docker-compose test commands are best for faster development iterations.

# Dependancy
* Docker

# Datasets

#### Dev/Test 
`./models/n-synth/dataset-test`

#### Actual Generation Input
`./models/n-synth/dataset`

# Sound Generation

Utilizes [Magenta's Nsynth](https://github.com/tensorflow/magenta/tree/master/magenta/models/nsynth) 
model based on Wavenet trained on the following [sound dataset](https://magenta.tensorflow.org/datasets/nsynth) <br />
Model can be retrained on different sounds.

## Local CPU
Runs locally on machine CPU configured with `config-workflow-local.json`

#### Dev/Test
```
$ docker-compose up --build generate-test-local
```

#### Actual Generation
```
$ docker-compose up --build generate-local
```

## Cloud GPUs
Runs on Paperspace GPUs configured with `config-workflow-paperspace.json`

#### Actual Generation
```
$ docker-compose up --build generate-test-paperspace
```

#### Dev/Test
```
$ docker-compose up --build generate-paperspace
```

### How This Works
Jobs are deployed throughout data pipeline process:
* Run on Paperspace GPU
* Run in configured Docker Container
* Uses model checkpoint(s) that has been upload as .zip file to Paperspace 'storage' (common persistant storage)

#### Configuring GPU
`config-workflow-paperspace.json`

#### Deploying updates to Docker Container
Right now all jobs use the same container
```
$ ./models/nsynth/deploy-docker.sh
```

#### Deploying updated model checkpoint(s)
Checkpoints are accessed through the Paperspace 'storage' directory, which can be accessed on Paperspace in the 'Notebooks' section under the container named 'COMMON STORAGE'. The 'storage' directory is common accross all jobs running on Paperspace.

## Troubleshooting

No space left on disk when invoking `docker-compose`
```
$ docker image prune
```

# Related Docs
* [Paperspace API](https://paperspace.github.io/paperspace-node/)
* [Paperspace GPU & CPU Types](https://support.paperspace.com/hc/en-us/articles/360007742114-Gradient-Instance-Types)

