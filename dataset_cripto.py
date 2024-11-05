import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output, State

# Carregar e preparar os dados
df = pd.read_excel("cryptos.xlsx")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Year'] = df['Date'].dt.year
df = df[(df['Year'] >= 2019) & (df['Year'] <= 2024)].dropna()
df['Month'] = df['Date'].dt.to_period('M').dt.end_time
df['Month'] = pd.to_datetime(df['Month'])


# Dicionário com informações das criptomoedas
cryptos = {
    'BTC-USD': {'name': 'Bitcoin', 'color': 'blue'},
    'BNB-USD': {'name': 'Binance Coin', 'color': 'orange'},
    'BCH-USD': {'name': 'Bitcoin Cash', 'color': 'cyan'},
    'DOGE-USD': {'name': 'Dogecoin', 'color': 'red'},
    'ETH-USD': {'name': 'Ethereum', 'color': 'gold'},
    'SOL-USD': {'name': 'Solana', 'color': 'lightgreen'},
    'USDT-USD': {'name': 'Tether', 'color': 'purple'},
    'XMR-USD': {'name': 'Monero', 'color': 'white'},
    'XRP-USD': {'name': 'Ripple', 'color': 'gray'},
}

# Layout do Dash
app = Dash(__name__)

drop_style = {
    'borderRadius': '15px',
    'height': '35px',
    'margin': '5px',
    'width': '250px',
    'display': 'inline-block',
    'textAlign': 'center',
    'fontSize': '20px',
    'color':'black'
}
style_layout = {
    'borderRadius': '10px',
    'margin': '0 0 15px 0',
    'width': '250px',
    'height': '35px',
    'fontSize': '22px',
    'textAlign': 'center',
    'color':'black'
    }

app.layout = html.Div(style={
    'backgroundColor': '#202630',
    'color':'#58ecba',
    'textAlign': 'center',
    'height': '140vh',
    'padding': '30px'
}, children=[
    html.H1('Dashboard de Criptomoedas', style={'textAlign': 'center', 'fontSize':'32px'}),
    html.H3('Período de 03/06/2019 até 01/06/2024', style={'textAlign': 'center', 'fontSize':'24px'}),
    html.Div('Selecione uma criptomoeda e o tipo de gráfico.', style={'textAlign': 'center', 'fontSize':'24px'}),

    dcc.Dropdown(
        id='crypto-dropdown',
        options=[{'label': 'Todas as Moedas', 'value': 'ALL'}] +
                [{'label': cryptos[coin]['name'], 'value': coin} for coin in cryptos],
        value='ALL',
        clearable=False,
        style=drop_style
    ),

    dcc.Dropdown(
        id='graph-dropdown',
        options=[
            {'label': 'Gráfico de Linha', 'value': 'line'},
            {'label': 'Gráfico de Barra', 'value': 'bar'},
            {'label': 'Gráfico de Boxplot', 'value': 'box'},
            {'label': 'Gráfico de Dispersão', 'value': 'scatter'},
            {'label': 'Gráfico de Linha PCT', 'value': 'line-pct'},
            {'label': 'Gráfico de Barra PCT', 'value': 'bar-pct'},
        ],
        value='line',
        clearable=False,
        style=drop_style
    ),

    dcc.Graph(id='crypto-graph', config={'displayModeBar': False}, style={'height': '75vh'}),

    # Inserindo dados na calculadora
    html.Div(style={
            'display':'flex',
            'flexDirection':'column',
            'alignItems':'center',
            'marginTop': '30px',
            'textAlign':'center'},
        children=[
        html.H1('Calculadora de Retorno de Investimento'),
        dcc.Dropdown(
            id='moeda-dropdown',
            options=[{'label': 'Selecione uma moeda', 'value':'None'}] +
                    [{'label': cryptos[coin]['name'], 'value': coin} for coin in cryptos],
            value='None',
            clearable=False,
            style=style_layout
        ),
        dcc.Dropdown(
            id='ano-dropdown',
            options=[{'label': 'Selecione um ano', 'value':'None'}] +
                    [{'label': str(year), 'value': year} for year in range(2019, 2025)],
            value='None',
            clearable=False,
            style=style_layout
        ),
        dcc.Input(id='investimento-input', type='number', placeholder='Valor investido', style=style_layout),
        html.Button('Calcular', id='calcular-button', n_clicks=0,style=style_layout),
        html.Div(id='resultado-retorno')
    ])
])

@app.callback(
    Output('crypto-graph', 'figure'),
    Input('crypto-dropdown', 'value'),
    Input('graph-dropdown', 'value'),

)
def update_graph(selected_crypto, graph_type):
    if selected_crypto is None:
        return px.bar(title="Nenhuma moeda selecionada.")
    # Filtrar dados
    if selected_crypto == 'ALL':
        data = df
    else:
        data = df[df['Crypto'] == selected_crypto]


    # Criar gráfico
    if graph_type == 'line':
        fig = px.line(data, x='Date', y='Adj Close', color='Crypto', color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'bar':
        data = data.groupby(['Year', 'Crypto'])['Adj Close'].mean().reset_index()
        fig = px.bar(data, x='Year', y='Adj Close', color='Crypto', barmode='group',
                        color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'box':
        fig = px.box(data, x='Crypto', y='Adj Close', color='Crypto', color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    elif graph_type == 'scatter':
        fig = px.scatter(data, x='Date', y='Adj Close', color='Crypto', color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})
    
    elif graph_type == 'line-pct':
        data = data.groupby(['Month','Crypto'])['Adj Close'].mean().reset_index()
        data['Percent'] = data.groupby('Crypto')['Adj Close'].pct_change() * 100
        fig = px.line(data, x='Month', y='Percent', color='Crypto', color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})
    
    elif graph_type == 'bar-pct':
        data = data.groupby(['Year','Crypto'])['Adj Close'].mean().reset_index()
        data['Percent'] = data.groupby('Crypto')['Adj Close'].pct_change() * 100
        fig = px.bar(data, x='Year', y='Percent', color='Crypto', barmode='group',
                        color_discrete_map={crypto: cryptos[crypto]['color'] for crypto in cryptos})

    # Atualizar layout do gráfico
    fig.update_layout(
        plot_bgcolor='#202630',
        paper_bgcolor='#272e40',
        font_color='#58ecba',
        title={
        'text': 'Preço de fechamento ajustado ao longo do tempo!',
        'font': {
            'size': 22,
        },
        'x': 0.5,
        },
        legend_title='Criptomoedas',
        legend=dict(
            itemsizing='constant',
            font=dict(
                size=16
            ),
        )
    )

    # Renomear legendas
    for trace in fig.data:
        trace.name = cryptos[trace.name]['name']

    return fig

# Callback para calcular o retorno do investimento
@app.callback(
    Output('resultado-retorno', 'children'),
    Input('calcular-button', 'n_clicks'),
    State('investimento-input', 'value'),
    State('moeda-dropdown', 'value'),
    State('ano-dropdown', 'value'),
)
def calcular_retorno(n_clicks, investimento, moeda_escolhida, ano_escolhido):
    if n_clicks > 0:
        if investimento is not None and moeda_escolhida is not None and ano_escolhido is not None:
            # Filtrando para obter o preço do primeiro dia do ano selecionado
            preco_compra = df[(df['Year'] == ano_escolhido) & (df['Crypto'] == moeda_escolhida) & (df['Date'] == df[df['Year'] == ano_escolhido]['Date'].min())]['Adj Close']

            # Obtendo o preço do último dia disponível
            preco_atual = df[df['Crypto'] == moeda_escolhida]['Adj Close'].iloc[-1]

            if not preco_compra.empty:
                preco_compra = preco_compra.iloc[0]
                quantidade_moeda = investimento / preco_compra
                valor_atual = quantidade_moeda * preco_atual
                retorno = valor_atual - investimento
                return html.Div(
                    f'Valor atual investido: US${valor_atual:.2f}, Lucro do investimento: US${retorno:.2f}',
                    style={'color': '#58ecba' if retorno > 0 else '#FF0000', 'fontSize': '24px'}
                )
            else:
                return html.Div(
                    "Preço de compra não disponível para a moeda e ano selecionados.",
                    style={'textAlign': 'center', 'padding':'10px', 'fontSize':'24px', 'fontWeight':'bold'}
                )
        else:
            return html.Div(
                "Por favor, preencha todos os campos.",
                style={'textAlign': 'center', 'padding':'10px', 'fontSize':'24px', 'fontWeight':'bold'}
            )


if __name__ == '__main__':
    app.run_server(port=8050, debug=True)
