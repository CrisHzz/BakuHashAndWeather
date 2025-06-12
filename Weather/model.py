import numpy as np
import pandas as pd

dataset = pd.read_csv('./dataset/baku_past5years_weather.csv')

def minimos_cuadrados_multiple(X, y):
    # Agregar columna de 1's para el intercepto
    X_with_ones = np.column_stack([np.ones(len(X)), X])
    
    # Calcular (X^T X)^(-1) X^T y
    X_transpose = X_with_ones.T
    XTX = np.dot(X_transpose, X_with_ones)
    XTX_inv = np.linalg.inv(XTX)
    XTy = np.dot(X_transpose, y)
    
    coeficientes = np.dot(XTX_inv, XTy)
    
    intercepto = coeficientes[0]
    pendientes = coeficientes[1:]
    
    return pendientes, intercepto

def preparar_datos_temporales(df, dias_previos=3):

    # Ordenar el dataset por fecha
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    X_temp = []
    y_temp = []
    
    # Para cada punto en el tiempo (excepto los primeros días_previos)
    for i in range(dias_previos, len(df)-1):
        # Tomar los datos de los últimos días_previos
        features = []
        for j in range(dias_previos):
            idx = i - j
            features.extend([
                float(df.iloc[idx]['maxtemp_C']),
                float(df.iloc[idx]['mintemp_C']),
                float(df.iloc[idx]['sunHour'])
            ])
        X_temp.append(features)
        # La variable a predecir es la temperatura máxima del día siguiente
        y_temp.append(float(df.iloc[i+1]['maxtemp_C']))
    
    return np.array(X_temp), np.array(y_temp)

X, y = preparar_datos_temporales(dataset)

pendientes, intercepto = minimos_cuadrados_multiple(X, y)

def predecir_temp_maxima(datos_3dias):
    """
    Predice la temperatura máxima del día siguiente usando los datos de los últimos 3 días
    datos_3dias: lista de tuplas (maxtemp, mintemp, sunHour) para cada día
    """
    X_pred = []
    for dia in datos_3dias:
        X_pred.extend(dia)
    temp_pred = intercepto + np.dot(pendientes, X_pred)
    
    # Determinar el tipo de clima basado en la temperatura predicha
    if temp_pred >= 30:
        clima = "Caluroso"
    elif temp_pred >= 20:
        clima = "Templado"
    elif temp_pred >= 15:
        clima = "Fresco"
    elif temp_pred >= 10:
        clima = "Frío"
    elif temp_pred >= 5:
        clima = "Muy Frío"
    else:
        clima = "Helado"
    return {
        "temp": round(temp_pred, 2),
        "weather": clima
    }
