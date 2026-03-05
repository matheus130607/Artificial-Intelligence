import pandas as pd

#Crie um dicionario com os dados de alunos
dados = {
    "Nome":["Ana", "Bruno", "Carlos", "Diana"],
    "Idade":[20, 22, 19, 21],
    "Nota":[8.5, 7.0, 9.0, 8.0]
}

#Crie DataFrame
df = pd.DataFrame(dados)
print(df)

#Calcule estatísticas
print("\nEstatísticas da Nota"),
print(df["Nota"]. describe())