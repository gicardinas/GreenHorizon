import requests

def consultar_clima():
    """
    Consulta a API Open-Meteo para as próximas 3 horas.
    Retorna médias e somas para análise preditiva.
    """
    lat, lon = -22.9519, -43.2105
    #  Pega API
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation&forecast_days=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Pega os dados das próximas 3 horas
        temps = data['hourly']['temperature_2m'][0:3]
        chuvas = data['hourly']['precipitation'][0:3]
        
        return {
            "temperatura_media": round(sum(temps) / len(temps), 1),
            "volume_chuva_total": round(sum(chuvas), 2),
            "vai_chover": sum(chuvas) > 0.1, # Considera chuva se for > 0.1mm
            "probabilidade_chuva": 100 if sum(chuvas) > 0.5 else 0 
        }
    except Exception as e:
        print(f"⚠️ Erro na API de Clima: {e}")
        return None