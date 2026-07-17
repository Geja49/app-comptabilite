"""Configuration de test : clé API obligatoire avant import de l'application."""
import os

os.environ.setdefault("API_CLE", "cle-test-pytest")
os.environ.setdefault("ENVIRONNEMENT", "developpement")
os.environ.setdefault("DATABASE_URL", "sqlite://")
