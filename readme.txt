tras implementar la arquitectura por capas, la logica del backend quedo algo asi:

ahora cada ruta esta en un rachivo .py dentro de source/routes y esas rutas a su vez hacen uso de las funciones de source/services 

basicamente toman los parametros de la url o el body y hacen toda la logica de filtrado y lo que pide el ejercicio haciendo uso de las funciones auxiliares de source/repositories,

de esta manera la logica se reparte entre la funcion de services y no en el endpoint de la ruta 

