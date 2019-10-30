Dev
------
```
$ docker-compose up --build generate-local-test
```

If error about no disk space run...

```
$ docker image prune
```

Deploy
------
Deployed as a job that runs in Paperspace. Job runs in a configurable docker container and uses configurable AI model checkpoint(s) that has been upload as .zip file to Paperspace 'storage' (common persistant storage)

1) Deploy Docker
$ ./deploy-docker.sh

2) Deploy Checkpoint
Checkpoints are accessed through the Paperspace 'storage' directory, which can be accessed on Paperspace in the 'Notebooks' section under the container named 'COMMON STORAGE'. The 'storage' directory is common accross all jobs running on Paperspace.

3) Deploy Job
$ ./deploy-job.sh

Paperspace
----------
CLI/API
https://paperspace.github.io/paperspace-node/
https://docs.paperspace.com/gradient/experiments/run-experiments

GPU & CPU Types
https://support.paperspace.com/hc/en-us/articles/360007742114-Gradient-Instance-Types
