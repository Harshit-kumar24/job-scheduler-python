set -e 

echo "deleting the old image..."
docker rmi -f job-scheduler 

echo "creating new image..."
docker build -t job-scheduler .

echo "running the container..."
docker-compose up 
