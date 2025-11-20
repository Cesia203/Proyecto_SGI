import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido
from modulos.login import login

# Llamamos a la función mostrar_bienvenido para mostrar el mensaje en la app
mostrar_bienvenido()
login()
