import xml.etree.ElementTree as ET

# Cargar el archivo GML
tree = ET.parse("finca2.gml")
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
