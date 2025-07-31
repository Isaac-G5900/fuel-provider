# /********************************************************************************
# * Copyright (c) 2023 Contributors to the Eclipse Foundation
# *
# * See the NOTICE file(s) distributed with this work for additional
# * information regarding copyright ownership.
# *
# * This program and the accompanying materials are made available under the
# * terms of the Apache License 2.0 which is available at
# * http://www.apache.org/licenses/LICENSE-2.0
# *
# * SPDX-License-Identifier: Apache-2.0
# ********************************************************************************/

# Build stage, to create a Virtual Environent
FROM python:3.11-slim-bullseye

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first (better layer caching)
COPY requirements.in requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Install our package in development mode
RUN pip install -e .

# Environment setup
ENV LOG_LEVEL="info,databroker=debug"
ENV PYTHONUNBUFFERED=yes

# Run the service
CMD ["fuel-provider"]
