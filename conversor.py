import os
from osgeo import ogr, osr
import json

# Configuración de las variables de entorno para GDAL y PROJ
os.environ["GDAL_DATA"] = (
    r"C:\Users\34692\miniconda3\envs\catastroenv\Library\share\gdal"
)
os.environ["PROJ_LIB"] = (
    r"C:\Users\34692\miniconda3\envs\catastroenv\Library\share\proj"
)

# Lista de archivos GML a procesar
input_files = [
    "./Polígono 57 Parcela 100 TRAS DO CANDAL. FORCAREI (PONTEVEDRA)  2.112 m2.gml",
    "./finca2.gml",
]
output_file = "output_file.geojson"

features = []  # Lista para almacenar todas las features de todos los archivos

# Iterar sobre cada archivo GML
for input_file in input_files:
    driver = ogr.GetDriverByName("GML")
    data_source = driver.Open(input_file, 0)  # 0 significa solo lectura
    if not data_source:
        print(f"No se pudo abrir el archivo '{input_file}'")
        continue  # Saltar al siguiente archivo si no se puede abrir

    layer = data_source.GetLayer(0)

    sourceSR = osr.SpatialReference()
    if sourceSR.ImportFromEPSG(25829) != 0:
        print(
            "No se pudo inicializar la referencia espacial de origen para", input_file
        )
        continue

    targetSR = osr.SpatialReference()
    if targetSR.ImportFromEPSG(4326) != 0:
        print(
            "No se pudo inicializar la referencia espacial de destino para", input_file
        )
        continue

    transform = osr.CoordinateTransformation(sourceSR, targetSR)
    if not transform:
        print("No se pudo crear la transformación de coordenadas para", input_file)
        continue

    file_name = os.path.splitext(os.path.basename(input_file))[
        0
    ]  # Extraer solo el nombre del archivo sin la extensión

    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom and geom.Transform(transform) == 0:  # Transformar solo si es posible
            feature_dict = json.loads(geom.ExportToJson())
            properties = {
                field.GetName(): feature.GetField(field.GetName())
                for field in layer.schema
            }
            properties["source_file"] = (
                file_name  # Añadir el nombre del archivo GML a las propiedades
            )
            features.append(
                {
                    "type": "Feature",
                    "geometry": feature_dict,
                    "properties": properties,
                }
            )

# Crear el objeto GeoJSON
geojson = {"type": "FeatureCollection", "features": features}

# Guardar el GeoJSON transformado en un archivo
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(geojson, f)

print("Conversión completada. El archivo GeoJSON ha sido guardado en:", output_file)
