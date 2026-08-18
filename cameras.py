import json
import os


CAMERAS_FILE = "cameras.json"
MIDDLEWARE_URL = "http://192.168.68.107:5000/hik-alert"


def cargar_camaras():
    if not os.path.exists(CAMERAS_FILE):
        return {}

    try:
        with open(CAMERAS_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return {}


def guardar_camaras(camaras):
    with open(CAMERAS_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            camaras,
            archivo,
            indent=4,
            ensure_ascii=False
        )


def mostrar_camaras(camaras):
    print("\nCAMARAS CONFIGURADAS")
    print("-" * 50)

    if not camaras:
        print("No hay camaras configuradas.")
        return

    for camera_id, datos in camaras.items():
        print(
            f"{camera_id} | "
            f"{datos['name']} | "
            f"{datos['latitude']}, {datos['longitude']}"
        )


def pedir_coordenada(nombre):
    while True:
        try:
            return float(input(f"{nombre}: ").strip())
        except ValueError:
            print("Ingrese una coordenada valida.")


def agregar_camara(camaras):
    print("\n========== AGREGAR CAMARA ==========")

    camera_id = input("ID de camara (ej. cam04): ").strip()

    if not camera_id:
        print("El ID no puede estar vacio.")
        return

    if camera_id in camaras:
        print(f"La camara '{camera_id}' ya existe.")
        return

    nombre = input("Nombre de la camara: ").strip()

    latitud = pedir_coordenada("Latitud")
    longitud = pedir_coordenada("Longitud")

    if not (-90 <= latitud <= 90):
        print("Latitud fuera de rango.")
        return

    if not (-180 <= longitud <= 180):
        print("Longitud fuera de rango.")
        return

    camaras[camera_id] = {
        "name": nombre,
        "latitude": latitud,
        "longitude": longitud
    }

    guardar_camaras(camaras)

    print(f"\nCamara '{camera_id}' guardada correctamente.")


def editar_camara(camaras):
    mostrar_camaras(camaras)

    camera_id = input(
        "\nID de la camara que desea editar: "
    ).strip()

    if camera_id not in camaras:
        print("Camara no encontrada.")
        return

    actual = camaras[camera_id]

    print("\nPresione ENTER para conservar el valor actual.")

    nombre = input(
        f"Nombre [{actual['name']}]: "
    ).strip()

    latitud = input(
        f"Latitud [{actual['latitude']}]: "
    ).strip()

    longitud = input(
        f"Longitud [{actual['longitude']}]: "
    ).strip()

    if nombre:
        actual["name"] = nombre

    if latitud:
        try:
            nueva_latitud = float(latitud)

            if not (-90 <= nueva_latitud <= 90):
                print("Latitud fuera de rango.")
                return

            actual["latitude"] = nueva_latitud

        except ValueError:
            print("Latitud invalida.")
            return

    if longitud:
        try:
            nueva_longitud = float(longitud)

            if not (-180 <= nueva_longitud <= 180):
                print("Longitud fuera de rango.")
                return

            actual["longitude"] = nueva_longitud

        except ValueError:
            print("Longitud invalida.")
            return

    guardar_camaras(camaras)

    print("\nCamara actualizada correctamente.")


def eliminar_camara(camaras):
    mostrar_camaras(camaras)

    camera_id = input(
        "\nID de la camara que desea eliminar: "
    ).strip()

    if camera_id not in camaras:
        print("Camara no encontrada.")
        return

    nombre = camaras[camera_id]["name"]

    confirmar = input(
        f"Eliminar '{nombre}' ({camera_id})? [s/N]: "
    ).strip().lower()

    if confirmar == "s":
        del camaras[camera_id]
        guardar_camaras(camaras)
        print("Camara eliminada.")
    else:
        print("Operacion cancelada.")


def mostrar_configuracion_hikcentral(camaras):
    mostrar_camaras(camaras)

    camera_id = input(
        "\nID de camara: "
    ).strip()

    if camera_id not in camaras:
        print("Camara no encontrada.")
        return

    datos = camaras[camera_id]

    print("\n" + "=" * 50)
    print(" CONFIGURACION PARA HIKCENTRAL")
    print("=" * 50)

    print(f"\nCamara: {datos['name']}")

    print("\nEndpoint:")
    print(MIDDLEWARE_URL)

    print("\nHTTP Method:")
    print("POST")

    print("\nJSON:")
    print(
        json.dumps(
            {"camera_id": camera_id},
            indent=4,
            ensure_ascii=False
        )
    )

    print("\n" + "=" * 50)


def main():

    while True:

        camaras = cargar_camaras()

        print("\n" + "=" * 50)
        print(" CONFIGURADOR DE CAMARAS")
        print(" FH2 × HIKCENTRAL")
        print("=" * 50)

        print(f"\nCamaras configuradas: {len(camaras)}")

        mostrar_camaras(camaras)

        print("\n" + "-" * 50)
        print("1. Agregar camara")
        print("2. Editar camara")
        print("3. Eliminar camara")
        print("4. Ver configuracion HikCentral")
        print("5. Salir")

        opcion = input("\nSeleccione una opcion: ").strip()

        if opcion == "1":
            agregar_camara(camaras)

        elif opcion == "2":
            editar_camara(camaras)

        elif opcion == "3":
            eliminar_camara(camaras)

        elif opcion == "4":
            mostrar_configuracion_hikcentral(camaras)

        elif opcion == "5":
            print("\nConfigurador cerrado.")
            break

        else:
            print("\nOpcion invalida.")


if __name__ == "__main__":
    main()
