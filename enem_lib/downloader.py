# enem_lib/downloader.py
import requests
import zipfile
import pandas as pd
import os
import tempfile
from io import BytesIO
from tqdm import tqdm
import time
import shutil

class ENEMDownloader:
    def __init__(self, max_retries=5, delay_between_retries=10):
        self.max_retries = max_retries
        self.delay_between_retries = delay_between_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def download_enem_data(self, anos: list) -> dict:
        resultados = {}
        anos_restantes = anos.copy()
        tentativa_global = 1
        
        while anos_restantes and tentativa_global <= self.max_retries:
            print(f"\n📋 TENTATIVA GLOBAL {tentativa_global}")
            print(f"📅 Anos restantes: {len(anos_restantes)}")
            print("=" * 50)
            
            anos_processados = []
            
            for ano in anos_restantes:
                print(f"\n🔄 Processando ano {ano} (tentativa {tentativa_global})...")
                
                try:
                    sucesso = self._process_single_year(ano)
                    if sucesso:
                        resultados[str(ano)] = "Sucesso"
                        anos_processados.append(ano)
                        print(f"✅ Ano {ano} concluído com sucesso!")
                    else:
                        print(f"⚠️  Ano {ano} falhou, tentando novamente na próxima rodada")
                
                except Exception as e:
                    print(f"❌ Erro inesperado no ano {ano}: {str(e)}")
            
            for ano in anos_processados:
                anos_restantes.remove(ano)
            
            if anos_restantes and tentativa_global < self.max_retries:
                print(f"\n⏳ Aguardando {self.delay_between_retries} segundos antes da próxima tentativa...")
                time.sleep(self.delay_between_retries)
            
            tentativa_global += 1
        
        for ano in anos_restantes:
            resultados[str(ano)] = "Falha após todas as tentativas"
        
        return resultados
    
    def _process_single_year(self, ano: int) -> bool:
        temp_dir = tempfile.mkdtemp()
        
        try:
            url = f'https://download.inep.gov.br/microdados/microdados_enem_{ano}.zip'
            
            try:
                head_response = self.session.head(url, timeout=30, allow_redirects=True)
                if head_response.status_code != 200:
                    print(f"❌ Arquivo não disponível para {ano} (status: {head_response.status_code})")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro ao verificar disponibilidade: {str(e)}")
                return False
            
            print(f"📥 Baixando dados do ENEM {ano}...")
            response = self.session.get(url, stream=True, timeout=120)
            
            if response.status_code != 200:
                print(f"❌ Erro no download: Status {response.status_code}")
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            if total_size == 0:
                print("❌ Arquivo vazio ou indisponível")
                return False
            
            print(f"📦 Tamanho do arquivo: {total_size / (1024*1024):.2f} MB")
            
            print("📦 Processando arquivo ZIP...")
            zip_data = BytesIO()
            
            with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Baixando {ano}") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        zip_data.write(chunk)
                        pbar.update(len(chunk))
            
            print("✅ Download concluído")
            
            print("📂 Extraindo e processando arquivos...")
            zip_data.seek(0)
            
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                csv_files = []
                for file_name in zip_ref.namelist():
                    if file_name.endswith('.csv'):
                        file_info = zip_ref.getinfo(file_name)
                        csv_files.append((file_name, file_info.file_size))
                
                if not csv_files:
                    print("❌ Nenhum arquivo CSV encontrado no ZIP")
                    return False
                
                csv_files.sort(key=lambda x: x[1], reverse=True)
                csv_file = csv_files[0][0]
                
                print(f"📊 Arquivo CSV encontrado: {csv_file} ({csv_files[0][1]/1024/1024:.2f} MB)")
                
                csv_temp_path = os.path.join(temp_dir, os.path.basename(csv_file))
                with zip_ref.open(csv_file) as source, open(csv_temp_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                print("🔄 Lendo e convertendo dados...")
                
                with open(csv_temp_path, 'rb') as f:
                    sample = f.read(50000).decode('latin-1', errors='ignore')
                    
                    if sample.count(';') > sample.count(','):
                        separator = ';'
                    else:
                        separator = ','
                    
                    has_header = any(word in sample.upper() for word in 
                                ['NU_INSCRICAO', 'TP_FAIXA_ETARIA', 'TP_SEXO', 'CO_MUNICIPIO'])
                
                os.makedirs('dados_enem', exist_ok=True)
                parquet_path = f'dados_enem/microdados_enem_{ano}.parquet'
                
                if os.path.exists(parquet_path):
                    os.remove(parquet_path)
                
                print("💾 Convertendo para Parquet (isso pode demorar)...")
                
                chunk_size = 50000
                total_rows = 0
                
                print("📊 Contando número total de linhas...")
                with open(csv_temp_path, 'r', encoding='latin-1') as f:
                    total_csv_lines = sum(1 for _ in f) - (1 if has_header else 0)
                
                print(f"📈 Total de linhas no CSV: {total_csv_lines}")
                
                chunks = []
                for i, chunk in enumerate(pd.read_csv(csv_temp_path, 
                                                    encoding='latin-1', 
                                                    sep=separator,
                                                    chunksize=chunk_size,
                                                    low_memory=False,
                                                    header=0 if has_header else None)):
                    chunks.append(chunk)
                    total_rows += len(chunk)
                    
                    if i % 10 == 0:
                        print(f"📖 Processados {total_rows}/{total_csv_lines} registros ({total_rows/total_csv_lines*100:.1f}%)")
                
                print("💾 Salvando como Parquet...")
                df = pd.concat(chunks, ignore_index=True)
                
                try:
                    df.to_parquet(parquet_path, index=False, engine='fastparquet')
                except:
                    try:
                        df.to_parquet(parquet_path, index=False, engine='pyarrow')
                    except Exception as e:
                        print(f"❌ Erro ao salvar Parquet: {e}")
                        return False
                
                print(f"✅ Conversão concluída: {total_rows} registros salvos em {parquet_path}")
                
                if os.path.exists(parquet_path) and os.path.getsize(parquet_path) > 0:
                    try:
                        sample_df = pd.read_parquet(parquet_path, engine='fastparquet')
                    except:
                        try:
                            sample_df = pd.read_parquet(parquet_path, engine='pyarrow')
                        except Exception as e:
                            print(f"❌ Erro ao ler Parquet: {e}")
                            return False
                    
                    print(f"📋 Amostra do Parquet: {len(sample_df.columns)} colunas, {len(sample_df)} linhas")
                    return True
                else:
                    print("❌ Falha na criação do arquivo Parquet")
                    return False
                
        except Exception as e:
            print(f"❌ Erro no processamento: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)