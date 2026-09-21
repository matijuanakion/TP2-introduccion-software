import re

from src.errores import crear_error


EMAIL_VALIDO = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validar_nuevo_socio(datos):
    errores = []

    for campo in ('nombre', 'email'):
        if campo not in datos:
            errores.append(
                crear_error(
                    f"Falta el campo obligatorio '{campo}'",
                    codigo="CAMPO_OBLIGATORIO",
                    incluir_status=True,
                )
            )

    if errores:
        return errores, None

    nombre = datos['nombre']
    email = datos['email']

    if not isinstance(nombre, str):
        errores.append(
            crear_error(
                "El campo 'nombre' debe ser un texto",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )
    elif not nombre.strip():
        errores.append(
            crear_error(
                "El campo 'nombre' no puede estar vacío o ser solo espacios",
                codigo="NOMBRE_VACIO",
                incluir_status=True,
            )
        )

    if not isinstance(email, str):
        errores.append(
            crear_error(
                "El campo 'email' debe ser un texto",
                codigo="TIPO_INVALIDO",
                incluir_status=True,
            )
        )
    else:
        email_normalizado = email.strip().lower()
        if not EMAIL_VALIDO.fullmatch(email_normalizado):
            errores.append(
                crear_error(
                    "El campo 'email' debe tener un formato válido",
                    codigo="EMAIL_INVALIDO",
                    incluir_status=True,
                )
            )

    if errores:
        return errores, None

    return None, {
        'nombre': nombre.strip(),
        'email': email_normalizado,
        'activo': True,
    }