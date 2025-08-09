import streamlit as st
import pandas as pd
import plotly.express as px

# Configuracao da pagina
# define o titulo da pagina, o icone e o layout para ocupar toda a largura da tela

st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📈",
    layout="wide"
)

# Carregamento dos dados
df = pd.read_csv("../imersao_dev_python/dados_imersao_final.csv")

# Barra lateral
st.sidebar.header("☰ Filtros")

# Filtro por ano
anos_disponiveis = sorted(df['ano'].unique()) #sorted organiza os anos em ordem crescente
anos_selecionados = st.sidebar.multiselect( #multiselect permite selecionar múltiplas opções
    "ano",
    options=anos_disponiveis,
    default=anos_disponiveis
)

# Filtro por senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionados = st.sidebar.multiselect(
    "Senioridade",
    options=senioridades_disponiveis,
    default=senioridades_disponiveis
)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect(
    "Contrato",
    options=contratos_disponiveis,
    default=contratos_disponiveis
)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect(
    "Tamanho da Empresa",
    options=tamanhos_disponiveis,
    default=tamanhos_disponiveis
)

# Filtragem do DataFrame
# o dataframe df é filtrado com base nos filtros selecionados na barra lateral

df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) & #isin verifica se o valor de cada coluna está na lista filtrada
    (df['senioridade'].isin(senioridades_selecionados)) & #& é o operador "E" para combinar múltiplas condições
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# Conteúdo principal
st.title("📈 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos ultimos anos. Utilize os filtros na barra lateral para refinar sua análise.") #markdown permite formatar o texto com markdown

# Metricas principais
st.subheader("📊 Métricas Gerais (Salário anual em USD)")

if not df_filtrado.empty:  # Verifica se o DataFrame filtrado não está vazio
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]  # shape retorna uma tupla (linhas, colunas), pegamos o número de linhas
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]  # mode retorna a moda, pegamos o primeiro valor
else:
    salario_medio = 0
    salario_maximo = 0
    total_registros = 0
    cargo_mais_frequente = "N/A"

col1, col2, col3, col4 = st.columns(4)  # Cria 4 colunas para exibir as métricas
col1.metric("Salário Médio", f"${salario_medio:,.0f}") # ,.0f formata o número para exibir sem casas decimais e com separador de milhar
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}") # ${} formata o número como moeda
col3.metric("Total de Registros", f"{total_registros}")
col4.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")  # Linha horizontal para separar seções

# Analises Visuais com Plotly
st.subheader("📉 Gráficos")

col_graf1, col_graf2 = st.columns(2)  # Cria 2 colunas para os gráficos
with col_graf1: #with define o contexto para adicionar elementos na coluna
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()  # Top 10 cargos por salário médio
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h', # orientation='h' cria um gráfico de barras horizontal
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
            title='Top 10 Cargos por Salário Médio'
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})  # Alinha o título à esquerda e ordena o eixo y
        st.plotly_chart(grafico_cargos, use_container_width=True) # use_container_width faz o gráfico ocupar toda a largura da coluna
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")
    
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,  # Número de bins no histograma
            labels={'usd': 'Salário Anual (USD)', 'contagem': ''},
            title='Distribuição Salarial Anual'
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

col_graf3, col_graf4 = st.columns(2)  # Cria mais 2 colunas para os gráficos
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index() # reset_index transforma o Series em DataFrame
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']  # Renomeia as colunas
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Distribuição de Trabalho Remoto',
            hole=0.5  # Cria um gráfico de pizza com buraco no meio (donut chart)
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist'] 
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='Viridis', # Escala de cores Viridis para melhor visualização
            title='Salário médio de Cientista de Dados por País',
            labels={'usd': 'Salário Médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para os filtros selecionados.")

# tabela de dados detalhados
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado.reset_index(drop=True))  # reset_index(drop=True) reseta o índice do DataFrame para exibição limpa