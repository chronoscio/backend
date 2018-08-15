# InteractiveMap Back-end [![Build Status](https://travis-ci.org/interactivemap/backend.svg?branch=master)](https://travis-ci.org/interactivemap/backend) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/0074e97bc13b476ea3eec279483d3cab)](https://www.codacy.com/app/whirish/backend?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=interactivemap/backend&amp;utm_campaign=Badge_Grade)

## Getting Started
```bash
# Clone the repo
git clone https://github.com/interactivemap/backend

# Create env files, remember to update accordingly
mv django.env.sample django.env
mv postgres.env.sample postgres.env

# Build and start the docker containers
make run

# Navigate to http://localhost/, if you get a 502 error postgres likely has not been initialized yet,
#   try again in a few seconds
```
