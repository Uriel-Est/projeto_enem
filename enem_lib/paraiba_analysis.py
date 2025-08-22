# enem_lib/paraiba_analysis.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import os

class ParaibaENEMAnalyzer:
    def __init__(self, data_dir='dados_enem'):
        self.data_dir = data_dir
        self.data = {}
        self.loaded_years = []
        
    def load_data(self, years: List[int]) -> None:
        """Carrega os dados Parquet dos anos especificados"""
        for year in years:
            parquet_path = f'{self.data_dir}/microdados_enem_{year}.parquet'
            if os.path.exists(parquet_path):
                try:
                    print(f"📂 Carregando dados de {year}...")
                    self.data[year] = pd.read_parquet(parquet_path)
                    self.loaded_years.append(year)
                    print(f"✅ {year} carregado: {len(self.data[year])} registros")
                except Exception as e:
                    print(f"❌ Erro ao carregar {year}: {e}")
            else:
                print(f"⚠️  Arquivo não encontrado para {year}")
    
    def get_paraiba_data(self, year: int) -> pd.DataFrame:
        """Filtra dados apenas para a Paraíba usando SG_UF_PROVA = 'PB'"""
        if year not in self.data:
            print(f"❌ Dados de {year} não carregados")
            return None
        
        df = self.data[year].copy()
        
        # Verificar se a coluna SG_UF_PROVA existe
        if 'SG_UF_PROVA' not in df.columns:
            print(f"❌ Coluna SG_UF_PROVA não encontrada em {year}")
            return None
        
        # Filtrar para Paraíba
        paraiba_data = df[df['SG_UF_PROVA'] == 'PB']
        print(f"📊 Dados da Paraíba ({year}): {len(paraiba_data)} participantes")
        return paraiba_data
    
    def categorize_parent_education(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categoriza a educação dos pais conforme solicitado:
        Q002 (educação do pai) e Q003 (educação da mãe)
        A:D = 1 (informal/colarinho azul)
        E:G = 2 (colarinho azul técnico/colarinho branco)
        """
        df = df.copy()
        
        # Verificar se as colunas existem
        if 'Q002' not in df.columns or 'Q003' not in df.columns:
            print("⚠️  Colunas Q002 e/ou Q003 não encontradas")
            return df
        
        # Mapeamento das categorias
        education_map = {
            'A': 1, 'B': 1, 'C': 1, 'D': 1,  # Informal/colarinho azul
            'E': 2, 'F': 2, 'G': 2,           # Colarinho azul técnico/colarinho branco
            'H': np.nan, ' ': np.nan, '': np.nan  # Ignorar sem resposta
        }
        
        # Aplicar mapeamento
        df['Q002_CAT'] = df['Q002'].map(education_map)
        df['Q003_CAT'] = df['Q003'].map(education_map)
        
        # Criar uma variável combinada (média da educação dos pais)
        df['EDUCACAO_PAIS'] = df[['Q002_CAT', 'Q003_CAT']].mean(axis=1)
        
        return df
    
    def analyze_correlations(self, year: int) -> Dict:
        """Analisa correlações entre educação dos pais e notas"""
        paraiba_data = self.get_paraiba_data(year)
        if paraiba_data is None or len(paraiba_data) == 0:
            return {}
        
        # Categorizar educação dos pais
        df = self.categorize_parent_education(paraiba_data)
        
        # Selecionar colunas de notas
        note_columns = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        
        # Verificar quais colunas de notas existem
        available_note_columns = [col for col in note_columns if col in df.columns]
        
        if not available_note_columns:
            print("❌ Nenhuma coluna de nota encontrada")
            return {}
        
        # Filtrar apenas registros com notas e educação dos pais válidos
        valid_data = df[available_note_columns + ['EDUCACAO_PAIS']].dropna()
        
        if len(valid_data) == 0:
            print("❌ Nenhum dado válido após filtragem")
            return {}
        
        # Calcular correlações
        correlations = {}
        for note_col in available_note_columns:
            correlation = valid_data['EDUCACAO_PAIS'].corr(valid_data[note_col])
            correlations[note_col] = correlation
        
        # Calcular nota geral (média das áreas)
        valid_data['NOTA_GERAL'] = valid_data[available_note_columns].mean(axis=1)
        correlations['NOTA_GERAL'] = valid_data['EDUCACAO_PAIS'].corr(valid_data['NOTA_GERAL'])
        
        return correlations, valid_data
    
    def print_correlations(self, correlations_dict: Dict[int, Dict]):
        """Imprime correlações por ano em formato de texto"""
        print("\n" + "=" * 80)
        print("CORRELAÇÕES ENTRE EDUCAÇÃO DOS PAIS E DESEMPENHO NO ENEM - PARAÍBA")
        print("=" * 80)
        
        areas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NOTA_GERAL']
        area_names = ['Ciências Naturais', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação', 'Nota Geral']
        
        # Cabeçalho da tabela
        print(f"{'Ano':<6}", end="")
        for area_name in area_names:
            print(f"{area_name:<20}", end="")
        print()
        
        print("-" * 126)
        
        # Dados da tabela
        for year, corrs in correlations_dict.items():
            print(f"{year:<6}", end="")
            for area in areas:
                if area in corrs:
                    print(f"{corrs[area]:<20.3f}", end="")
                else:
                    print(f"{'N/A':<20}", end="")
            print()
    
    def bootstrap_correlation(self, data: pd.DataFrame, column: str, n_iterations: int = 1000) -> Tuple[float, List[float]]:
        """
        Realiza bootstrap para estimar a correlação e seu intervalo de confiança
        """
        correlations = []
        n = len(data)
        
        for _ in range(n_iterations):
            # Amostra com reposição
            sample = data.sample(n, replace=True)
            correlation = sample['EDUCACAO_PAIS'].corr(sample[column])
            correlations.append(correlation)
        
        # Calcular intervalo de confiança 95%
        mean_corr = np.mean(correlations)
        ci_lower = np.percentile(correlations, 2.5)
        ci_upper = np.percentile(correlations, 97.5)
        
        return mean_corr, (ci_lower, ci_upper), correlations
    
    def analyze_with_bootstrap(self, year: int, n_iterations: int = 1000) -> Dict:
        """Análise com bootstrap para estimar intervalos de confiança"""
        paraiba_data = self.get_paraiba_data(year)
        if paraiba_data is None or len(paraiba_data) == 0:
            return {}
        
        # Categorizar educação dos pais
        df = self.categorize_parent_education(paraiba_data)
        
        # Selecionar colunas de notas
        note_columns = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        
        # Verificar quais colunas de notas existem
        available_note_columns = [col for col in note_columns if col in df.columns]
        
        # Filtrar apenas registros com notas e educação dos pais válidos
        valid_data = df[available_note_columns + ['EDUCACAO_PAIS']].dropna()
        
        if len(valid_data) == 0:
            return {}
        
        # Calcular nota geral
        valid_data['NOTA_GERAL'] = valid_data[available_note_columns].mean(axis=1)
        
        # Realizar bootstrap para cada área
        results = {}
        for note_col in available_note_columns + ['NOTA_GERAL']:
            mean_corr, ci, corr_dist = self.bootstrap_correlation(valid_data, note_col, n_iterations)
            results[note_col] = {
                'correlacao': mean_corr,
                'intervalo_confianca': ci,
                'distribuicao': corr_dist
            }
        
        return results, valid_data
    
    def print_bootstrap_results(self, results: Dict, year: int):
        """Imprime resultados do bootstrap em formato de texto"""
        print(f"\nANÁLISE BOOTSTRAP - ENEM {year}")
        print("=" * 50)
        
        areas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NOTA_GERAL']
        area_names = ['Ciências Naturais', 'Ciências Humanas', 'Linguagens', 'Matemática', 'Redação', 'Nota Geral']
        
        print(f"{'Área':<20} {'Correlação':<12} {'IC 95% Inferior':<18} {'IC 95% Superior':<18}")
        print("-" * 70)
        
        for area, area_name in zip(areas, area_names):
            if area in results:
                result = results[area]
                print(f"{area_name:<20} {result['correlacao']:<12.3f} {result['intervalo_confianca'][0]:<18.3f} {result['intervalo_confianca'][1]:<18.3f}")
    
    def print_descriptive_stats(self, year: int):
        """Imprime estatísticas descritivas"""
        paraiba_data = self.get_paraiba_data(year)
        if paraiba_data is None or len(paraiba_data) == 0:
            return
        
        df = self.categorize_parent_education(paraiba_data)
        
        # Selecionar colunas de notas
        note_columns = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        
        # Verificar quais colunas de notas existem
        available_note_columns = [col for col in note_columns if col in df.columns]
        
        valid_data = df[available_note_columns + ['EDUCACAO_PAIS']].dropna()
        
        if len(valid_data) == 0:
            return
        
        print(f"\nESTATÍSTICAS DESCRITIVAS - ENEM {year}")
        print("=" * 50)
        print(f"Participantes Paraíba: {len(paraiba_data)}")
        print(f"Dados válidos para análise: {len(valid_data)}")
        
        # Distribuição educação dos pais
        nivel_1 = (valid_data['EDUCACAO_PAIS'] == 1).sum()
        nivel_2 = (valid_data['EDUCACAO_PAIS'] == 2).sum()
        total = len(valid_data)
        
        if total > 0:
            print(f"\nDistribuição Educação dos Pais:")
            print(f"Nível 1 (A-D): {nivel_1} ({nivel_1/total*100:.1f}%)")
            print(f"Nível 2 (E-G): {nivel_2} ({nivel_2/total*100:.1f}%)")
            
            # Médias das notas por nível
            print(f"\nMédias das Notas por Nível de Educação dos Pais:")
            for nivel in [1, 2]:
                nivel_data = valid_data[valid_data['EDUCACAO_PAIS'] == nivel]
                if len(nivel_data) > 0:
                    print(f"\nNível {nivel}:")
                    for area in available_note_columns:
                        area_name = area.replace('NU_NOTA_', '').replace('_', ' ').title()
                        media = nivel_data[area].mean()
                        print(f"  {area_name}: {media:.1f}")