from EVA.permisos import Permiso

app_name = "Proyectos"

permisos = [
    Permiso("index", None),
    Permiso("contratos", ["Proyectos.view_contrato"]),
    Permiso("contratos-crear", ["Proyectos.add_contrato"]),
    Permiso("contratos-editar", ["Proyectos.change_contrato"]),
    Permiso("contratos-eliminar", ["Proyectos.delete_contrato"]),
    Permiso("contratos-detalle", ["Proyectos.view_contrato"]),
]
