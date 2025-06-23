import xml.etree.ElementTree as ET
import json
import os

def detect_odm_model(cam_type, k1, k2, p1, p2, k3):
    """
    Determina el modelo de cámara ODM más adecuado según el tipo y coeficientes de distorsión.
    """
    cam_type = cam_type.lower().strip()

    if "fisheye" in cam_type:
        return "fisheye_opencv"  # Puedes cambiar a 'fisheye' si el modelo se ajusta mejor

    if any(abs(val) > 1e-6 for val in [k1, k2, p1, p2, k3]):
        return "brown"

    return "perspective"


def export_cameras(xml_path, output_path="cameras.json"):
    """
    Convierte las cámaras definidas en un fichero XML de Graphos al formato ODM cameras.json.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    odm_cameras = {}

    for cam in root.findall(".//Camera"):
        make = cam.findtext("Make", default="unknown").lower()
        model = cam.findtext("Model", default="unknown").lower()
        cam_type = cam.findtext("Type", default="unknown").lower().strip()
        width = int(cam.findtext("Width", default="0"))
        height = int(cam.findtext("Height", default="0"))
        sensor_size = float(cam.findtext("SensorSize", default="1.0"))

        calib = cam.find("Calibration")
        fx = float(calib.findtext("fx"))
        fy = float(calib.findtext("fy"))
        cx = float(calib.findtext("cx"))
        cy = float(calib.findtext("cy"))
        k1 = float(calib.findtext("k1", default="0"))
        k2 = float(calib.findtext("k2", default="0"))
        p1 = float(calib.findtext("p1", default="0"))
        p2 = float(calib.findtext("p2", default="0"))
        k3 = float(calib.findtext("k3", default="0"))

        odm_model = detect_odm_model(cam_type, k1, k2, p1, p2, k3)

        # Normalización de parámetros
        focal_x = fx / width
        focal_y = fy / height
        c_x = (cx / width) - 0.5
        c_y = (cy / height) - 0.5

        focal_mm = fx * sensor_size / width  # focal en mm
        focal_ratio = round(focal_mm / sensor_size, 4)
        key = f"{make} {model} {width} {height} {odm_model} {focal_ratio}"

        odm_entry = {
            "projection_type": odm_model,
            "width": width,
            "height": height,
            "focal_x": focal_x,
            "focal_y": focal_y,
            "c_x": c_x,
            "c_y": c_y,
        }

        if odm_model in ["brown", "fisheye_opencv"]:
            odm_entry.update({
                "k1": k1,
                "k2": k2,
                "p1": p1,
                "p2": p2,
                "k3": k3
            })

        odm_cameras[key] = odm_entry

    with open(output_path, "w") as f:
        json.dump(odm_cameras, f, indent=4)

    print(f"[✓] cameras.json generado en: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python3 export_cameras.py <ruta_proyecto.xml> [ruta_salida.json]")
        sys.exit(1)

    xml_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "cameras.json"
    export_cameras(xml_file, output_file)
