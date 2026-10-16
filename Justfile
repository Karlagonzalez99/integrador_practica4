
# para cargar para variables de entorno 
set dotenv-load := true
set shell :=["powershell.exe","-c"]

default:
    @just --list



# cargando el esquema 
load:
    python loader.Py
