# Guardar el valor actual de LD_LIBRARY_PATH
ORIGINAL_LD_LIBRARY_PATH=$LD_LIBRARY_PATH

# Establecer LD_LIBRARY_PATH para Graphos
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Ejecutar Graphos con los parámetros recibidos
graphos "$@"

# Restaurar el valor original de LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$ORIGINAL_LD_LIBRARY_PATH
