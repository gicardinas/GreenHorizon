import time
from decisao_irrigacao import processar_decisao

def executar_simulacao():
    # Simula 5 situações diferentes de umidade
    testes_umidade = [15, 25, 35, 45, 10]
    
    print("🚀 Iniciando Simulação de 5 Ciclos para o Green Horizon...")
    
    for i, umidade in enumerate(testes_umidade, 1):
        print(f"\n🔄 TESTE {i}: Simulando Umidade em {umidade}%")
        processar_decisao(umidade)
        # Pequena pausa para os timestamps não ficarem idênticos
        time.sleep(1) 

    print("\n✅ Simulação concluída! Verifique o banco etl/green_horizon.db")

if __name__ == "__main__":
    executar_simulacao()