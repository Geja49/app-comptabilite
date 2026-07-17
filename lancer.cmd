@echo off
REM Lance l'application en mode local sans Docker.
REM Contourne la politique d'execution PowerShell pour ce script uniquement.

cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0lancer.ps1" %*
