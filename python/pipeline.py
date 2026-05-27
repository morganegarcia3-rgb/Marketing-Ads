import pandas as pd
import mysql.connector
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

# Chargement des variables d'environnement
load_dotenv()

# ─── 1. CONNEXION À LA BASE ───────────────────────────────────────────────────

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ─── 2. CHARGEMENT DES DONNÉES ────────────────────────────────────────────────

def load_data(conn):
    query = """
        SELECT
            c.id AS campagne_id,
            cl.nom AS client,
            c.plateforme,
            c.objectif,
            SUM(p.impressions) AS impressions,
            SUM(p.clics) AS clics,
            SUM(p.spend) AS spend,
            SUM(p.conversions) AS conversions
        FROM campagnes c
        JOIN clients cl ON cl.id = c.client_id
        JOIN performances p ON p.campagne_id = c.id
        GROUP BY c.id, cl.nom, c.plateforme, c.objectif
    """
    return pd.read_sql(query, conn)

# ─── 3. APPEL API EXTERNE (taux de change EUR/USD) ────────────────────────────

def get_eur_usd_rate():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/EUR", timeout=5)
        data = response.json()
        return data["rates"]["USD"]
    except:
        return 1.08  # valeur de fallback

# ─── 4. ALGORITHME DE SCORING ─────────────────────────────────────────────────

def calculer_score(df, taux_usd):
    """
    Score de performance pondéré sur 100 :
    - CTR     (30%) : clics / impressions
    - CPC     (25%) : spend / clics (inversé, plus bas = mieux)
    - ROAS    (30%) : conversions * 50 / spend (valeur estimée par conversion)
    - Volume  (15%) : impressions normalisées
    """
    df = df.copy()

    # Calcul des métriques
    df["ctr"]  = df["clics"] / df["impressions"].replace(0, 1)
    df["cpc"]  = df["spend"] / df["clics"].replace(0, 1)
    df["roas"] = (df["conversions"] * 50) / df["spend"].replace(0, 1)
    df["spend_usd"] = df["spend"] * taux_usd

    # Normalisation min-max (0 à 1)
    def norm(serie):
        mn, mx = serie.min(), serie.max()
        if mx == mn:
            return serie * 0
        return (serie - mn) / (mx - mn)

    df["score_ctr"]    = norm(df["ctr"])    * 30
    df["score_cpc"]    = norm(1 / df["cpc"].replace(0, 1)) * 25  # inversé
    df["score_roas"]   = norm(df["roas"])   * 30
    df["score_volume"] = norm(df["impressions"]) * 15

    df["score_performance"] = (
        df["score_ctr"] + df["score_cpc"] + df["score_roas"] + df["score_volume"]
    ).round(2)

    # Segmentation
    df["segment"] = pd.cut(
        df["score_performance"],
        bins=[0, 33, 66, 100],
        labels=["Low", "Mid", "Top"],
        include_lowest=True
    )

    return df

# ─── 5. ÉCRITURE DES RÉSULTATS EN BASE ───────────────────────────────────────

def save_scores(conn, df):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scores_campagnes")  # reset avant réinsertion

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO scores_campagnes
                (campagne_id, score_performance, segment, ctr, cpc, roas, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            int(row["campagne_id"]),
            float(row["score_performance"]),
            str(row["segment"]),
            float(row["ctr"]),
            float(row["cpc"]),
            float(row["roas"]),
            now
        ))

    conn.commit()
    cursor.close()
    print(f"✅ {len(df)} scores enregistrés en base.")

# ─── 6. MAIN ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    conn = get_connection()
    print("✅ Connexion MySQL OK")

    df = load_data(conn)
    print(f"✅ {len(df)} campagnes chargées")

    taux = get_eur_usd_rate()
    print(f"✅ Taux EUR/USD récupéré : {taux}")

    df_scored = calculer_score(df, taux)
    print(df_scored[["client", "plateforme", "score_performance", "segment"]].to_string())

    save_scores(conn, df_scored)
    conn.close()