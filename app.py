from flask import Flask, render_template, url_for, request, jsonify
from Weather.model import predecir_temp_maxima

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

if __name__ == '__main__':
    app.run(debug=True)