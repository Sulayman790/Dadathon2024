import yfinance as yf
import boto3
import botocore
import pandas as pd
from io import StringIO

# Set up AWS S3 client
s3_client = boto3.client('s3', 
                        aws_access_key_id='AKIAR2QID37NBSCXNSWA',
                        aws_secret_access_key='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',
                        region_name='us-west-2')

# Specify the S3 bucket
bucket_name = "companiesdatas"

def extraire_donnees_completes(company_name):
    # Récupération des données boursières
    ticker = yf.Ticker(company_name)
    data = ticker.history(period="1y")  # Données sur un an pour l'analyse technique
    
    # Ajout des indicateurs techniques
    
    # Moyennes mobiles
    data['MA_20'] = data['Close'].rolling(window=20).mean()  # Moyenne mobile 20 jours
    data['MA_50'] = data['Close'].rolling(window=50).mean()  # Moyenne mobile 50 jours

    # RSI
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))

    # Bandes de Bollinger
    data['BB_upper'] = data['MA_20'] + 2 * data['Close'].rolling(window=20).std()
    data['BB_lower'] = data['MA_20'] - 2 * data['Close'].rolling(window=20).std()

    # Ajouter d'autres indicateurs financiers de yfinance
    info = ticker.info
    
    indicateurs_financiers = {
        "Net Profit Margin (%)": info.get('profitMargins', 'N/A') * 100 if info.get('profitMargins') else 'N/A',
        "Return on Equity (ROE) (%)": info.get('returnOnEquity', 'N/A') * 100 if info.get('returnOnEquity') else 'N/A',
        "Quick Ratio": info.get('quickRatio', 'N/A'),
        "Debt/Equity": info.get('debtToEquity', 'N/A'),
        "Earnings Growth": info.get('earningsGrowth', 'N/A'),
        "Price-to-Earnings Ratio (PER) - Trailing": info.get('trailingPE', 'N/A'),
        "Price-to-Earnings Ratio (PER) - Forward": info.get('forwardPE', 'N/A'),
        "EV/EBITDA": info.get('enterpriseToEbitda', 'N/A'),
        "Free Cash Flow Yield": info.get('freeCashflow', 'N/A'),
        "Dividend Yield (%)": info.get('dividendYield', 'N/A') * 100 if info.get('dividendYield') else 'N/A',
        "Market Cap": info.get('marketCap', 'N/A'),
        "Beta": info.get('beta', 'N/A'),
        "Enterprise Value": info.get('enterpriseValue', 'N/A'),
        "Revenue": info.get('totalRevenue', 'N/A'),
        "Gross Profit": info.get('grossProfits', 'N/A'),
        "EBITDA": info.get('ebitda', 'N/A'),
        "Operating Income": info.get('operatingIncome', 'N/A'),
        "Net Income": info.get('netIncomeToCommon', 'N/A'),
        "Total Debt": info.get('totalDebt', 'N/A'),
        "Total Cash": info.get('totalCash', 'N/A'),
        "Shares Outstanding": info.get('sharesOutstanding', 'N/A')
    }

    # Conversion des données financières en DataFrame
    df_financier = pd.DataFrame(indicateurs_financiers, index=[0])
    
    # Ajout des informations financières comme des colonnes statiques à chaque ligne des données techniques
    for col in df_financier.columns:
        data[col] = df_financier[col][0]

    # Suppression des lignes avec des valeurs manquantes
    data.dropna(inplace=True)

    return data

# Upload DataFrame to S3
def upload_to_s3(dataframe, bucket, s3_path):
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer)
    s3_client.put_object(Bucket=bucket, Key=s3_path, Body=csv_buffer.getvalue())
    print(f"Data uploaded to s3://{bucket}/{s3_path}")

# Main function
def main():
    company_name = input("Entrez le symbole boursier de la compagnie (ex: AAPL pour Apple): ")
    df_complet = extraire_donnees_completes(company_name)
    print(df_complet)
    
    # Set dynamic file path for the S3 upload
    s3_file_path = f"data/{company_name}_technical_analysis.csv"
    
    # Upload to S3
    upload_to_s3(df_complet, bucket_name, s3_file_path)

if __name__ == "__main__":
    main()
