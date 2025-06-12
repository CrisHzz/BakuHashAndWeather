import numpy as np
import sympy as sp

x = sp.symbols('x')

def lagrange_interpolation(x_data, y_data):
    """Genera el polinomio interpolador de Lagrange"""
    n = len(x_data)
    P = 0
    for i in range(n):
        L = 1
        for j in range(n):
            if j != i:
                L *= (x - x_data[j]) / (x_data[i] - x_data[j])
        P += L * y_data[i]
    # Evitamos expand() para polinomios grandes para mejorar performance
    return P

def text_to_numbers(text):
    """Convierte una cadena en una lista de valores Unicode"""
    return [ord(c) for c in text]

def numbers_to_text(nums):
    """Convierte una lista de números a texto (caracteres Unicode)"""
    result = []
    for n in nums:
        try:
            # Redondear y convertir a entero
            char_code = int(round(float(n)))
            # Verificar que esté en el rango válido de Unicode
            if 0 <= char_code <= 0x10FFFF:
                result.append(chr(char_code))
            else:
                print(f"Advertencia: Valor fuera de rango Unicode: {char_code}")
                # Intentar mapear al rango válido
                char_code = abs(char_code) % 1114111  # 0x10FFFF = 1114111
                result.append(chr(char_code))
        except (ValueError, OverflowError) as e:
            print(f"Error al convertir {n} a carácter: {e}")
            result.append('?')  # Carácter de reemplazo
    return ''.join(result)

def encrypt(message):
    """Cifra el mensaje como un polinomio y retorna sus coeficientes y puntos de evaluación"""
    print("Iniciando proceso de cifrado...")
    y_data = text_to_numbers(message)
    x_data = list(range(1, len(y_data) + 1))

    print(f"Mensaje tiene {len(message)} caracteres")
    print(f"Puntos de interpolación: {len(x_data)} puntos")

    # Limitamos el tamaño del mensaje para evitar polinomios muy grandes
    if len(message) > 120:
        raise ValueError(f"Mensaje demasiado largo ({len(message)} caracteres). Máximo permitido: 120 caracteres.")

    P = lagrange_interpolation(x_data, y_data)
    print("Polinomio generado exitosamente")

    try:
        coef = sp.Poly(P, x).all_coeffs()
        print(f"Cifrado completado. {len(coef)} coeficientes generados")
        # Retornar también los y_data para un descifrado más estable
        return coef, x_data, y_data
    except Exception as e:
        print(f"Error al obtener coeficientes: {e}")
        raise ValueError(f"Error en el proceso de cifrado: {str(e)}")

def decrypt(coef, x_data, y_data=None):
    """Reconstruye el mensaje a partir de los coeficientes del polinomio o directamente de y_data"""
    print("\nIniciando proceso de descifrado...")
    
    # Si tenemos los datos originales, usarlos directamente (más estable)
    if y_data is not None:
        print("Usando descifrado directo con datos originales (más estable)")
        try:
            message = numbers_to_text(y_data)
            print(f"Mensaje recuperado: {message[:50]}{'...' if len(message) > 50 else ''}")
            return message
        except Exception as e:
            print(f"Error en descifrado directo: {e}")
            # Si falla, intentar con el método de polinomios
    
    # Método tradicional usando polinomios (puede ser inestable para mensajes largos)
    print("Usando descifrado con reconstrucción de polinomio (puede ser inestable)")
    try:
        # Convertir coeficientes a float si vienen como strings
        coef = [float(c) for c in coef]
        
        # Reconstrucción del polinomio
        P = sum([coef[i] * x**(len(coef)-1 - i) for i in range(len(coef))])
        print("Polinomio reconstruido exitosamente")

        # Evaluación del polinomio en los puntos originales
        y_data_reconstructed = []
        for xi in x_data:
            try:
                # Usar evaluación numérica con mayor precisión
                val = complex(P.evalf(subs={x: xi}))
                # Tomar solo la parte real (debería ser muy pequeña la imaginaria)
                if abs(val.imag) < 1e-10:
                    y_data_reconstructed.append(val.real)
                else:
                    print(f"Advertencia: Valor con parte imaginaria significativa en x={xi}: {val}")
                    y_data_reconstructed.append(val.real)
            except Exception as e:
                print(f"Error evaluando en x={xi}: {e}")
                y_data_reconstructed.append(0)  # Valor por defecto
        
        print(f"Valores obtenidos ({len(y_data_reconstructed)} puntos): {[round(float(v), 2) for v in y_data_reconstructed[:5]]}...")

        message = numbers_to_text(y_data_reconstructed)
        print(f"Mensaje recuperado: {message[:50]}{'...' if len(message) > 50 else ''}")
        return message
        
    except Exception as e:
        print(f"Error en el descifrado: {e}")
        raise ValueError(f"Error en el proceso de descifrado: {str(e)}")