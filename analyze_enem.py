from enem_lib.analysis import ENEMAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def main():
    print("=" * 60)
    print("📊 ANALISADOR DE DADOS DO ENEM - PARAÍBA")
    print("=" * 60)
    
    # Inicializar analisador
    analyzer = ENEMAnalyzer()
    
    # Carregar dados disponíveis
    available_years = []
    for year in range(2014, 2025):
        parquet_path = f'dados_enem/microdados_enem_{year}.parquet'
        if os.path.exists(parquet_path):
            available_years.append(year)
    
    if not available_years:
        print("❌ Nenhum dado encontrado. Execute o download primeiro.")
        return
    
    print(f"📅 Anos disponíveis: {available_years}")
    
    # Carregar dados
    analyzer.load_data(available_years)
    
    if not analyzer.loaded_years:
        print("❌ Nenhum dado pôde ser carregado.")
        return
    
    # Análise 1: Correlações simples por ano
    print("\n" + "=" * 60)
    print("🔍 ANÁLISE 1: CORRELAÇÕES SIMPLES")
    print("=" * 60)
    
    correlations_by_year = {}
    for year in analyzer.loaded_years:
        print(f"\n📈 Analisando {year}...")
        correlations, data = analyzer.analyze_correlations(year)
        
        if correlations:
            correlations_by_year[year] = correlations
            print(f"   Participantes válidos: {len(data)}")
            for area, corr in correlations.items():
                area_name = area.replace('NU_NOTA_', '').replace('_', ' ')
                print(f"   {area_name}: {corr:.3f}")
    
    # Gráfico das correlações ao longo dos anos
    if correlations_by_year:
        analyzer.plot_correlations(correlations_by_year)
    
    # Análise 2: Bootstrap para um ano específico
    print("\n" + "=" * 60)
    print("🔍 ANÁLISE 2: BOOTSTRAP COM INTERVALOS DE CONFIANÇA")
    print("=" * 60)
    
    # Escolher o ano mais recente para análise detalhada
    latest_year = max(analyzer.loaded_years)
    print(f"📊 Analisando {latest_year} com bootstrap...")
    
    results, data = analyzer.analyze_with_bootstrap(latest_year, n_iterations=1000)
    
    if results:
        print(f"   Participantes válidos: {len(data)}")
        for area, result in results.items():
            area_name = area.replace('NU_NOTA_', '').replace('_', ' ')
            print(f"   {area_name}: {result['correlacao']:.3f} (IC 95%: {result['intervalo_confianca'][0]:.3f} - {result['intervalo_confianca'][1]:.3f})")
        
        # Gráficos dos resultados do bootstrap
        analyzer.plot_bootstrap_results(results, latest_year)
    
    # Análise 3: Estatísticas descritivas
    print("\n" + "=" * 60)
    print("🔍 ANÁLISE 3: ESTATÍSTICAS DESCRITIVAS")
    print("=" * 60)
    
    for year in analyzer.loaded_years:
        paraiba_data = analyzer.get_paraiba_data(year)
        if paraiba_data is not None:
            df = analyzer.categorize_parent_education(paraiba_data)
            valid_data = df[['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO', 'EDUCACAO_PAIS']].dropna()
            
            print(f"\n📊 {year}:")
            print(f"   Participantes Paraíba: {len(paraiba_data)}")
            print(f"   Dados válidos para análise: {len(valid_data)}")
            print(f"   Distribuição educação pais:")
            print(f"     Nível 1 (A-D): {(valid_data['EDUCACAO_PAIS'] == 1).sum()} ({((valid_data['EDUCACAO_PAIS'] == 1).sum()/len(valid_data)*100):.1f}%)")
            print(f"     Nível 2 (E-G): {(valid_data['EDUCACAO_PAIS'] == 2).sum()} ({((valid_data['EDUCACAO_PAIS'] == 2).sum()/len(valid_data)*100):.1f}%)")
            
            # Médias das notas por nível de educação dos pais
            for nivel in [1, 2]:
                nivel_data = valid_data[valid_data['EDUCACAO_PAIS'] == nivel]
                if len(nivel_data) > 0:
                    print(f"   Médias notas - Nível {nivel}:")
                    for area in ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']:
                        area_name = area.replace('NU_NOTA_', '')[:5]
                        media = nivel_data[area].mean()
                        print(f"     {area_name}: {media:.1f}")

if __name__ == "__main__":
    main()