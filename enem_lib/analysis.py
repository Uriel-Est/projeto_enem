# enem_lib/analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import os

class ENEMAnalyzer:
    def __init__(self, data_dir='dados_enem'):
        self.data_dir = data_dir
        self.data = {}
        self.loaded_years = []
        
    def load_data(self, years: List[int]) -> None:
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
    
    def get_uf_data(self, year: int, uf: str) -> pd.DataFrame:
        if year not in self.data:
            print(f"❌ Dados de {year} não carregados")
            return None
        
        df = self.data[year].copy()
        
        # Verificar diferentes possíveis nomes de coluna para UF
        uf_columns = [col for col in df.columns if 'UF' in col or 'ESTADO' in col]
        
        if not uf_columns:
            print(f"❌ Nenhuma coluna de UF encontrada em {year}")
            return None
        
        uf_data = None
        for col in uf_columns:
            try:
                # Tentar encontrar a UF na coluna (pode ser código numérico ou string)
                if df[col].dtype == 'object' or df[col].dtype.name == 'string':
                    uf_data = df[df[col].astype(str).str.contains(uf, na=False)]
                else:
                    # Se for numérico, tentar converter UF para número
                    uf_num = int(uf)
                    uf_data = df[df[col] == uf_num]
                
                if len(uf_data) > 0:
                    print(f"📊 Dados da UF {uf} ({year}) encontrados na coluna {col}: {len(uf_data)} participantes")
                    break
            except:
                continue
        
        if uf_data is None or len(uf_data) == 0:
            print(f"❌ UF {uf} não encontrada em {year}")
            return None
        
        return uf_data
    
    def categorize_work_status(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Mapeamento do status de trabalho dos pais (Q002 e Q003)
        work_status_map = {
            'A': 'Não trabalha', 'B': 'Trabalha em casa', 'C': 'Trabalha fora (informal)',
            'D': 'Trabalha fora (formal)', 'E': 'Aposentado', 'F': 'Desempregado',
            'G': 'Outro', 'H': np.nan, ' ': np.nan, '': np.nan
        }
        
        # Aplicar mapeamento se as colunas existirem
        for col in ['Q002', 'Q003']:
            if col in df.columns:
                df[f'{col}_STATUS'] = df[col].map(work_status_map)
        
        return df
    
    def analyze_work_status_vs_grades(self, year: int, uf: str) -> Dict:
        uf_data = self.get_uf_data(year, uf)
        if uf_data is None:
            return {}
        
        # Categorizar status de trabalho
        df = self.categorize_work_status(uf_data)
        
        # Selecionar colunas de notas
        note_columns = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        
        # Verificar quais colunas de notas existem
        available_note_columns = [col for col in note_columns if col in df.columns]
        
        if not available_note_columns:
            print("❌ Nenhuma coluna de nota encontrada")
            return {}
        
        # Calcular nota geral
        df['NOTA_GERAL'] = df[available_note_columns].mean(axis=1)
        
        # Analisar relação entre trabalho dos pais e notas
        results = {}
        
        for parent_col in ['Q002_STATUS', 'Q003_STATUS']:
            if parent_col not in df.columns:
                continue
            
            # Filtrar dados válidos
            valid_data = df[[parent_col, 'NOTA_GERAL'] + available_note_columns].dropna()
            
            if len(valid_data) == 0:
                continue
            
            # Calcular médias por categoria de trabalho
            parent_work_stats = valid_data.groupby(parent_col).agg({
                'NOTA_GERAL': ['mean', 'std', 'count']
            }).round(2)
            
            results[parent_col] = parent_work_stats
        
        return results, df
    
    def analyze_income_vs_grades(self, year: int, uf: str) -> Dict:
        uf_data = self.get_uf_data(year, uf)
        if uf_data is None:
            return {}
        
        # Verificar se existe coluna de renda (Q006)
        if 'Q006' not in uf_data.columns:
            print("❌ Coluna de renda (Q006) não encontrada")
            return {}
        
        # Selecionar colunas de notas
        note_columns = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']
        
        # Verificar quais colunas de notas existem
        available_note_columns = [col for col in note_columns if col in uf_data.columns]
        
        if not available_note_columns:
            print("❌ Nenhuma coluna de nota encontrada")
            return {}
        
        # Filtrar dados válidos
        valid_data = uf_data[['Q006'] + available_note_columns].dropna()
        
        if len(valid_data) == 0:
            print("❌ Nenhum dado válido após filtragem")
            return {}
        
        # Calcular nota geral
        valid_data['NOTA_GERAL'] = valid_data[available_note_columns].mean(axis=1)
        
        # Calcular correlação entre renda e notas
        # Primeiro, converter renda para valores numéricos (as categorias são A, B, C, ...)
        income_map = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
            'I': 9, 'J': 10, 'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16,
            'Q': 17
        }
        
        valid_data['RENDA_NUM'] = valid_data['Q006'].map(income_map)
        
        correlations = {}
        for note_col in available_note_columns + ['NOTA_GERAL']:
            correlation = valid_data['RENDA_NUM'].corr(valid_data[note_col])
            correlations[note_col] = correlation
        
        # Calcular médias por faixa de renda
        income_stats = valid_data.groupby('Q006').agg({
            'NOTA_GERAL': ['mean', 'std', 'count']
        }).round(2)
        
        return {
            'correlacoes': correlations,
            'estatisticas_renda': income_stats
        }, valid_data