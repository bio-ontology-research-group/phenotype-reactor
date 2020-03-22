To run transformation over phenotype annotation datasets
```sh
python manage.py transform
```
To copy transformed data to virtuoso container. Note that you need to run this script on machine that has virtuoso container running on it.
```sh
# To make it executable
chmod +x deployds.sh

# Run the script
./deployds.sh [virtuoso-docker-container-id] 
```
To bulk load transformed data to virtuoso server
```sh
python manage.py loadvirtuoso
```
To process training data
```sh
python manage.py processds -o true -d true -c true
```
To train data using TrainE algorithm with setting  device=CPU, num of epochs=1000 and batch size=32, run the following command
```sh
python manage.py trainkg -r CPU -e 1000 -b 32
```
ls

