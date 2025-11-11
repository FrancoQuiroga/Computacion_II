# common/serialization.py

import json

class JsonSerializer:
    """Serializador simple usando JSON y UTF-8."""
    
    def serialize(self, data):
        """Convierte un objeto Python (dict, list) a bytes."""
        try:
            json_string = json.dumps(data)
            return json_string.encode('utf-8')
        except (TypeError, ValueError) as e:
            raise Exception(f"Error de serialización: {e}")

    def deserialize(self, data_bytes):
        """Convierte bytes (UTF-8) de vuelta a un objeto Python."""
        try:
            json_string = data_bytes.decode('utf-8')
            return json.loads(json_string)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise Exception(f"Error de deserialización: {e}")

# Instancia global para ser usada por ambos servidores
serializer = JsonSerializer()