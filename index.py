import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash_bootstrap_templates import ThemeSwitchAIO
import plotly.graph_objects as go
import json
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar variáveis globais
df = None
data_loaded = False
cobs = None

# Função para calcular o total de viaturas únicas em cada linha
def calcular_total_vtr(linha):
    return len(set(linha.split(' / ')))

# Função para carregar e processar os dados da API
# Função para carregar e processar os dados da API
def load_data(force_reload=False):
    global df, cobs, data_loaded

    # Se `force_reload=True`, força a atualização dos dados
    if force_reload or not data_loaded:
        url = os.environ.get("URL_API")
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        response = requests.get(url, headers=headers)

        df = pd.DataFrame(response.json())

        # Converter colunas com valores repetidos para category
        categorical_columns = ["Natureza", "Prioridade", "tipo_classificacao", "COB", "UNIDADE", "municipio"]
        for col in categorical_columns:
            df[col] = df[col].astype("category")

        # Converter latitude e longitude para float32
        df["latitude"] = df["latitude"].astype("float32")
        df["longitude"] = df["longitude"].astype("float32")

        # Converter a coluna data para datetime
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")

        # Mapear COBs e Prioridades
        cob_legend = {
            '1COB': '1ºCOB - RMBH/Divinóplis',
            '2COB': '2ºCOB - Uberlândia',
            '3COB': '3ºCOB - Juiz de Fora',
            '4COB': '4ºCOB - Montes Claros',
            '5COB': '5ºCOB - Governador Valadares',
            '6COB': '6ºCOB - Varginha'
        }
        df['COB_nome'] = df['COB'].map(cob_legend)

        priori_legend = {
            '1': 'Prioridade 1 - Alta',
            '2': 'Prioridade 2 - Média',
            '3': 'Prioridade 3 - Baixa'
        }
        df['Prioridade_nome'] = df['Prioridade'].map(priori_legend)

        # Criando a coluna 'total_vtr'
        df['total_vtr'] = df['recursos_empenhados'].apply(calcular_total_vtr)

        # Lista de Cobs Única e Ordenada
        cobs = sorted(df["COB_nome"].dropna().astype(str).unique())

        # Atualizar estado
        data_loaded = True


load_data()

# Configurar valores iniciais e finais para o filtro de data
data_min = df["data"].min().date()
data_max = df["data"].max().date()

# Configuração do Dash (Stylesheet e título) ==========================
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.VAPOR, dbc.themes.FLATLY],
)
app.title = "Dashboard de Ocorrências - CBMMG"
template_theme1 = "vapor"
template_theme2 = "flatly"
url_theme1 = dbc.themes.VAPOR
url_theme2 = dbc.themes.FLATLY


# Layout do Dashboard ================================================
app.layout = dbc.Container([

    # Linha com imagem, título e filtros
    # Row 1
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src="/assets/bombeiro.png", style={'width': '60px', 'height': '60px'}),
                html.H2("Painel CAD Período Chuvoso", className="text-center", style={'font-weight': 'bold', 'font-size': '1.3rem'}),
                ThemeSwitchAIO(aio_id="theme", themes=[url_theme2, url_theme1]),
            ], className="text-center"),
        ], md=4),

        dbc.Col([
            html.Label("Filtrar por Data:", style={'font-weight': 'bold', 'display': 'block'}),
            dcc.DatePickerRange(
                id="date-filter",
                start_date=data_min,
                end_date=data_max,
                display_format="DD/MM/YYYY",
                start_date_placeholder_text="Data inicial",
                end_date_placeholder_text="Data final",
            )
        ], md=4),

        dbc.Col([
            html.Label("Filtrar por COB:", style={'font-weight': 'bold', 'display': 'block'}),
            dcc.Dropdown(
                id="cob-filter",
                options=[{"label": cob, "value": cob} for cob in cobs],
                value=None,
                multi=True,
                placeholder="Selecione o COB",
            )
        ], md=4),
    ], className="align-items-center my-4"),

    # Primeira linha de indicadores
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="indc_1", style={'height': '150px'})
        ], md=3),
        dbc.Col([
            dcc.Graph(id="indc_2", style={'height': '150px'})
        ], md=3),
        dbc.Col([
            dcc.Graph(id="indc_3", style={'height': '150px'})
        ], md=3),
        dbc.Col([
            dcc.Graph(id="indc_7", style={'height': '150px'})
        ], md=3),
    ], className="mb-2"),
    
    # Segunda linha de indicadores
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="indc_5", style={'height': '150px'})
        ], md=3),
        dbc.Col([
            dcc.Graph(id="indc_4", style={'height': '150px'})
        ], md=3),
        dbc.Col([
            dcc.Graph(id="indc_6", style={'height': '150px'})
        ], md=3),
        dbc.Col([
            dcc.Graph(id="indc_8", style={'height': '150px'})
        ], md=3),
    ], className="mb-4"),

    # Gráfico
    # Row 2
    dbc.Row([
        dbc.Col([
            dbc.CardBody([
            dcc.Graph(id="cob_pri", config={"displayModeBar": False})
                    ]),
        ]),
        dbc.Col([
            dbc.CardBody([
            dcc.Graph(id="pri_pie", config={"displayModeBar": False})
                    ]),
        ]),

    ], className="align-items-center mb-4"),

    # Row 3
    dbc.Row([
        dbc.Col([
            dbc.CardBody([
            dcc.Graph(id="cob_nat", config={"displayModeBar": False})
                    ]),
        ]),

    ], className="align-items-center mb-4"),

    # Mapas de Prioridades e Recursos =================================
    # dbc.Row([
    #     dbc.Col([
    #         html.Div([
    #             html.H2("Mapa de Prioridades", className="text-center", style={'font-weight': 'bold'}),
    #             dcc.Graph(
    #                 id="map_priorities",
    #                 config={"scrollZoom": True}
    #             )
    #         ])
    #     ])
    # ]),
    dcc.Interval(id="interval-update", interval=60*1000, n_intervals=0) # Atualizar a cada 1 min
], fluid=True)

# Callbacks =========================================================
@app.callback(
    Output("indc_1", "figure"),
    Output("indc_2", "figure"),
    Output("indc_3", "figure"),
    Output("indc_4", "figure"),
    Output("indc_5", "figure"),
    Output("indc_6", "figure"),
    Output("indc_7", "figure"),
    Output("indc_8", "figure"),
    Output("cob_pri", "figure"),
    Output("pri_pie", "figure"),
    Output("cob_nat", "figure"),
    #Output("map_priorities", "figure"),
    Input("date-filter", "start_date"),
    Input("date-filter", "end_date"),
    Input("cob-filter", "value"),
    Input("interval-update", "n_intervals"),
    Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def line_graph_1(start_date, end_date, cobs, n_intervals,toggle):

    print(f"🔄 Atualizando dados... Intervalo: {n_intervals}")

    # Agora os dados sempre serão recarregados corretamente
    load_data(True)

    # Criar uma cópia profunda para evitar modificações na variável global
    df_filtered = df.copy(deep=True)

    # Filtro de data
    if start_date and end_date:
        mask = (df_filtered["data"] >= start_date) & (df_filtered["data"] <= end_date)
        df_filtered = df_filtered.loc[mask]

    # Recriar a coluna 'COB_nome' se necessário
    if 'COB_nome' not in df_filtered.columns:
        df_filtered['COB_nome'] = df_filtered['COB'].map({
            '1COB': '1ºCOB - RMBH/Divinóplis',
            '2COB': '2ºCOB - Uberlândia',
            '3COB': '3ºCOB - Juiz de Fora',
            '4COB': '4ºCOB - Montes Claros',
            '5COB': '5ºCOB - Governador Valadares',
            '6COB': '6ºCOB - Varginha'
        })

    # Filtro de COBs
    if cobs:
        df_filtered = df_filtered[df_filtered["COB_nome"].isin(cobs)]

    # Verificar novamente a presença de 'COB_nome'
    if 'COB_nome' not in df_filtered.columns:
        return [go.Figure().update_layout(title="Erro: Coluna 'COB_nome' não encontrada.")] * 12



    # Copia profunda do Dataframe
    df_filtered = df.copy(deep=True)
    mask = (df_filtered["data"] >= start_date) & (df_filtered["data"] <= end_date)
    df_filtered = df_filtered.loc[mask]

    template = template_theme1 if toggle else template_theme2


    if cobs:
        df_filtered = df_filtered[df_filtered["COB_nome"].isin(cobs)]

    # Layout do Indicadores ================================================
    # ===== Preparação dos dados para indicadores =====
    # Filtrar ocorrências de prioridade 1 e agrupar por COB
    prioridade_alta = df_filtered[df_filtered["Prioridade"] == "1"].groupby("COB_nome", observed=True).size().reset_index(name="Quantidade")

    # Verificar se existe pelo menos um valor maior que 0
    if not prioridade_alta.empty and prioridade_alta["Quantidade"].sum() > 0:
        top_cob_prioridade_alta = prioridade_alta.loc[prioridade_alta["Quantidade"].idxmax()]
        top_cob_nome = top_cob_prioridade_alta["COB_nome"]
        top_cob_quantidade = top_cob_prioridade_alta["Quantidade"]
        media_prioridade_alta = prioridade_alta["Quantidade"].mean()
    else:
        top_cob_nome = "—"  # Se não houver registros válidos, exibe "-"
        top_cob_quantidade = 0
        media_prioridade_alta = 0

    # Município com maior frequência de ocorrências
    municipios_frequencia = df_filtered.groupby("municipio", observed=True).size().reset_index(name="Frequencia")
    top_municipio = municipios_frequencia.loc[municipios_frequencia["Frequencia"].idxmax()]
    media_frequencia_municipio = municipios_frequencia["Frequencia"].mean()

    # Unidade com maior número de ocorrências
    unidades_ocorrencias = df_filtered.groupby("UNIDADE", observed=True).size().reset_index(name="Quantidade")
    top_unidade = unidades_ocorrencias.loc[unidades_ocorrencias["Quantidade"].idxmax()]
    media_unidade = unidades_ocorrencias["Quantidade"].mean()

    # Unidade com maior número de ocorrências Prioridade 1 - Alta
    # Filtrar ocorrências de prioridade 1 e agrupar por Unidade
    unidade_prioridade_alta = df_filtered[df_filtered["Prioridade"] == "1"].groupby("UNIDADE", observed=True).size().reset_index(name="Quantidade")

    # Verificar se existe pelo menos um valor maior que 0
    if not unidade_prioridade_alta.empty and unidade_prioridade_alta["Quantidade"].sum() > 0:
        top_unidade_prioridade_alta = unidade_prioridade_alta.loc[unidade_prioridade_alta["Quantidade"].idxmax()]
        top_unidade_nome = top_unidade_prioridade_alta["UNIDADE"]
        top_unidade_quantidade = top_unidade_prioridade_alta["Quantidade"]
        media_unidade_prioridade_alta = unidade_prioridade_alta["Quantidade"].mean()
    else:
        top_unidade_nome = "—"  # Se não houver registros válidos, exibe "-"
        top_unidade_quantidade = 0
        media_unidade_prioridade_alta = 0

    # Unidade com maior número de recursos empenhados
    recursos_empenhados = df_filtered.groupby("UNIDADE", observed=True)["total_vtr"].sum().reset_index(name="TotalRecursos")
    top_recursos = recursos_empenhados.loc[recursos_empenhados["TotalRecursos"].idxmax()]
    media_recursos = recursos_empenhados["TotalRecursos"].mean()

    # Expandir os recursos empenhados em coordenadas separadas
    recursos = []
    for _, row in df.iterrows():
        for recurso in row["recursos_empenhados"].split(" / "):
            recursos.append({
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "recurso": recurso,
                "local": row["local_fato"]
            })
    df_recursos = pd.DataFrame(recursos)
    # ===== Graficos =====

    # Conjunto de todas as viaturas únicas
    total_viaturas = set()
    df_filtered['recursos_empenhados'].str.split(' / ').apply(total_viaturas.update)

    # Total de recursos existentes
    total_recursos_unicos = len(total_viaturas)

    # Total de Ocorrencias existentes
    total_ocorrencias = len(df_filtered)

    # ===== Indicadores =====

    # Criar indicador
    fig1 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{top_cob_nome} - Top COB</span><br>"
                    f"<span style='font-size:90%'>Maior Prioridade 1 - Alta</span>"
        },
        value=top_cob_quantidade,
        number={'suffix': " ocorrências", 'font': {'size': 40}},
        delta={'relative': True, 'valueformat': '.1%', 'reference': media_prioridade_alta, 'position': "bottom", 'font': {'size': 30}}
    ))
    fig1.update_layout(template=template)

    # Indicator 2: Município com maior frequência de ocorrências
    fig2 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{top_municipio['municipio']} - Top Município</span><br>"
                    f"<span style='font-size:90%'>Mais frequente</span>"
        },
        value=top_municipio["Frequencia"],
        number={'suffix': " ocorrências", 'font': {'size': 40}},
        delta={'relative': True, 'valueformat': '.1%', 'reference': media_frequencia_municipio, 'position': "bottom", 'font': {'size': 30}}
    ))
    fig2.update_layout(template=template)

    # Indicator 3: Unidade com maior número de ocorrências
    fig3 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{top_unidade['UNIDADE']} - Top Unidade</span><br>"
                    f"<span style='font-size:90%'>Mais Ocorrências</span>"
        },
        value=top_unidade["Quantidade"],
        number={'suffix': " ocorrências", 'font': {'size': 40}},
        delta={'relative': True, 'valueformat': '.1%', 'reference': media_unidade, 'position': "bottom", 'font': {'size': 30}}
    ))
    fig3.update_layout(template=template)

    # Indicator 4: Unidade com maior número de ocorrências Prioridade 1 - Alta
    # Criar indicador
    fig4 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{top_unidade_nome} - Top Unidade</span><br>"
                    f"<span style='font-size:90%'>Maior Prioridade 1 - Alta</span>"
        },
        value=top_unidade_quantidade,
        number={'suffix': " ocorrências", 'font': {'size': 40}},
        delta={'relative': True, 'valueformat': '.1%', 'reference': media_unidade_prioridade_alta, 'position': "bottom", 'font': {'size': 30}}
    ))
    fig4.update_layout(template=template)

    # Indicator 5: Unidade com maior número de recursos empenhados
    fig5 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{top_recursos['UNIDADE']} - Top Unidade</span><br>"
                    f"<span style='font-size:90%'>Mais Recursos Empenhados</span>"
        },
        value=top_recursos["TotalRecursos"],
        number={'suffix': " recursos", 'font': {'size': 40}},
        delta={'relative': True, 'valueformat': '.1%', 'reference': media_recursos, 'position': "bottom", 'font': {'size': 30}}
    ))
    fig5.update_layout(template=template)

    # Indicator 6: Total de recursos existentes
    # Natureza de Ocorrência que Mais Aparece
    natureza_freq = df_filtered.groupby("Natureza", observed=True).size().reset_index(name="Frequencia")
    top_natureza = natureza_freq.loc[natureza_freq["Frequencia"].idxmax()]
    media_natureza = natureza_freq["Frequencia"].mean()

    fig6 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>{top_natureza['Natureza']} - Top Natureza</span><br>"
                    f"<span style='font-size:90%'>Natureza mais comum</span>"
        },
        value=top_natureza["Frequencia"],
        number={'suffix': " ocorrências", 'font': {'size': 40}},
        delta={'relative': True, 'valueformat': '.1%', 'reference': media_natureza, 'position': "bottom", 'font': {'size': 30}}
    ))
    fig6.update_layout(template=template)

    # FILE EDIT =============================================================

        # Indicator 5: Unidade com maior número de recursos empenhados
    fig7 = go.Figure(go.Indicator(
        mode='number+delta',
        title={
            "text": f"<span>Total de Ocorrências Existentes</span>"
        },
        value=total_ocorrencias,
        number={'suffix': " ocorrências", 'font': {'size': 40}},
    ))
    fig7.update_layout(template=template)

    # Indicator 6: Total de recursos existentes
    fig8 = go.Figure(go.Indicator(
        mode='number',
        title={
            "text": "<span>Total de Recursos Existentes</span><br>"
        },
        value=total_recursos_unicos,
        number={'suffix': " viaturas", 'font': {'size': 40}}
    ))
    fig8.update_layout(template=template)

    # FILE EDIT =============================================================

    # Criação do Gráfico quantidaede de chamadas por COB e Prioridade
    prioridade_por_cob = df_filtered.groupby(['COB_nome', 'Prioridade_nome'], observed=True).size().reset_index(name='Quantidade')
    fig9 = px.bar(prioridade_por_cob, x='COB_nome', y='Quantidade', color='Prioridade_nome',
                    title='Quantidade de Chamadas por Prioridade em cada COB',
                    labels={'Quantidade': 'Número de Chamadas', 'COB_nome': 'COBs', 'Prioridade_nome': 'Prioridades'},
                        color_discrete_sequence=['#636EFA', '#FF0000', '#00CC96'])
    fig9.update_layout(
        legend_title_text='Prioridades', legend=dict(traceorder='normal'), template=template)
    

    # Criação de Gráfico de Pizza de Tipo de Prioridade pelo total de ocorrencias
    # Gráfico de pizza por Prioridade
    prioridade_total = df_filtered.groupby('Prioridade_nome', observed=True).size().reset_index(name='Quantidade')
    fig10 = px.pie(
        prioridade_total, values='Quantidade', names='Prioridade_nome',
        title='Proporção de Registros por Prioridade',
        color_discrete_sequence=['#636EFA', '#FF0000', '#00CC96']
    )
    fig10.update_layout(template=template)
    
    # Criação do Gráfico quantidaede de chamadas por COB e Natureza
    cob_por_natureza = df_filtered.groupby(['Natureza', 'COB_nome'], observed=True).size().reset_index(name='Quantidade')
    fig11 = px.bar(cob_por_natureza, x='Natureza', y='Quantidade', color='COB_nome',
                    title='Quantidade de Chamadas por Natureza em cada COB',
                    labels={'Quantidade': 'Número de Chamadas', 'Natureza': 'Naturezas', 'COB_nome': 'COBs'},
                        color_discrete_sequence=px.colors.qualitative.T10, template=template)
    
    fig11.update_layout(
    height=600,  # Aumente a altura do gráfico
    legend_title_text='COBs',
    legend=dict(
        traceorder='normal',
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="right",
        x=1.3
    ),
    template=template
    )
        

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11 

# Rodar o servidor ================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run_server(host='0.0.0.0', port=port)
else:
    server = app.server
    print(f"Server callable: {server}")