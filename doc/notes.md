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
To process test data
```sh
python manage.py processds -t true
```
To train data using TrainE algorithm with setting  device=CPU, num of epochs=1000 and batch size=32, run the following command
```sh
python manage.py trainkg -r cpu -e 1000 -b 32
```

To deploy phenotype reactor backend api follow the following steps:
Copy the projects uwsgi configuration file 'phenotype-reactor.wsgi.ini' to apps-enabled of uwsgi.
Change the paths in uwsgi configuration file to project according to server settings.
Restart the uwsgi service. 
Add nginx app configuration to sites-available of nginx.
```sh
cp {nginx}/sites-available/phenotype-reactor.nginx.conf
```
Generate app configuration link in sites-enabled
```sh
sudo ln -s {nginx}/sites-available/phenotype-reactor.nginx.conf {nginx}/etc/nginx/sites-enabled
```
Restart nginx service.


To federate queries on virtuoso, run following command using iSQL:
```sh
grant SPARQL_LOAD_SERVICE_DATA to "SPARQL";
grant SPARQL_SPONGE to "SPARQL";
```