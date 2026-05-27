import pandas as pd
import mysql.connector
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from dotenv import load_dotenv
import os

load_dotenv()

# ─── CONNEXION ────────────────────────────────────────────────────────────────

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ─── CHARGEMENT DES DONNÉES ───────────────────────────────────────────────────

conn = get_connection()

df = pd.read_sql("""
    SELECT
        cl.nom AS client,
        c.plateforme,
        c.objectif,
        c.statut,
        s.score_performance,
        s.segment,
        s.ctr,
        s.cpc,
        s.roas,
        SUM(p.impressions) AS impressions,
        SUM(p.clics) AS clics,
        SUM(p.spend) AS spend,
        SUM(p.conversions) AS conversions
    FROM scores_campagnes s
    JOIN campagnes c ON c.id = s.campagne_id
    JOIN clients cl ON cl.id = c.client_id
    JOIN performances p ON p.campagne_id = c.id
    GROUP BY cl.nom, c.plateforme, c.objectif, c.statut,
             s.score_performance, s.segment, s.ctr, s.cpc, s.roas
""", conn)
conn.close()

# ─── APP DASH ─────────────────────────────────────────────────────────────────

app = Dash(__name__)

clients = ["Tous"] + sorted(df["client"].unique().tolist())
plateformes = ["Toutes"] + sorted(df["plateforme"].unique().tolist())

app.layout = html.Div([

    html.H1("Dashboard Performance Pub", style={"textAlign": "center", "fontFamily": "Arial"}),

    # Filtres
    html.Div([
        html.Div([
            html.Label("Client"),
            dcc.Dropdown(clients, "Tous", id="filtre-client", clearable=False)
        ], style={"width": "30%", "display": "inline-block", "marginRight": "2%"}),

        html.Div([
            html.Label("Plateforme"),
            dcc.Dropdown(plateformes, "Toutes", id="filtre-plateforme", clearable=False)
        ], style={"width": "30%", "display": "inline-block"}),
    ], style={"padding": "20px"}),

    # KPIs
    html.Div(id="kpis", style={"display": "flex", "gap": "20px", "padding": "0 20px 20px"}),

    # Graphiques
    html.Div([
        dcc.Graph(id="graph-score"),
        dcc.Graph(id="graph-spend"),
        dcc.Graph(id="graph-segment"),
    ])

], style={"fontFamily": "Arial", "maxWidth": "1200px", "margin": "0 auto"})

# ─── CALLBACK ─────────────────────────────────────────────────────────────────

@app.callback(
    Output("kpis", "children"),
    Output("graph-score", "figure"),
    Output("graph-spend", "figure"),
    Output("graph-segment", "figure"),
    Input("filtre-client", "value"),
    Input("filtre-plateforme", "value")
)
def update(client, plateforme):
    dff = df.copy()
    if client != "Tous":
        dff = dff[dff["client"] == client]
    if plateforme != "Toutes":
        dff = dff[dff["plateforme"] == plateforme]

    # KPIs
    total_spend  = f"{dff['spend'].sum():,.0f} €"
    total_conv   = f"{int(dff['conversions'].sum())}"
    score_moyen  = f"{dff['score_performance'].mean():.1f} / 100"

    kpis = [
        kpi_card("Budget dépensé", total_spend, "#4A90D9"),
        kpi_card("Conversions totales", total_conv, "#27AE60"),
        kpi_card("Score moyen", score_moyen, "#E67E22"),
    ]

    # Graph 1 — Score par campagne
    fig1 = px.bar(
        dff.sort_values("score_performance", ascending=True),
        x="score_performance", y="client", color="plateforme",
        orientation="h", title="Score de performance par client",
        labels={"score_performance": "Score", "client": "Client"}
    )

    # Graph 2 — Spend par plateforme
    fig2 = px.pie(
        dff, values="spend", names="plateforme",
        title="Répartition du budget par plateforme"
    )

    # Graph 3 — Segments
    seg_counts = dff["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]
    fig3 = px.bar(
        seg_counts, x="segment", y="count",
        color="segment", title="Répartition des segments (Top / Mid / Low)",
        color_discrete_map={"Top": "#27AE60", "Mid": "#E67E22", "Low": "#E74C3C"}
    )

    return kpis, fig1, fig2, fig3

def kpi_card(titre, valeur, couleur):
    return html.Div([
        html.P(titre, style={"margin": "0", "fontSize": "13px", "color": "#666"}),
        html.H3(valeur, style={"margin": "4px 0 0", "color": couleur})
    ], style={
        "background": "#f9f9f9", "border": f"1px solid {couleur}",
        "borderRadius": "8px", "padding": "16px", "flex": "1",
        "textAlign": "center"
    })

# ─── LANCEMENT ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)