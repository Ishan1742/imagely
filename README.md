# imagely
A image metadata storage management system, using Bootstrap, Flask, MongoDB and Docker.

### Installation
```bash
docker-compose up
```

### Clean Build Images
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Running in localhost
To see your changes to the code being updated. Run the flask app from the terminal and the mongodb instance from docker.
- Install pipenv
```bash
pip3 install pipenv
```
- Installing Requirements
```bash
~/imagely/$ pipenv install
```

- Running Flask App
```bash
pipenv shell
python3 app.py
```

- Running mongodb instance
```bash
docker-compose up mongodb
```



### Access
```
http://localhost:5000
```
