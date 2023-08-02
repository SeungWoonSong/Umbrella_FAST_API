import uvicorn
from .sql_app import main

if __name__ == "__main__":
		uvicorn.run(main, host="0.0.0.0", port=8000)