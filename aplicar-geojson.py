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
