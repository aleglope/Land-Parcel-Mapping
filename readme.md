# Herramienta de Conversión y Mapeo de GeoJSON

## Introducción

Este proyecto está diseñado para extraer datos de archivos GML del Catastro Español, convertirlos en formato GeoJSON y mostrarlos en un mapa interactivo utilizando Folium. El proyecto consta de dos scripts principales en Python: uno para la conversión de GML a GeoJSON y otro para visualizar los datos GeoJSON en un mapa.

## Funcionalidades

1. **Conversión de GML a GeoJSON**:
    - Lee archivos GML y extrae datos relevantes, incluyendo el ID de la parcela, área, fechas de validez, referencia catastral nacional, punto de referencia y coordenadas del polígono.
    - Transforma la referencia espacial de EPSG:25829 a EPSG:4326.
    - Almacena las características extraídas en un archivo GeoJSON.

2. **Visualización de GeoJSON**:
    - Carga el archivo GeoJSON generado y lo visualiza usando Folium.
    - Añade tooltips y popups personalizados para la exploración interactiva de datos en el mapa.

## Requisitos

- Python 3.x
- folium
- gdal
- xml.etree.ElementTree

## Configuración

1. Instalar los paquetes necesarios de Python:
    ```sh
    pip install folium gdal
    ```

2. Configurar las variables de entorno para GDAL y PROJ. Ajusta estas rutas según tu instalación:
    ```sh
    export GDAL_DATA=/ruta/a/gdal
    export PROJ_LIB=/ruta/a/proj
    ```

## Uso

### Conversión de GML a GeoJSON

El script `convert_gml_to_geojson.py` maneja la conversión de archivos GML a GeoJSON. Actualiza la lista `input_files` con las rutas a tus archivos GML. El archivo GeoJSON resultante se guardará como `output_file.geojson`.

Actualmente, para que el nombre de la parcela aparezca correctamente, debes renombrar el archivo resultante con los datos de la parcela. En futuros commits se mejorará este apartado.

```python
import os
from osgeo import ogr, osr
import json

# Configuración de las variables de entorno para GDAL y PROJ
os.environ["GDAL_DATA"] = r"ruta_a_gdal"
os.environ["PROJ_LIB"] = r"ruta_a_proj"

# Lista de archivos GML a procesar
input_files = ["./parcela.gml"]
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
    sourceSR.ImportFromEPSG(25829)

    targetSR = osr.SpatialReference()
    targetSR.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(sourceSR, targetSR)

    file_name = os.path.splitext(os.path.basename(input_file))[0]

    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom:
            geom.Transform(transform)
            feature_dict = json.loads(geom.ExportToJson())
            properties = {
                field.GetName(): feature.GetField(field.GetName())
                for field in layer.schema
            }
            properties["source_file"] = file_name
            features.append({
                "type": "Feature",
                "geometry": feature_dict,
                "properties": properties,
            })

# Crear el objeto GeoJSON
geojson = {"type": "FeatureCollection", "features": features}

# Guardar el GeoJSON transformado en un archivo
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(geojson, f)

print("Conversión completada. El archivo GeoJSON ha sido guardado en:", output_file)
```

### Visualización de GeoJSON

El script `visualize_geojson.py` carga un archivo GeoJSON y lo visualiza usando Folium. El mapa se guardará como `mapa_con_geojson.html`.

```python
import folium
import json

center_location = [42.53806, -8.30453]  # Ajusta según la ubicación deseada

m = folium.Map(location=center_location, zoom_start=13)

# Cargar el GeoJSON desde el archivo
with open("output_file.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Añadir el GeoJSON al mapa con popups y tooltips personalizados
folium.GeoJson(
    geojson_data,
    name="geojson",
    tooltip=folium.GeoJsonTooltip(
        fields=["source_file", "areaValue"], aliases=["Archivo:", "Área:"]
    ),
    popup=folium.GeoJsonPopup(
        fields=["source_file", "areaValue"], aliases=["Archivo:", "Área:"]
    ),
).add_to(m)

m.save("mapa_con_geojson.html")

print("Mapa generado con éxito y guardado en 'mapa_con_geojson.html'")
```

## Ejemplo: Análisis de Archivos GML

Para la extracción más avanzada de datos de archivos GML, el script `parse_gml.py` demuestra cómo extraer varios elementos de la estructura GML usando `xml.etree.ElementTree`.

```python
import xml.etree.ElementTree as ET

# Cargar el archivo GML
tree = ET.parse("parcela.gml")
root = tree.getroot()

# Definir los namespaces para facilitar la búsqueda de elementos
ns = {
    "cp": "http://inspire.ec.europa.eu/schemas/cp/4.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

# Buscar todos los elementos de la parcela
parcels = root.findall(".//cp:CadastralParcel", ns)
for parcel in parcels:
    # Extraer el ID de la parcela
    parcel_id = parcel.get("{http://www.opengis.net/gml/3.2}id")
    print(f"ID de la Parcela: {parcel_id}")

    # Extraer el valor del área
    area_value = parcel.find(".//cp:areaValue", ns)
    area_uom = (
        area_value.get("uom") if area_value is not None else "m2"
    )  # Unidad de medida
    print(f"Área de la Parcela: {area_value.text} {area_uom}")

    # Extraer fechas de validez
    begin_version = parcel.find(".//cp:beginLifespanVersion", ns)
    end_version = parcel.find(".//cp:endLifespanVersion", ns)
    print(
        f'Inicio de validez: {begin_version.text if begin_version is not None else "N/A"}'
    )
    print(f'Fin de validez: {end_version.text if end_version is not None else "N/A"}')

    # Extraer la referencia catastral nacional
    national_ref = parcel.find(".//cp:nationalCadastralReference", ns)
    print(
        f'Referencia Catastral Nacional: {national_ref.text if national_ref is not None else "N/A"}'
    )

    # Extraer punto de referencia
    ref_point = parcel.find(".//cp:referencePoint/gml:Point/gml:pos", ns)
    print(f'Punto de Referencia: {ref_point.text if ref_point is not None else "N/A"}')

    # Extraer coordenadas del polígono
    surfaces = parcel.findall(
        ".//gml:MultiSurface/gml:surfaceMember/gml:Surface/gml:patches/gml:PolygonPatch/gml:exterior/gml:LinearRing/gml:posList",
        ns,
    )
    for i, surface in enumerate(surfaces, start=1):
        print(f"Coordenadas del polígono {i}: {surface.text}")
```

## Conclusión

Este proyecto proporciona un conjunto de herramientas completo para convertir archivos GML del Catastro Español a GeoJSON y visualizarlos en un mapa interactivo. Los scripts están diseñados para ser modulares y fácilmente extensibles para diversos casos de uso. No dudes en contribuir y mejorar la funcionalidad.

Actualmente, para que el nombre de la parcela aparezca correctamente, debes renombrar el archivo resultante con los datos de la parcela. En futuros commits se mejorará este apartado.