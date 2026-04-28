import sys
import os

# Adiciona /backend ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from main import app  # noqa: E402
from mangum import Mangum  # noqa: E402

# Vercel invoca esta variável como handler
handler = Mangum(app, lifespan="off")
