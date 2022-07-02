## Build Docker Image
```
cd wanikani-stats-dashboard

docker build -t wanikani-stats-dashboard .
```

## Run Docker Container
The -v flag is used to mount a local directory to a directory on the container. So any files that are in the local directory will appear in the container directory, and vice versa.
```
export mount_dir=/Users/jongo/wanikani-stats-dashboard/project_files

docker run -d --rm -t -i --name wanikani-stats-dashboard -v $mount_dir:/src/project_files -p 8888:8888 -p 7777:7777 wanikani-stats-dashboard:latest
```

## Access Jupyter Lab
```
http://localhost:8888
```
