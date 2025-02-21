from interface import create_app
from interface.storage import AskarStorage
import asyncio

app = create_app()

if __name__ == "__main__":
    asyncio.run(AskarStorage().provision(recreate=False))
    app.run(host="0.0.0.0", port="5000", debug=True)
