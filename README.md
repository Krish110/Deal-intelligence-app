# 💎 Inter Gold — Deal Intelligence Engine

A Streamlit app that reads any retailer's annual report PDF and produces a complete B2B deal intelligence brief for lab-grown diamond jewellery sales.

## What it does

Upload a retailer's annual report → get a 12-point intelligence brief:

- **GO / CAUTION / AVOID** verdict with confidence score
- Jewellery category signals extracted from the report
- ESG alignment score (critical for LGD pitch)
- Financial health & counterparty risk assessment
- Shopper profile match analysis
- Custom approach strategy & opening line
- Opportunities found in their own report
- Cautions & red flags
- Your negotiation leverage points
- What NOT to say or do
- Recommended deal structure
- First buyer meeting agenda

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set the main file path to `app.py`
5. Add your Anthropic API key in **Secrets**:

```toml
GEMINI_API_KEY = "AIzaSyACJ_nIa23Tys1zfAFK88KlTMJu0gh6DPg"
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set your API key:
```bash
export GEMINI_API_KEY="AIzaSyACJ_nIa23Tys1zfAFK88KlTMJu0gh6DPg"
```

## Built for

Inter Gold India · Mumbai · IGI Certified Lab-Grown Diamond Jewellery  
Target retailers: H&M, Inditex/Zara, Zalando, Otto, John Lewis, El Corte Inglés
