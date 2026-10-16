
# para cargar para variables de entorno
set dotenv-load
export PATH := justfile_directory() + "/.venv/Scripts:" + justfile_directory() + "/.venv/bin:" + env('PATH')
set shell := ["powershell.exe", "-c"]

default:
    @just --list


dbt *args="debug":
     dbt {{ args }} --project-dir dbt --profiles-dir dbt


# cargando el esquema
load:
    python loader.py

fetch:
    python fetcher.py

crear-entorno:
    python -m venv .venv
