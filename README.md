# InteractiveMap Back-end

## Getting Started
```bash
# Clone the repo
git clone https://github.com/interactivemap/backend

# Create env files, remember to update accordingly
mv django.env.sample django.env
mv postgres.env.sample postgres.env

# Build and start the docker containers
make run

# Navigate to http://localhost/, if you get a 502 error postgres likely has not been initialized yet, try again in a few seconds
```
