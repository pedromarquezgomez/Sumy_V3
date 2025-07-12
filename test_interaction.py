import requests
import json

# URL del endpoint de invocación del agente coordinador
url = "http://localhost:8080/api/invoke/coordinator"

# Pregunta de ejemplo para enviar al agente
# Esta pregunta requiere la colaboración de varios especialistas (culinario y sumiller)
prompt = "Quisiera una recomendación de un plato principal que sea bajo en calorías y un vino para maridarlo."

# Cabeceras para la petición
headers = {
    "Content-Type": "application/json"
}

# Cuerpo de la petición en formato JSON
data = {
    "prompt": prompt
}

print(f"🤖 Enviando pregunta al coordinador: '{prompt}'")
print("-" * 50)

try:
    # Realizar la petición POST con streaming activado
    with requests.post(url, headers=headers, json=data, stream=True) as response:
        # Verificar que la petición fue exitosa
        response.raise_for_status()
        
        print("🗣️  Respuesta de Claude, nuestro Maître Digital:")
        # Iterar sobre la respuesta en streaming
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                # Decodificar el chunk y mostrarlo en tiempo real
                print(chunk.decode('utf-8'), end='', flush=True)

except requests.exceptions.RequestException as e:
    print(f"\n❌ Error al conectar con la API: {e}")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")

print("\n" + "-" * 50)
print("✅ Fin de la prueba.")
