# main.py
from enem_lib.downloader import ENEMDownloader
from enem_lib.numpy_ops import exemplo_algebra_linear, exemplo_numeros_aleatorios
from enem_lib.analysis import ENEMAnalyzer
import time

def main():
    print("=" * 60)
    print("📊 PROCESSADOR DE DADOS DO ENEM - ANÁLISE POR UF")
    print("=" * 60)
    
    # Pedir anos para processar
    anos_input = input("Digite os anos para baixar (ex: 2014:2024 ou 2014,2015,2016): ")
    
    # Processar input
    if ':' in anos_input:
        try:
            inicio, fim = anos_input.split(':')
            anos = [int(ano) for ano in range(int(inicio), int(fim) + 1)]
        except ValueError:
            print("❌ Formato de intervalo inválido. Use ex: 2014:2024")
            return
    else:
        try:
            anos = [int(ano.strip()) for ano in anos_input.split(",")]
        except ValueError:
            print("❌ Formato inválido. Use ex: 2014,2015,2016")
            return
    
    # Verificar anos válidos
    anos_validos = []
    for ano in anos:
        if 1998 <= ano <= 2024:
            anos_validos.append(ano)
        else:
            print(f"⚠️  Ano inválido: {ano}")
    
    if not anos_validos:
        print("❌ Nenhum ano válido fornecido")
        return
    
    print(f"📅 Anos a processar: {', '.join(map(str, anos_validos))}")
    
    # Pedir UF para análise
    uf = input("Digite a UF que deseja analisar (ex: PB, SP, RJ): ").strip().upper()
    
    confirmacao = input("Continuar? (s/n): ")
    if confirmacao.lower() != 's':
        print("Operação cancelada pelo usuário")
        return
    
    # Processar os anos
    inicio = time.time()
    
    downloader = ENEMDownloader(max_retries=5, delay_between_retries=10)
    resultados = downloader.download_enem_data(anos_validos)
    
    tempo_total = time.time() - inicio
    
    # Mostrar resultados do download
    print("\n" + "=" * 60)
    print("📋 RESULTADOS DO DOWNLOAD")
    print("=" * 60)
    
    sucessos = 0
    falhas = 0
    
    for ano, resultado in resultados.items():
        status = "✅" if resultado == "Sucesso" else "❌"
        print(f"{status} {ano}: {resultado}")
        
        if resultado == "Sucesso":
            sucessos += 1
        else:
            falhas += 1
    
    print(f"\n📊 Resumo: {sucessos} sucesso(s), {falhas} falha(s)")
    print(f"⏱️  Tempo total: {tempo_total/60:.1f} minutos")
    
    # Análise dos dados
    if sucessos > 0:
        print("\n" + "=" * 60)
        print("📈 ANÁLISE DOS DADOS")
        print("=" * 60)
        
        analyzer = ENEMAnalyzer()
        analyzer.load_data(anos_validos)
        
        # Analisar relação entre trabalho dos pais e notas
        print(f"\n🔍 Analisando relação entre trabalho dos pais e notas na UF {uf}")
        for ano in anos_validos:
            if str(ano) in resultados and resultados[str(ano)] == "Sucesso":
                print(f"\n📊 Ano {ano}:")
                resultados_trabalho, dados = analyzer.analyze_work_status_vs_grades(ano, uf)
                
                if resultados_trabalho:
                    for parent_col, stats in resultados_trabalho.items():
                        parent_name = "Pai" if "Q002" in parent_col else "Mãe"
                        print(f"\n📋 Estatísticas por trabalho do(a) {parent_name}:")
                        print(stats)
                else:
                    print("❌ Não foi possível analisar trabalho dos pais para este ano")
        
        # Analisar relação entre renda e notas
        print(f"\n💰 Analisando relação entre renda e notas na UF {uf}")
        for ano in anos_validos:
            if str(ano) in resultados and resultados[str(ano)] == "Sucesso":
                print(f"\n📊 Ano {ano}:")
                resultados_renda, dados = analyzer.analyze_income_vs_grades(ano, uf)
                
                if resultados_renda:
                    print("\n📈 Correlações entre renda e notas:")
                    for nota, correlacao in resultados_renda['correlacoes'].items():
                        nome_nota = nota.replace('NU_NOTA_', '').replace('_', ' ').title()
                        if nota == 'NOTA_GERAL':
                            nome_nota = 'Nota Geral'
                        print(f"{nome_nota}: {correlacao:.3f}")
                    
                    print("\n📊 Estatísticas por faixa de renda:")
                    print(resultados_renda['estatisticas_renda'])
                else:
                    print("❌ Não foi possível analisar renda para este ano")
        
        # Exemplos do NumPy
        print("\n" + "=" * 50)
        print("🧪 EXEMPLOS DO NUMPY COM DADOS DO ENEM")
        print("=" * 50)
        
        exemplo_algebra_linear()
        exemplo_numeros_aleatorios()
    else:
        print("\n⚠️  Não há dados do ENEM para analisar")
        print("📋 Executando exemplos com dados simulados...")
        
        print("\n" + "=" * 50)
        print("🧪 EXEMPLOS DO NUMPY (DADOS SIMULADOS)")
        print("=" * 50)
        
        exemplo_algebra_linear()
        exemplo_numeros_aleatorios()
    
    print("\n" + "=" * 50)
    print("🎉 PROCESSAMENTO CONCLUÍDO!")
    print("=" * 50)

if __name__ == "__main__":
    main()