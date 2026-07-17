"""Configuration de test : secret JWT avant import de l'application."""
import os

os.environ.setdefault("JWT_SECRET", "secret-test-pytest-tres-long")
os.environ.setdefault("API_CLE", "cle-test-pytest")
os.environ.setdefault("ENVIRONNEMENT", "developpement")
os.environ.setdefault("DATABASE_URL", "sqlite://")
