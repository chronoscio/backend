# InteractiveMap Back-end

## Getting Started
```bash
git clone https://github.com/interactivemap/backend
mv django.env.sample django.env #Update file accordingly
docker-compose build
docker-compose up -d
#Navigate to http://localhost/, if you get a 502 error postgres likely has not been initialized yet, try again in a few seconds
```
