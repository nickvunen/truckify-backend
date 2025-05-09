

## Using Docker

1. Build the Docker image
```
docker build -t fastapi-string-api .
```
2. Run the container
```
docker run -p 8000:8000 fastapi-string-api
```

## Using the terminal

1. Create and get in to a virtual environment:
```
python3 -m venv venv

source venv/bin/activate
```

2. Install dependencies
```
pip install
```

3. Initialize the database
```
python3 init_db.py
```

4. Start the FastAPI application
```
uvicorn main:app --reload
```
