# NOTE: this doesn't invoke a run command as this is used
# in paperspace jobs where the command is invoked in the job itself

# Image depends on gpu/cpu type needed
ARG TENSORFLOW_IMAGE
FROM ${TENSORFLOW_IMAGE}

# Install libraries
RUN apt-get update && apt-get install -y \
  build-essential \
  libasound2-dev \
  libjack-dev \
  libav-tools \
  libavcodec-extra \
  sox \
  lame

# Set working dir
WORKDIR /code

# Install common packages
COPY requirements-common.txt /code/requirements-common.txt
RUN pip install -r requirements-common.txt

# Install packages specific to compute type
ARG COMPUTE_TYPE
COPY requirements-${COMPUTE_TYPE}.txt /code/requirements-${COMPUTE_TYPE}.txt
RUN pip install -r requirements-${COMPUTE_TYPE}.txt

# Env
ENV COMPUTE_TYPE $COMPUTE_TYPE
ARG COMPUTE_ENVIRONMENT
ENV COMPUTE_ENVIRONMENT $COMPUTE_ENVIRONMENT

ARG DATASET_TYPE
ENV DATASET_TYPE $DATASET_TYPE

# Copy code
COPY . /code
