#!/usr/bin/env pwsh
# Lancement local de l'application, sans Docker, avec une base SQLite.
# Usage : .\lancer.ps1 [demarrer|reinitialiser|aide]

param(
    [string]$Mode = "demarrer"
)

$ErrorActionPreference = "Stop"

$Racine = Split-Path -Parent $MyInvocation.MyCommand.Path
$DossierBackend = Join-Path $Racine "backend"
$DossierFrontend = Join-Path $Racine "frontend"
$DossierVenv = Join-Path $DossierBackend "venv"
$PythonVenv = Join-Path $DossierVenv "Scripts\python.exe"
$FichierBd = Join-Path $DossierBackend "comptabilite.db"

# Base SQLite locale (chemin relatif au dossier backend, qui est le repertoire de travail)
$UrlBaseDonnees = "sqlite:///./comptabilite.db"
$OriginesCors = "http://localhost:5173,http://localhost:3000"

function Afficher-Aide {
    Write-Host "Usage: .\lancer.cmd [demarrer|reinitialiser|aide]"
    Write-Host "   ou: .\lancer.ps1 [demarrer|reinitialiser|aide]"
    Write-Host ""
    Write-Host "  demarrer       Installe les dependances puis lance backend + frontend (defaut)"
    Write-Host "  reinitialiser  Supprime la base SQLite locale (comptabilite.db)"
    Write-Host "  aide           Affiche cette aide"
    Write-Host ""
    Write-Host "Si PowerShell bloque le .ps1 (ExecutionPolicy), utilisez plutot :"
    Write-Host "  .\lancer.cmd"
    Write-Host ""
    Write-Host "Base de donnees : SQLite ($FichierBd)"
    Write-Host "Frontend : http://localhost:5173"
    Write-Host "API      : http://localhost:8000/docs"
}

function Rafraichir-Path {
    # Recharge le PATH systeme/utilisateur (utile juste apres une install de Node)
    $machine = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $utilisateur = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$utilisateur"
}

function Trouver-Python {
    foreach ($nom in @("python", "python3")) {
        $commande = Get-Command $nom -ErrorAction SilentlyContinue
        if ($commande) { return $commande.Source }
    }
    return $null
}

function Trouver-Npm {
    Rafraichir-Path
    $commande = Get-Command npm.cmd, npm -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($commande) { return $commande.Source }

    $candidats = @(
        (Join-Path $env:ProgramFiles "nodejs\npm.cmd"),
        (Join-Path ${env:ProgramFiles(x86)} "nodejs\npm.cmd"),
        (Join-Path $env:LOCALAPPDATA "Programs\nodejs\npm.cmd")
    )
    foreach ($chemin in $candidats) {
        if ($chemin -and (Test-Path $chemin)) { return $chemin }
    }
    return $null
}

function Reinitialiser {
    if (Test-Path $FichierBd) {
        Remove-Item $FichierBd -Force
        Write-Host "Base SQLite supprimee."
    } else {
        Write-Host "Aucune base SQLite a supprimer."
    }
}

function Demarrer {
    $env:DATABASE_URL = $UrlBaseDonnees
    $env:CORS_ORIGINS = $OriginesCors

    # --- Backend ---
    $python = Trouver-Python
    if (-not $python) {
        Write-Error "Python est introuvable. Installez Python 3 puis relancez."
        exit 1
    }

    if (-not (Test-Path $PythonVenv)) {
        Write-Host "Creation de l'environnement Python..."
        & $python -m venv $DossierVenv
    }

    Write-Host "Installation des dependances backend..."
    & $PythonVenv -m pip install -q --upgrade pip
    & $PythonVenv -m pip install -q -r (Join-Path $DossierBackend "requirements.txt")

    Write-Host "Migrations et initialisation de la base SQLite..."
    Push-Location $DossierBackend
    try {
        & $PythonVenv -m alembic upgrade head
        & $PythonVenv -m app.seed
    } finally {
        Pop-Location
    }

    Write-Host "Demarrage du backend (port 8000)..."
    $backend = Start-Process -FilePath $PythonVenv `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" `
        -WorkingDirectory $DossierBackend -PassThru -NoNewWindow

    # --- Frontend ---
    $frontend = $null
    $npm = Trouver-Npm
    if (-not $npm) {
        Write-Warning "npm est introuvable : le frontend ne sera pas demarre."
        Write-Warning "Installez Node.js, puis fermez/rouvez ce terminal et relancez avec .\lancer.cmd"
    } else {
        Write-Host "Node/npm detecte : $npm"
        if (-not (Test-Path (Join-Path $DossierFrontend "node_modules"))) {
            Write-Host "Installation des dependances frontend..."
            Push-Location $DossierFrontend
            try {
                & $npm install
            } finally {
                Pop-Location
            }
        }
        Write-Host "Demarrage du frontend (port 5173)..."
        $frontend = Start-Process -FilePath $npm `
            -ArgumentList "run", "dev" `
            -WorkingDirectory $DossierFrontend -PassThru -NoNewWindow
    }

    Write-Host ""
    Write-Host "Application demarree en mode local (sans Docker)."
    Write-Host "  Frontend : http://localhost:5173"
    Write-Host "  API      : http://localhost:8000/docs"
    Write-Host ""
    Write-Host "Appuyez sur Ctrl+C pour arreter."

    try {
        while ($true) {
            if ($backend.HasExited) { break }
            if ($frontend -and $frontend.HasExited) { break }
            Start-Sleep -Seconds 1
        }
    } finally {
        Write-Host ""
        Write-Host "Arret des services..."
        if ($backend -and -not $backend.HasExited) {
            Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
        }
        if ($frontend -and -not $frontend.HasExited) {
            Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

switch ($Mode.ToLower()) {
    "demarrer" { Demarrer }
    "reinitialiser" { Reinitialiser }
    "aide" { Afficher-Aide }
    "-h" { Afficher-Aide }
    "--help" { Afficher-Aide }
    default {
        Write-Host "Mode inconnu: $Mode"
        Afficher-Aide
        exit 1
    }
}
