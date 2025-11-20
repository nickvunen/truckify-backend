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
   ``
`
   python3 -m venv venv

source venv/bin/activate

```

2. Install dependencies
```

pip install -r requirements.txt

```

3. Start the FastAPI application
```

uvicorn main:app --reload

```

4. Optional: If you want some tests data, run:
```

python3 init_sample_data.py

```

```
