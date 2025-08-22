# explore_data.py
import pandas as pd
import os

def explore_parquet_files():
    """Explora a estrutura dos arquivos Parquet"""
    data_dir = 'dados_enem'
    
    if not os.path.exists(data_dir):
        print("❌ Pasta 'dados_enem' não existe")
        return
    
    parquet_files = [f for f in os.listdir(data_dir) if f.endswith('.parquet')]
    
    if not parquet_files:
        print("❌ Nenhum arquivo Parquet encontrado")
        return
    
    print(f"📊 Encontrados {len(parquet_files)} arquivos Parquet")
    
    for file_name in parquet_files:
        file_path = os.path.join(data_dir, file_name)
        print(f"\n🔍 Explorando: {file_name}")
        
        try:
            # Ler o arquivo Parquet
            df = pd.read_parquet(file_path)
            
            print(f"📈 Total de registros: {len(df):,}")
            print(f"📋 Número de colunas: {len(df.columns)}")
            
            # Verificar colunas relacionadas a UF/localização
            uf_columns = [col for col in df.columns if 'UF' in col or 'ESTADO' in col or 'LOCAL' in col]
            print(f"📍 Colunas de localização: {uf_columns}")
            
            # Mostrar valores únicos nas colunas de UF (se existirem)
            for col in uf_columns:
                unique_values = df[col].unique()
                print(f"   Valores únicos em {col}: {unique_values[:10]}{'...' if len(unique_values) > 10 else ''}")
            
            # Verificar colunas de questões socioeconômicas
            q_columns = [col for col in df.columns if col.startswith('Q')]
            print(f"❓ Colunas de questionário: {q_columns[:10]}{'...' if len(q_columns) > 10 else ''}")
            
            # Verificar colunas de notas
            nota_columns = [col for col in df.columns if 'NOTA' in col]
            print(f"📝 Colunas de notas: {nota_columns}")
            
            # Verificar primeiras linhas
            print("\n📄 Primeiras 2 linhas:")
            print(df.head(2))
            
            # Verificar se há dados da Paraíba
            paraiba_found = False
            for col in uf_columns:
                if any('25' in str(val) or 'PB' in str(val) for val in df[col].unique()):
                    print(f"✅ Paraíba encontrada na coluna {col}")
                    paraiba_found = True
                    # Mostrar quantos registros da Paraíba
                    paraiba_data = df[df[col].astype(str).str.contains('25|PB')]
                    print(f"   Registros da Paraíba: {len(paraiba_data):,}")
                    
            if not paraiba_found:
                print("❌ Paraíba não encontrada em nenhuma coluna de UF")
                
        except Exception as e:
            print(f"❌ Erro ao explorar {file_name}: {e}")

if __name__ == "__main__":
    explore_parquet_files()