from flask import Flask, render_template, url_for, request, jsonify
from Weather.model import predecir_temp_maxima
from Hash.hash import encrypt , decrypt
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Obtener los datos del formulario
        data = request.get_json()
        
        # Extraer los datos de los 3 días en el formato que espera la función
        datos_3dias = [
            (float(data['day1-max']), float(data['day1-min']), float(data['day1-sun'])),
            (float(data['day2-max']), float(data['day2-min']), float(data['day2-sun'])),
            (float(data['day3-max']), float(data['day3-min']), float(data['day3-sun']))
        ]
        
        # Llamar a la función de predicción
        resultado = predecir_temp_maxima(datos_3dias)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/encrypt', methods=['POST'])
def encrypt_message():
    try:
        # Obtener el JSON del request
        data = request.get_json()
        json_text = data.get('jsonInput', '')
        
        # Validar que sea un JSON válido
        try:
            json.loads(json_text)
        except json.JSONDecodeError:
            return jsonify({'error': 'El texto ingresado no es un JSON válido'}), 400
        
        # Cifrar el mensaje
        coef, x_data, y_data = encrypt(json_text)
        
        # Convertir los coeficientes a float para serialización JSON
        coef_serializable = []
        for c in coef:
            try:
                # Convertir a float, manejando tipos complejos de SymPy
                if hasattr(c, 'evalf'):
                    # Es un objeto de SymPy
                    float_val = float(c.evalf())
                else:
                    # Es un número normal
                    float_val = float(c)
                coef_serializable.append(float_val)
            except (ValueError, TypeError) as e:
                print(f"Error convirtiendo coeficiente {c}: {e}")
                # En caso de error, convertir a string y luego intentar float
                try:
                    float_val = float(str(c))
                    coef_serializable.append(float_val)
                except:
                    # Si todo falla, usar 0 como valor por defecto
                    coef_serializable.append(0.0)
        
        return jsonify({
            'success': True,
            'original_message': json_text,
            'encrypted_coefficients': coef_serializable,
            'x_data': x_data,
            'y_data': y_data,  # Datos originales para descifrado estable
            'message': 'Mensaje cifrado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/decrypt', methods=['POST'])
def decrypt_message():
    try:
        # Obtener los datos del request
        data = request.get_json()
        coef = data.get('coefficients', [])
        x_data = data.get('x_data', [])
        y_data = data.get('y_data', None)  # Datos originales (opcional)
        
        if not coef or not x_data:
            return jsonify({'error': 'Se requieren los coeficientes y datos x para descifrar'}), 400
        
        # Descifrar el mensaje usando datos originales si están disponibles
        decrypted_message = decrypt(coef, x_data, y_data)
        
        return jsonify({
            'success': True,
            'decrypted_message': decrypted_message,
            'message': 'Mensaje descifrado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)