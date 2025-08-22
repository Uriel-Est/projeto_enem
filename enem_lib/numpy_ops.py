# enem_lib/numpy_ops.py
import numpy as np
import pandas as pd
import os

def exemplo_algebra_linear():
    print("\n🧮 EXEMPLO DE ÁLGEBRA LINEAR")
    print("=" * 40)
    
    enem_files = [f for f in os.listdir('dados_enem') if f.endswith('.parquet')]
    
    if enem_files:
        try:
            file_path = os.path.join('dados_enem', enem_files[0])
            df = pd.read_parquet(file_path)
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) >= 2:
                col1, col2 = numeric_cols[:2]
                
                data = df[[col1, col2]].dropna()
                data = data[np.isfinite(data).all(1)]
                
                if len(data) > 10:
                    cov_matrix = np.cov(data.values.T)
                    
                    print("Matriz de covariância entre duas variáveis numéricas:")
                    print(cov_matrix)
                    
                    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
                    
                    print(f"\nAutovalores: {eigenvalues}")
                    print("Autovetores:")
                    print(eigenvectors)
                    
                    return cov_matrix, eigenvalues, eigenvectors
            
        except Exception as e:
            print(f"Erro ao processar dados do ENEM: {str(e)}")
    
    print("Usando dados simulados (não foi possível acessar dados do ENEM)")
    
    notas = np.array([
        [650, 700, 600, 650],
        [550, 600, 750, 500],
        [800, 850, 780, 820],
        [450, 500, 480, 520],
        [720, 680, 710, 690]
    ])
    
    print("Matriz de notas (alunos x provas):")
    print(notas)
    
    cov_matrix = np.cov(notas.T)
    print("\nMatriz de covariância:")
    print(cov_matrix)
    
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    
    print(f"\nAutovalores: {eigenvalues}")
    print("Autovetores:")
    print(eigenvectors)
    
    return cov_matrix, eigenvalues, eigenvectors

def exemplo_numeros_aleatorios():
    print("\n🎲 EXEMPLO COM NÚMEROS ALEATÓRIOS")
    print("=" * 40)
    
    np.random.seed(42)
    
    n_alunos = 10000
    
    media_linguagens = 520
    desvio_linguagens = 90
    
    media_humanas = 540
    desvio_humanas = 95
    
    media_natureza = 490
    desvio_natureza = 100
    
    media_matematica = 520
    desvio_matematica = 110
    
    media_redacao = 580
    desvio_redacao = 120
    
    linguagens = np.random.normal(media_linguagens, desvio_linguagens, n_alunos)
    humanas = np.random.normal(media_humanas, desvio_humanas, n_alunos)
    natureza = np.random.normal(media_natureza, desvio_natureza, n_alunos)
    matematica = np.random.normal(media_matematica, desvio_matematica, n_alunos)
    redacao = np.random.normal(media_redacao, desvio_redacao, n_alunos)
    
    linguagens = np.clip(linguagens, 0, 1000)
    humanas = np.clip(humanas, 0, 1000)
    natureza = np.clip(natureza, 0, 1000)
    matematica = np.clip(matematica, 0, 1000)
    redacao = np.clip(redacao, 0, 1000)
    
    notas_finais = (linguagens + humanas + natureza + matematica + redacao) / 5
    
    print(f"Notas simuladas para {n_alunos} alunos:")
    print(f"Linguagens: Média = {np.mean(linguagens):.1f}, Desvio = {np.std(linguagens):.1f}")
    print(f"Humanas: Média = {np.mean(humanas):.1f}, Desvio = {np.std(humanas):.1f}")
    print(f"Natureza: Média = {np.mean(natureza):.1f}, Desvio = {np.std(natureza):.1f}")
    print(f"Matemática: Média = {np.mean(matematica):.1f}, Desvio = {np.std(matematica):.1f}")
    print(f"Redação: Média = {np.mean(redacao):.1f}, Desvio = {np.std(redacao):.1f}")
    print(f"Nota Final: Média = {np.mean(notas_finais):.1f}, Desvio = {np.std(notas_finais):.1f}")
    
    todas_notas = np.vstack([linguagens, humanas, natureza, matematica, redacao]).T
    matriz_correlacao = np.corrcoef(todas_notas.T)
    
    print("\nMatriz de correlação entre as áreas:")
    areas = ['Linguagens', 'Humanas', 'Natureza', 'Matemática', 'Redação']
    for i, area1 in enumerate(areas):
        for j, area2 in enumerate(areas):
            if i < j:
                print(f"{area1} x {area2}: {matriz_correlacao[i,j]:.3f}")
    
    return todas_notas, notas_finais