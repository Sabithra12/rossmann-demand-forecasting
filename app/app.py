"""Rossmann demand forecast + reorder recommendation (Flask).

Needs these files in the SAME folder as app.py:
    model.txt, history.csv, store_info.csv, safety.csv
Run:  python app.py   then open http://127.0.0.1:5000
"""
import os

import lightgbm as lgb
import numpy as np
import pandas as pd
from flask import Flask, render_template_string, request

BASE = os.path.dirname(os.path.abspath(__file__))

model = lgb.Booster(model_file=os.path.join(BASE, "model.txt"))
hist = pd.read_csv(os.path.join(BASE, "history.csv"), parse_dates=["date"])
info = pd.read_csv(os.path.join(BASE, "store_info.csv")).set_index("store")
safety = pd.read_csv(os.path.join(BASE, "safety.csv")).set_index("store")["safety_stock"]

LAST_DATE = hist["date"].max()
HORIZON = 7  # days; matches the 7-day lead-time assumption and lag_7 minimum

FEATURES = [
    "store", "day_of_week", "promo", "state_holiday", "school_holiday",
    "store_type", "assortment", "competition_distance", "promo2",
    "year", "month", "day", "week",
    "lag_7", "lag_14", "lag_21", "lag_28", "roll_mean_4w",
]
TYPE_LABEL = {0: "a", 1: "b", 2: "c", 3: "d"}
PROMO_MODES = {
    "none": "No promotion",
    "weekdays": "Promotion Monday to Friday",
    "all": "Promotion on all 7 days",
}

app = Flask(__name__)


def forecast(store, promo_mode):
    """Forecast the next 7 days for one store. Returns a DataFrame."""
    sales = hist[hist["store"] == store].set_index("date")["sales"]
    row_info = info.loc[store]
    rows = []
    for i in range(1, HORIZON + 1):
        d = LAST_DATE + pd.Timedelta(days=i)
        dow = d.weekday() + 1  # 1 = Monday ... 7 = Sunday
        lags = [sales.get(d - pd.Timedelta(days=k), np.nan) for k in (7, 14, 21, 28)]
        if promo_mode == "all":
            promo = 1
        elif promo_mode == "weekdays":
            promo = 1 if dow <= 5 else 0
        else:
            promo = 0
        rows.append({
            "store": store,
            "day_of_week": dow,
            "promo": promo,
            "state_holiday": 0,    # assumption: no state holiday
            "school_holiday": 0,   # assumption: no school holiday
            "store_type": row_info["store_type"],
            "assortment": row_info["assortment"],
            "competition_distance": row_info["competition_distance"],
            "promo2": row_info["promo2"],
            "year": d.year,
            "month": d.month,
            "day": d.day,
            "week": int(d.isocalendar()[1]),
            "lag_7": lags[0],
            "lag_14": lags[1],
            "lag_21": lags[2],
            "lag_28": lags[3],
            "roll_mean_4w": pd.Series(lags).mean(),  # skips missing values
            "_date": d,
        })
    frame = pd.DataFrame(rows)
    pred = np.expm1(model.predict(frame[FEATURES]))  # model was trained on log1p(sales)
    pred = np.clip(pred, 0, None)
    # Most stores are closed on Sundays: forecast 0 for them.
    closed = (frame["day_of_week"] == 7) & (int(row_info["opens_sunday"]) == 0)
    pred[closed.values] = 0
    return pd.DataFrame({
        "date": frame["_date"],
        "day": frame["_date"].dt.strftime("%a"),
        "promo": frame["promo"],
        "closed": closed.values,
        "forecast": pred,
    })


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Store Demand Forecast</title>
<style>
  body { font-family: Segoe UI, Arial, sans-serif; background:#f4f6f9; margin:0; color:#1b2a3a; }
  .wrap { max-width: 860px; margin: 28px auto; padding: 0 16px; }
  h1 { color:#14325c; margin-bottom:4px; }
  .sub { color:#556; margin-bottom:20px; }
  .card { background:#fff; border-radius:10px; padding:18px; box-shadow:0 1px 4px rgba(0,0,0,.08); margin-bottom:16px; }
  label { display:block; font-weight:600; margin:8px 0 4px; }
  select, button { padding:9px 12px; font-size:15px; border-radius:6px; border:1px solid #bcc6d3; }
  button { background:#14325c; color:#fff; border:none; cursor:pointer; margin-top:12px; }
  .row { display:flex; gap:12px; flex-wrap:wrap; }
  .row > div { flex:1; min-width:150px; }
  .kpi { text-align:center; padding:12px; background:#eef2f8; border-radius:8px; }
  .kpi .v { font-size:24px; font-weight:700; color:#14325c; }
  .kpi .l { font-size:12px; color:#556; }
  table { width:100%; border-collapse:collapse; margin-top:8px; }
  th, td { padding:8px; border-bottom:1px solid #e3e8ef; text-align:right; }
  th:first-child, td:first-child { text-align:left; }
  th { background:#eef2f8; }
  .note { font-size:12.5px; color:#556; line-height:1.5; }
  .closed { color:#999; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Store Demand Forecast</h1>
  <div class="sub">Next 7 days after {{ last_date }} &middot; values are sales in &euro; (not units)</div>

  <div class="card">
    <form method="post">
      <div class="row">
        <div>
          <label for="store">Store</label>
          <select name="store" id="store">
            {% for s in stores %}<option value="{{ s }}" {% if s == sel_store %}selected{% endif %}>Store {{ s }}</option>{% endfor %}
          </select>
        </div>
        <div>
          <label for="promo">Promotion plan</label>
          <select name="promo" id="promo">
            {% for k, v in modes.items() %}<option value="{{ k }}" {% if k == sel_promo %}selected{% endif %}>{{ v }}</option>{% endfor %}
          </select>
        </div>
      </div>
      <button type="submit">Forecast</button>
    </form>
  </div>

  {% if res %}
  <div class="card">
    <b>Store {{ res.store }}</b> &middot; type {{ res.type }}{% if not res.opens_sunday %} &middot; closed on Sundays{% endif %}
    <div class="row" style="margin-top:12px">
      <div class="kpi"><div class="v">{{ res.total }}</div><div class="l">7-day forecast demand (&euro;)</div></div>
      <div class="kpi"><div class="v">{{ res.safety }}</div><div class="l">Safety stock (&euro;)</div></div>
      <div class="kpi"><div class="v">{{ res.reorder }}</div><div class="l">Reorder point (&euro;)</div></div>
      {% if res.uplift is not none %}
      <div class="kpi"><div class="v">{{ res.uplift }}</div><div class="l">Model lift vs no promotion</div></div>
      {% endif %}
    </div>
  </div>

  <div class="card">
    <table>
      <tr><th>Date</th><th>Day</th><th>Promo</th><th>Forecast (&euro;)</th></tr>
      {% for r in res.rows %}
      <tr class="{{ 'closed' if r.closed }}">
        <td>{{ r.date }}</td><td>{{ r.day }}</td><td>{{ 'Yes' if r.promo else 'No' }}</td>
        <td>{{ 'Closed' if r.closed else r.value }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>
  {% endif %}

  <div class="card note">
    <b>How it works.</b> A LightGBM model trained on about 8.4 lakh Rossmann store-days (Jan 2013 to Jul 2015)
    forecasts daily sales from the store's last 4 weeks of sales, promotion and calendar features.
    Reorder point = 7-day forecast demand + safety stock.<br>
    <b>Assumptions.</b> 7-day lead time, 95% service level, no state or school holidays, stores closed on Sundays
    unless they opened on Sundays in the data. Safety stock comes from forecast errors on a 6-week test window.
    The promotion lift is a model estimate, not a proven causal effect.
  </div>
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    stores = sorted(info.index.tolist())
    sel_store = 262 if 262 in info.index else stores[0]
    sel_promo = "none"
    res = None

    if request.method == "POST":
        try:
            candidate = int(request.form.get("store", sel_store))
            if candidate in info.index:
                sel_store = candidate
        except ValueError:
            pass
        if request.form.get("promo") in PROMO_MODES:
            sel_promo = request.form["promo"]

        fc = forecast(sel_store, sel_promo)
        total = float(fc["forecast"].sum())
        ss = safety.get(sel_store)
        uplift = None
        if sel_promo != "none":
            base = float(forecast(sel_store, "none")["forecast"].sum())
            if base > 0:
                uplift = f"{(total - base) / base * 100:+.1f}%"
        res = {
            "store": sel_store,
            "type": TYPE_LABEL.get(int(info.loc[sel_store, "store_type"]), "?"),
            "opens_sunday": bool(info.loc[sel_store, "opens_sunday"]),
            "total": f"{total:,.0f}",
            "safety": "n/a" if ss is None or pd.isna(ss) else f"{ss:,.0f}",
            "reorder": "n/a" if ss is None or pd.isna(ss) else f"{total + ss:,.0f}",
            "uplift": uplift,
            "rows": [
                {"date": r.date.strftime("%d %b %Y"), "day": r.day, "promo": r.promo,
                 "closed": r.closed, "value": f"{r.forecast:,.0f}"}
                for r in fc.itertuples()
            ],
        }

    return render_template_string(
        PAGE, stores=stores, modes=PROMO_MODES, sel_store=sel_store, sel_promo=sel_promo,
        res=res, last_date=LAST_DATE.strftime("%d %b %Y"),
    )


if __name__ == "__main__":
    app.run(debug=True)
