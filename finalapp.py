import streamlit as st
import yfinance as yf
import datetime as dt
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import mplfinance as mpf
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
from IPython.display import display


st.title("Financial sevices")

model_selection = st.selectbox(
    "Select the model you would like to use ",
    options=["DDM valuation model","Fundamental Data","Technical Data"],
    index=None,
)







if model_selection == "DDM valuation model":  
    st.subheader("DDM Model valuation")

    nation = st.selectbox(
        "select a Stock market",
        options=["Saudi Arabia", "United States"],
        index=None,
    )
    if nation == "none":
        st.info("Please select a nation first.")
        st.stop()

    if nation is None:
        st.info("Please select a nation first.")
        st.stop()

    if nation == "Saudi Arabia":
        st.write("Saudi Arabia has been selected")
        ticker_symbol = st.text_input("ticker",help="For example 2222 for  Saudi Aramco")
        input1 = (ticker_symbol + ".SR") if ticker_symbol else ""
        if input1 == "Eyad.SR":
            st.info("Roses are red violets are blue im autistic and so are you Eyad")
            st.stop()
        elif input1 == "eyad.SR":
            st.info("Roses are red violets are blue im autistic and so are you Eyad")
            st.stop()
    elif nation == "United States":
        st.write("United states of america has been selected")
        ticker_symbol = st.text_input("ticker",help=" For example MSFT for Microsfot")
        input1 = ticker_symbol.strip()

    if not input1:
        st.warning("Please input a stock ticker.")
        st.stop()



    stock = yf.Ticker(input1)



    data = stock.history("3y")
    if data.empty:
        st.error("No market data was returned for that ticker. Please try another one.")
        st.stop()
    mrp = .06
    rfr = .051
    name = stock.info.get("longName")


    balance_sheet = stock.balance_sheet
    income_sheet = stock.income_stmt
    cashflow = stock.cashflow
    dividends = abs(cashflow.loc["Cash Dividends Paid"].iloc[0])
    netincome = income_sheet.loc["Net Income"].iloc[0]
    equity = balance_sheet.loc["Stockholders Equity"].iloc[0]
    shares = balance_sheet.loc["Ordinary Shares Number"].iloc[0]

    dividends_per = dividends/shares
    all_divs = abs(cashflow.loc["Cash Dividends Paid"])
    all_shares = balance_sheet.loc["Ordinary Shares Number"]
    meangrowth = np.mean((abs(all_divs)/all_shares)/(abs(all_divs.shift(-1)/all_shares))-1)


    roe = netincome/equity
    retention = (netincome-dividends)/netincome

    beta = stock.info.get("beta")
    rr = rfr+(mrp*beta) 
    final = len(data) - 1

    if len(data) < 2:
        st.error("Not enough historical data rows to calculate the model.")
        st.stop()

    st.write(name + ": has been selected")



    return_choice = st.selectbox(
        "select Requierd Rate of Return",
        options=[
            "Calculated Return",
            "5%",
            "6%",
            "7%",
            "8%",
            "9%",
            "10%",
            "11%",
            "12%",

    ],
        index=None,
    )
    if return_choice == "Calculated Return" :
        rr = rr
    elif return_choice == "5%":
        rr = .05
    elif return_choice == "6%":
        rr = .06
    elif return_choice == "7%":
        rr = .07
    elif return_choice == "8%":
        rr = .08
    elif return_choice == "9%":
        rr = .09
    elif return_choice == "10%":
        rr = .1
    elif return_choice == "11%":
        rr = .11
    elif return_choice == "12%":
        rr = .12
    else:
        st.warning("Please select a Required Rate of Return")
        st.stop()

        

    growth_choice = st.selectbox( 
        "Select a growth Rate",
        options=[
            "Mature 2%",
            "Mature 3%",
            "Historical growth",
            "ROE",
        ],
        index=None,
    )






    if growth_choice == "Mature 2%":
        g = .02
    elif growth_choice == "Mature 3%":
        g = .03
    elif growth_choice == "Historical growth":
        g = meangrowth
        if g > rr:
            st.warning("Error growth is greater than rr")
            st.stop()
    elif growth_choice == "ROE":
        g = roe * retention
        if g > rr:
            st.warning("Error growth is greater than rr")
            st.stop()
    else:
        st.warning("Please select a Growth Rate")
        st.stop()












    bear = round((dividends_per*(1+(g -.01)))/((rr+.001)-g),2)
    base = round((dividends_per*(1+g))/(rr-g),3)
    bull = round((dividends_per*(1+(g+.01)))/((rr-.001)-g),2)
    current = round(data["Close"].iloc[final], 2)
    if pd.isna(current):
        current = round(data["Close"].iloc[final-1], 2)
    
    if bear>current:
        x1 = "undervalued"
    else:
        x1 = "overvalued"
        
    if base>current:
        x2 = "undervalued"
    else:
        x2 = "overvalued"

    if bull>current:
        x3 = "undervalued"
    else:
        x3 = "overvalued"




    st.write("Current Price is: $" + str(current))
    finaloutput = {"Statement":["Bear value is: ","Base value is: ","Bull value is: "],"Valuation":[bear,base,bull],"result":[x1,x2,x3]}
    finaloutput_df = pd.DataFrame(finaloutput)
    st.dataframe(finaloutput_df.head())


    g = round(g*100,2)
    retention = round(retention*100,2)
    rr = rr = round(rr*100,2)
    st.write("required return rate is "+ str(rr)+"%")
    st.write("growth rate is " + str(g) + "%")

elif model_selection == "Fundamental Data":
    def safe_divide(numerator, denominator, default=0):
        try:
            if denominator in (None, 0, 0.0) or pd.isna(denominator):
                return default
        except Exception:
            return default

        try:
            return numerator / denominator
        except (TypeError, ZeroDivisionError):
            return default


    def get_cashflow_value(cashflow_df, labels, position, default=0):
        for label in labels:
            if label in cashflow_df.index:
                return cashflow_df.loc[label].iloc[position]
        return default


    def get_df_value(df, labels, position, default=0):
        for label in labels:
            if label in df.index:
                try:
                    return df.loc[label].iloc[position]
                except Exception:
                    return default
        return default


    def get_reit_ffo(cashflow_df, position, default=0):
        return get_df_value(
            cashflow_df,
            ["Funds From Operations", "Operating Cash Flow", "Free Cash Flow"],
            position,
            default,
        )

    st.subheader("Fundamental analysis")

    nation = st.selectbox(
        "select a Stock market",
        options=["Saudi Arabia", "United States"],
        index=None,
    )
    
    if nation == "Saudi Arabia":
        st.write("Saudi Arabia has been selected")
        ticker_symbol = st.text_input("Enter Saudi Stock ticker",help="For example 2222 for Saudi Aramco")
        ticker_input = (ticker_symbol + ".SR") if ticker_symbol else ""
        if ticker_input == "Abdulrahman.SR":
            st.info("maidenless tarnished ahh, thou'rt unfit to even graft")
            st.stop()
        elif ticker_input == "abdulrahman.SR":
            st.info("maidenless tarnished ahh, thou'rt unfit to even graft")
            st.stop()
    elif nation == "United States":
        st.write("United states of america has been selected")
        ticker_symbol = st.text_input("Enter US Stock ticker",help="For example MSFT for Microsoft")
        ticker_input = ticker_symbol.strip()
    else:
        st.info("Please select a stock market.")
        st.stop()

    if not ticker_input:
        st.warning("Please input a stock ticker.")
        st.stop()

    stock = yf.Ticker(ticker_input)
    name = stock.info.get("longName")
    info_share_count = (
        stock.info.get("sharesOutstanding")
        or stock.info.get("floatShares")
        or stock.info.get("ordinarySharesNumber")
        or stock.info.get("shareCount")
        or stock.fast_info.get("shares")
        or 0
    )


    data = stock.history("1y")
    if data.empty:
        st.error("No market data was returned for that ticker. Please try another one.")
        st.stop()

    data = data.reset_index()
    data["Date"] = pd.to_datetime(data["Date"]).dt.date
    data = data[["Date","Close","High","Low","Volume"]]

    st.write(str(name) + ": Has been selected")
    st.write("")
    st.write("")
    st.write("")



    final_day = len(data) - 1
    if len(data) < 2:
        st.error("Not enough historical data rows to calculate the model.")
        st.stop()

    testing1 = data["Close"].iloc[final_day]
    if pd.isna(testing1):
        final_day = len(data) - 2

    Quarter_ago = max(final_day - 63, 0)
    year_ago = max(final_day - 252, 0)
    financial = stock.income_stmt
    balance = stock.balance_sheet
    cashflow = stock.cashflow
    ebitdaP1 = get_df_value(financial, ["EBITDA", "Ebitda"], 1, 0)
    assetP1 = get_df_value(balance, ["Total Assets"], 1, 0)
    dividendsP1 = abs(get_df_value(cashflow, ["Cash Dividends Paid", "Dividends Paid"], 1, 0))
    equityP1 = get_df_value(balance, ["Stockholders Equity", "Total Equity"], 1, 0)
    liabilitiesP1 = get_df_value(balance, ["Total Liabilities Net Minority Interest", "Total Liabilities"], 1, 0)
    incomeP1 = get_df_value(financial, ["Net Income", "Net Income (Loss)"], 1, 0)
    revenueP1 = get_df_value(financial, ["Total Revenue", "Revenue"], 1, 0)
    sharesP1 = get_df_value(balance, ["Share Issued", "Ordinary Shares Number", "Shares Outstanding", "Total Shares Outstanding"], 1, 0) or info_share_count
    epsP1 = get_df_value(financial, ["Basic EPS", "Diluted EPS", "EPS"], 1, 0)
    price_P1 = round(data["Close"].iloc[year_ago],2)
    name1 = "current year"
    name2 = "past year"


    statement_type = st.selectbox(
        "Select a statement type",
        options=["None","(A) yearly", "(B) quarterly"],
        index=None,
    )
    if statement_type == "None":
        st.stop()
    if statement_type is None:
        st.stop()

    if statement_type == "(A) yearly":
        type_loop = False
        st.write("")
        st.write("Yearly data selected")
        st.write("")
        financial = stock.income_stmt
        balance = stock.balance_sheet
        cashflow = stock.cashflow
        average_inventoryP1 = (get_df_value(balance, ["Inventory"], 1, 0)+get_df_value(balance, ["Inventory"], 2, 0))/2
        cogsP1 = get_df_value(financial, ["Cost Of Revenue", "Cost of Revenue"], 1, 0)
        ebitdaP1 = get_df_value(financial, ["EBITDA", "Ebitda"], 1, 0)
        assetP1 = get_df_value(balance, ["Total Assets"], 1, 0)
        dividendsP1 = abs(get_df_value(cashflow, ["Cash Dividends Paid", "Dividends Paid"], 1, 0))
        equityP1 = get_df_value(balance, ["Stockholders Equity", "Total Equity"], 1, 0)
        liabilitiesP1 = get_df_value(balance, ["Total Liabilities Net Minority Interest", "Total Liabilities"], 1, 0)
        incomeP1 = get_df_value(financial, ["Net Income", "Net Income (Loss)"], 1, 0)
        revenueP1 = get_df_value(financial, ["Total Revenue", "Revenue"], 1, 0)
        sharesP1 = get_df_value(balance, ["Share Issued", "Ordinary Shares Number", "Shares Outstanding", "Total Shares Outstanding"], 1, 0) or info_share_count
        epsP1 = get_df_value(financial, ["Basic EPS", "Diluted EPS", "EPS"], 1, 0)
        navP1 = safe_divide(assetP1 - liabilitiesP1, sharesP1)
        roep1 = safe_divide(incomeP1, equityP1)
        roaP1 = safe_divide(incomeP1, assetP1)
        previous_revenueP1 = get_df_value(financial, ["Total Revenue", "Revenue"], 2, revenueP1)
        previous_incomeP1 = get_df_value(financial, ["Net Income", "Net Income (Loss)"], 2, incomeP1)
        previous_epsP1 = get_df_value(financial, ["Basic EPS", "Diluted EPS", "EPS"], 2, epsP1)
        previous_freecashflowP1 = get_df_value(cashflow, ["Free Cash Flow"], 2, get_df_value(cashflow, ["Free Cash Flow"], 1, 0))
        revenue_growthP1 = safe_divide(revenueP1, previous_revenueP1) - 1 if previous_revenueP1 else 0
        earning_growthP1 = safe_divide(incomeP1, previous_incomeP1) - 1 if previous_incomeP1 else 0
        eps_growthP1 = safe_divide(epsP1, previous_epsP1) - 1 if previous_epsP1 else 0
        freecashflow_growthP1 = safe_divide(get_df_value(cashflow, ["Free Cash Flow"], 1, 0), previous_freecashflowP1) - 1 if previous_freecashflowP1 else 0
        freecashflowP1 = get_df_value(cashflow, ["Free Cash Flow"], 1, 0)
        operating_cashflow_marginP1 = get_df_value(cashflow, ["Operating Cash Flow"], 1, 0) / revenueP1 if revenueP1 else 0
        profit_marginP1 = incomeP1/revenueP1 if revenueP1 else 0
        operating_marginP1 = get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 1, 0) / revenueP1 if revenueP1 else 0
        payout_ratioP1 = dividendsP1/incomeP1 if incomeP1 else 0
        interest_coverageP1 = get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 1, 0) / get_df_value(financial, ["Interest Expense"], 1, 0) if get_df_value(financial, ["Interest Expense"], 1, 0) else 0
        average_inventoryP1 = (get_df_value(balance, ["Inventory", "Inventories"], 1, 0)+get_df_value(balance, ["Inventory", "Inventories"], 2, 0))/2
        inventory_turnoverP1 = cogsP1/average_inventoryP1 if average_inventoryP1 else 0


        tax_rateP1 = get_df_value(financial, ["Tax Rate For Calcs", "Tax Rate"], 1, 0)
        operating_incomeP1 = get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 1, 0)
        nopatP1 = operating_incomeP1 * (1-tax_rateP1)
        avg_investedcapitalP1 = (((assetP1 - get_df_value(balance, ["Current Liabilities"], 1, 0) - get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 1, 0))+(get_df_value(balance, ["Total Assets"], 2, assetP1) - get_df_value(balance, ["Current Liabilities"], 2, 0) - get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 2, 0)))/2)
        freecashflow_marginP1 = get_df_value(cashflow, ["Free Cash Flow"], 1, 0)/revenueP1 if revenueP1 else 0
        price_P1 = round(data["Close"].iloc[year_ago],2)
        freecashflow_yieldP1 = safe_divide(get_df_value(cashflow, ["Free Cash Flow"], 1, 0), price_P1 * sharesP1)
        equity_per_shareP1 = safe_divide(equityP1, sharesP1)
        price_to_bookP1 = safe_divide(price_P1, equity_per_shareP1)
        ev_ebitda_p1 = safe_divide(((price_P1*sharesP1)+get_df_value(balance, ["Total Debt"], 1, 0)-get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 1, 0)), ebitdaP1)
        ffo_pershareP1 = round(safe_divide(get_reit_ffo(cashflow, 1, 0), sharesP1),2)
        price_to_ffoP1 = round(safe_divide(price_P1, ffo_pershareP1),2)
        repurchase_p1 = get_cashflow_value(
            cashflow,
            ["Repurchase of Stock", "Repurchase Of Stock", "Repurchases of Stock", "Repurchase of Common Stock"],
            1,
            0,
        )
        total_returnP1 = safe_divide((safe_divide(dividendsP1, sharesP1) + safe_divide(repurchase_p1, sharesP1)), price_P1)
        name1 = "current year"
        name2 = "past year"
    elif statement_type == "(B) quarterly":
        type_loop = False
        st.write("")
        st.write("Quarterly data selected")
        st.write("")
        financial = stock.quarterly_income_stmt
        balance = stock.quarterly_balance_sheet
        cashflow = stock.quarterly_cash_flow
        cogsP1 = get_df_value(financial, ["Cost Of Revenue", "Cost of Revenue"], 4, 0)
        average_inventoryP1 = (get_df_value(balance, ["Inventory"], 4, 0)+get_df_value(balance, ["Inventory"], 8, 0))/2
        ebitdaP1 = get_df_value(financial, ["EBITDA", "Ebitda"], 4, 0)
        assetP1 = get_df_value(balance, ["Total Assets"], 4, 0)
        dividendsP1 = abs(get_df_value(cashflow, ["Cash Dividends Paid", "Dividends Paid"], 4, 0))
        equityP1 = get_df_value(balance, ["Stockholders Equity", "Total Equity"], 4, 0)
        liabilitiesP1 = get_df_value(balance, ["Total Liabilities Net Minority Interest", "Total Liabilities"], 4, 0)
        incomeP1 = get_df_value(financial, ["Net Income", "Net Income (Loss)"], 4, 0)
        revenueP1 = get_df_value(financial, ["Total Revenue", "Revenue"], 4, 0)
        sharesP1 = get_df_value(balance, ["Share Issued", "Ordinary Shares Number", "Shares Outstanding", "Total Shares Outstanding"], 4, 0) or info_share_count
        epsP1 = get_df_value(financial, ["Basic EPS", "Diluted EPS", "EPS"], 4, 0)
        navP1 = safe_divide(assetP1 - liabilitiesP1, sharesP1)
        roep1 = safe_divide(incomeP1, equityP1)
        roaP1 = safe_divide(incomeP1, assetP1)
        previous_revenueP1 = get_df_value(financial, ["Total Revenue", "Revenue"], 8, revenueP1)
        previous_incomeP1 = get_df_value(financial, ["Net Income", "Net Income (Loss)"], 8, incomeP1)
        previous_epsP1 = get_df_value(financial, ["Basic EPS", "Diluted EPS", "EPS"], 8, epsP1)
        previous_freecashflowP1 = get_df_value(cashflow, ["Free Cash Flow"], 8, get_df_value(cashflow, ["Free Cash Flow"], 4, 0))
        revenue_growthP1 = safe_divide(revenueP1, previous_revenueP1) - 1 if previous_revenueP1 else 0
        earning_growthP1 = safe_divide(incomeP1, previous_incomeP1) - 1 if previous_incomeP1 else 0
        eps_growthP1 = safe_divide(epsP1, previous_epsP1) - 1 if previous_epsP1 else 0
        freecashflow_growthP1 = safe_divide(get_df_value(cashflow, ["Free Cash Flow"], 4, 0), previous_freecashflowP1) - 1 if previous_freecashflowP1 else 0
        freecashflowP1 = get_df_value(cashflow, ["Free Cash Flow"], 4, 0)
        operating_cashflow_marginP1 = get_df_value(cashflow, ["Operating Cash Flow"], 4, 0) / revenueP1 if revenueP1 else 0
        profit_marginP1 = incomeP1/revenueP1 if revenueP1 else 0
        operating_marginP1 = get_df_value(financial, ["Operating Income"], 4, 0) / revenueP1 if revenueP1 else 0
        payout_ratioP1 = dividendsP1/incomeP1 if incomeP1 else 0
        interest_coverageP1 = get_df_value(financial, ["Operating Income"], 4, 0) / get_df_value(financial, ["Interest Expense"], 4, 0) if get_df_value(financial, ["Interest Expense"], 4, 0) else 0
        inventory_turnoverP1 = cogsP1/average_inventoryP1 if average_inventoryP1 else 0
        
        

        tax_rateP1 = get_df_value(financial, ["Tax Rate For Calcs", "Tax Rate"], 4, 0)
        operating_incomeP1 = get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 4, 0)
        nopatP1 = operating_incomeP1 * (1-tax_rateP1)
        total_assets_4 = get_df_value(balance, ["Total Assets"], 4, 0)
        current_liabilities_4 = get_df_value(balance, ["Current Liabilities"], 4, 0)
        cash_4 = get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 4, 0)
        total_assets_5 = get_df_value(balance, ["Total Assets"], 5, 0)
        current_liabilities_5 = get_df_value(balance, ["Current Liabilities"], 5, 0)
        cash_5 = get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 5, 0)
        avg_investedcapitalP1 = (((total_assets_4 - current_liabilities_4 - cash_4)+(total_assets_5 - current_liabilities_5 - cash_5)))/2
        freecashflow_marginP1 = get_df_value(cashflow, ["Free Cash Flow"], 4, 0)/revenueP1 if revenueP1 else 0
        price_P1 = round(data["Close"].iloc[Quarter_ago],2)
        freecashflow_yieldP1 = safe_divide(get_df_value(cashflow, ["Free Cash Flow"], 4, 0), price_P1 * sharesP1)
        equity_per_shareP1 = safe_divide(equityP1, sharesP1)
        price_to_bookP1 = safe_divide(price_P1, equity_per_shareP1)
        ev_ebitda_p1 = safe_divide(((price_P1*sharesP1)+get_df_value(balance, ["Total Debt"], 4, 0)-get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 4, 0)), ebitdaP1)
        ffo_pershareP1 = safe_divide(get_reit_ffo(cashflow, 4, 0), sharesP1)
        price_to_ffoP1 = round(safe_divide(price_P1, ffo_pershareP1),2)
        repurchase_p1 = get_cashflow_value(
            cashflow,
            ["Repurchase of Stock", "Repurchase Of Stock", "Repurchases of Stock", "Repurchase of Common Stock"],
            4,
            0,
        )
        total_returnP1 = safe_divide((safe_divide(dividendsP1, sharesP1) + safe_divide(repurchase_p1, sharesP1)), price_P1)
        name1 = "current quarter"
        name2 = "past quarter"



    price = round(data["Close"].iloc[final_day],2)

    cogs = get_df_value(financial, ["Cost Of Revenue", "Cost of Revenue"], 0, 0)
    shares = get_df_value(balance, ["Share Issued", "Ordinary Shares Number", "Shares Outstanding", "Total Shares Outstanding"], 0, 0) or info_share_count
    repo_pershare = safe_divide(
        get_cashflow_value(
            cashflow,
            ["Repurchase of Stock", "Repurchase Of Stock", "Repurchases of Stock", "Repurchase of Common Stock"],
            0,
            0,
        ),
        shares,
    )
    dividends_pershare = safe_divide(abs(get_df_value(cashflow, ["Cash Dividends Paid", "Dividends Paid"], 0, 0)), shares)
    enterprise_value = stock.info.get("enterpriseValue")
    mrkt_cap = stock.info.get("marketCap")
    eps = get_df_value(financial, ["Basic EPS", "Diluted EPS", "EPS"], 0, 0)
    ebitda = get_df_value(financial, ["EBITDA", "Ebitda"], 0, 0)
    asset = get_df_value(balance, ["Total Assets"], 0, 0)
    dividends = abs(get_df_value(cashflow, ["Cash Dividends Paid", "Dividends Paid"], 0, 0))
    equity = get_df_value(balance, ["Stockholders Equity", "Total Equity"], 0, 0)
    liabilities = get_df_value(balance, ["Total Liabilities Net Minority Interest", "Total Liabilities"], 0, 0)
    income = get_df_value(financial, ["Net Income", "Net Income (Loss)"], 0, 0)
    revenue = get_df_value(financial, ["Total Revenue", "Revenue"], 0, 0)
    nav = safe_divide(asset - liabilities, shares)
    roe = safe_divide(income, equity)
    roa = safe_divide(income, asset)
    revenue_growth = safe_divide(revenue, revenueP1) - 1 if revenueP1 else 0
    earning_growth = safe_divide(income, incomeP1) - 1 if incomeP1 else 0
    eps_growth = safe_divide(eps, epsP1) - 1 if epsP1 else 0
    profit_margin = safe_divide(income, revenue)
    operating_margin = safe_divide(get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 0, 0), revenue)
    payout_ratio = safe_divide(dividends, income)
    price_to_book = safe_divide(mrkt_cap, equity) if mrkt_cap else 0
    ev_ebitda = safe_divide(enterprise_value, ebitda) if enterprise_value else 0
    interest_coverage = safe_divide(get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 0, 0), get_df_value(financial, ["Interest Expense"], 0, 0))
    average_inventory = (get_df_value(balance, ["Inventory", "Inventories"], 0, 0)+get_df_value(balance, ["Inventory", "Inventories"], 1, 0))/2
    inventory_turnover = safe_divide(cogs, average_inventory)
    total_return = safe_divide((dividends_pershare + repo_pershare), price)
    ffo_pershare = safe_divide(get_reit_ffo(cashflow, 0, 0), shares)
    price_to_ffo = round(safe_divide(price, ffo_pershare),2)





    tax_rate = get_df_value(financial, ["Tax Rate For Calcs", "Tax Rate"], 0, 0)
    operating_income = get_df_value(financial, ["Operating Income", "Operating Income (Loss)"], 0, 0)
    nopat = operating_income * (1-tax_rate)
    avg_investedcapital = (((asset - get_df_value(balance, ["Current Liabilities"], 0, 0) - get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 0, 0))+(assetP1 - get_df_value(balance, ["Current Liabilities"], 1, 0) - get_df_value(balance, ["Cash And Cash Equivalents", "Cash and Cash Equivalents"], 1, 0)))/2)
    roic = nopat / avg_investedcapital if avg_investedcapital else 0

    freecashflow_margin = get_df_value(cashflow, ["Free Cash Flow"], 0, 0) / revenue if revenue else 0
    freecashflow = get_df_value(cashflow, ["Free Cash Flow"], 0, 0)
    freecashflow_yield = get_df_value(cashflow, ["Free Cash Flow"], 0, 0) / mrkt_cap if mrkt_cap else 0
    freecashflow_growth = (get_df_value(cashflow, ["Free Cash Flow"], 0, 0) / get_df_value(cashflow, ["Free Cash Flow"], 1, get_df_value(cashflow, ["Free Cash Flow"], 0, 0))) - 1 if get_df_value(cashflow, ["Free Cash Flow"], 1, get_df_value(cashflow, ["Free Cash Flow"], 0, 0)) else 0
    operating_cashflow_margin = get_df_value(cashflow, ["Operating Cash Flow"], 0, 0) / revenue if revenue else 0
    price = round(data["Close"].iloc[final_day],2)


    eps = round(eps,2)
    epsP1 = round(epsP1,2)
    pe_ratio = round(price/eps,2)
    pe_ratioP1 = round(price_P1/epsP1,2)
    asset_turnover =  round(revenue/asset,2)
    asset_turnoverP1 =  round(revenueP1/assetP1,2)
    dividend_yield = round(safe_divide(dividends, shares) / price * 100, 2) if price else 0
    dividend_yieldP1 = round(safe_divide(dividendsP1, sharesP1) / price_P1 * 100, 2) if price_P1 else 0
    dividend_yield_show = str(dividend_yield) + "%"
    dividend_yieldP1_show = str(dividend_yieldP1) + "%"
    debt_equity = round(safe_divide(liabilities, equity),2)
    debt_equityP1 = round(safe_divide(liabilitiesP1, equityP1),2)
    roic = round(roic,2)
    roicp1 = round((nopatP1/avg_investedcapitalP1),2)
    nav = round(nav,2)
    navP1 = round(safe_divide(assetP1 - liabilitiesP1, sharesP1),2)
    roe = round(roe,2)
    roa = round(roa,2)
    roeP1 = round(roep1,2)
    roaP1 = round(roaP1,2)
    revenue_growth = str(round(revenue_growth*100,2)) + "%"
    revenue_growthP1 = str(round(revenue_growthP1*100,2)) + "%"
    earning_growth = str(round(earning_growth*100,2)) + "%"
    earning_growthP1 = str(round(earning_growthP1*100,2)) + "%"
    eps_growth = str(round(eps_growth*100,2)) + "%"
    eps_growthP1 = str(round(eps_growthP1*100,2)) + "%"
    freecashflow_margin = str(round(freecashflow_margin*100,2)) + "%"
    freecashflow_marginP1 = str(round(freecashflow_marginP1*100,2)) + "%"
    freecashflow_yield = str(round(freecashflow_yield*100,2)) + "%"
    freecashflow_yieldP1 = str(round(freecashflow_yieldP1*100,2)) + "%"
    freecashflow_growth = str(round(freecashflow_growth*100,2)) + "%"
    freecashflow_growthP1 = str(round(freecashflow_growthP1*100,2)) + "%"
    operating_cashflow_margin = str(round(operating_cashflow_margin*100,2)) + "%"
    operating_cashflow_marginP1 = str(round(operating_cashflow_marginP1*100,2)) + "%"
    profit_margin = str(round(profit_margin*100,2)) + "%"
    profit_marginP1 = str(round(profit_marginP1*100,2)) + "%"
    operating_margin = str(round(operating_margin*100,2)) + "%"
    operating_marginP1 = str(round(operating_marginP1*100,2)) + "%"
    payout_ratio = str(round(payout_ratio*100,2)) + "%"
    payout_ratioP1 = str(round(payout_ratioP1*100,2)) + "%"
    price_to_book = str(round(price_to_book,2)) 
    price_to_bookP1 = str(round(price_to_bookP1,2)) 
    ev_ebitda = str(round(ev_ebitda,2))
    ev_ebitda_p1 = str(round(ev_ebitda_p1,2))
    interest_coverage = str(round(interest_coverage,2))
    interest_coverageP1 = str(round(interest_coverageP1,2))
    inventory_turnover = str(round(inventory_turnover,2))
    inventory_turnoverP1 = str(round(inventory_turnoverP1,2))
    total_return = str(round(total_return*100,2)) + "%"
    total_returnP1 = str(round(total_returnP1*100,2)) + "%"





    if statement_type in ["(A) yearly", "(B) quarterly"]:
        final_output = {"Ratios": ["ROIC","Price","EPS","PE Ratio","asset Turnover","debt equity ratio","dividend yield", "NAV","ROE","ROA","Revenue Growth","Earning Growth","EPS Growth","Free Cash Flow Margin","Free Cash Flow Yield","Free Cash Flow Growth","Operating Cash Flow Margin","Profit Margin","Operating Margin","Payout Ratio","Price to Book","EV/EBITDA","Interest Coverage","Inventory Turnover","Total Return","price to FFO"],name1:[roic,price,eps,pe_ratio,asset_turnover,debt_equity,dividend_yield_show,nav,roe,roa,revenue_growth,earning_growth,eps_growth,freecashflow_margin,freecashflow_yield,freecashflow_growth,operating_cashflow_margin,profit_margin,operating_margin,payout_ratio,price_to_book,ev_ebitda,interest_coverage,inventory_turnover,total_return,price_to_ffo],name2:[roicp1,price_P1,epsP1,pe_ratioP1,asset_turnoverP1,debt_equityP1,dividend_yieldP1_show,navP1,roeP1,roaP1,revenue_growthP1,earning_growthP1,eps_growthP1,freecashflow_marginP1,freecashflow_yieldP1,freecashflow_growthP1,operating_cashflow_marginP1,profit_marginP1,operating_marginP1,payout_ratioP1,price_to_bookP1,ev_ebitda_p1,interest_coverageP1,inventory_turnoverP1,total_returnP1,price_to_ffoP1]}
        df_final_ouput = pd.DataFrame(final_output)
        

        reit_output = {"Ratios":["Price","NAV","Price to FFO","Price to Book","Dividend Yield"],name1:[price,nav,price_to_ffo,price_to_book,dividend_yield_show],name2:[price_P1,navP1,price_to_ffoP1,price_to_bookP1,dividend_yieldP1_show]}
        df_reit = pd.DataFrame(reit_output)
        

        debt_output = {"Ratios":["Debt to Equity","Interest Coverage","EV/EBITDA"],name1:[debt_equity,interest_coverage,ev_ebitda],name2:[debt_equityP1,interest_coverageP1,ev_ebitda_p1]}
        df_debt = pd.DataFrame(debt_output)

        growth_output = {"Ratios":["Revenue","Revenue Growth","Earnings","Earnings Growth","EPS","EPS Growth","Free Cashflow","Free Cashflow Growth"],name1:[revenue,revenue_growth,income,earning_growth,eps,eps_growth,freecashflow,freecashflow_growth],name2:[revenueP1,revenue_growthP1,incomeP1,earning_growthP1,epsP1,eps_growthP1,freecashflowP1,freecashflow_growthP1]}
        df_growth = pd.DataFrame(growth_output)

        valuation_output = {"Ratios":["Price","PE Ratio","Total Yield","Dividend Yield","Payout Ratio"],name1:[price,pe_ratio,total_return,dividend_yield_show,payout_ratio],name2:[price_P1,pe_ratioP1,total_returnP1,dividend_yieldP1_show,payout_ratioP1]}
        df_valuation = pd.DataFrame(valuation_output)

        efficency_output = {"Ratios":["ROIC","ROE","ROA","Profit Margin","Free Cashflow Margin","Operating Cashflow Margin","Asset Turnover","Inventory Turnover"],name1:[roic,roe,roa,profit_margin,freecashflow_margin,operating_cashflow_margin,asset_turnover,inventory_turnover],name2:[roicp1,roeP1,roaP1,profit_marginP1,freecashflow_marginP1,operating_cashflow_marginP1,asset_turnoverP1,inventory_turnoverP1]}
        df_efficency = pd.DataFrame(efficency_output)
    
        basic_output = {"Ratios":["Price","PE Ratio","ROIC","Total Yield","EPS","ROE","ROA"],name1:[price,pe_ratio,roic,total_return,eps,roe,roa],name2:[price_P1,pe_ratioP1,roicp1,total_returnP1,epsP1,roeP1,roaP1]}
        df_basic = pd.DataFrame(basic_output)
        
    

        
        output_choice = st.selectbox( 
            "please select the data set you would like",
            ["none","All","Valuation","Growth","Efficency","REITs","Debt","Basic"]
        ) 
        col1,clo2,col3,col4,col5,col6=st.columns(6)
        if output_choice == "none":
            st.warning("Please select a data set")
        elif output_choice == "All":
            col1,clo2,col3,col4,col5,col6=st.columns(6)
            with col3:
                st.write("Valuation Data")
            st.dataframe(df_valuation.head(1000))
            col1,clo2,col3,col4,col5,col6=st.columns(6)
            with col3:
                st.write("Growth Data")
            st.dataframe(df_growth.head(1000))
            col1,clo2,col3,col4,col5,col6=st.columns(6)
            with col3:
                st.write("Efficency Data")
            st.dataframe(df_efficency.head(1000))
            col1,clo2,col3,col4,col5,col6=st.columns(6)
            with col3:
                st.write("REITs Data")
            st.dataframe(df_reit.head(1000))
            col1,clo2,col3,col4,col5,col6=st.columns(6)
            with col3:
                st.write("Debt Data")
            st.dataframe(df_debt.head(1000))
        elif output_choice == "Valuation":
            with col3:
                st.write("Valuation Data")
            st.dataframe(df_valuation.head(1000))

        elif output_choice == "Growth":
            with col3:
                st.write("Growth Data")
            st.dataframe(df_growth.head(1000))

        elif output_choice == "Efficency":
            with col3:
                st.write("Efficency Data")
            st.dataframe(df_efficency.head(1000))

        elif output_choice == "REITs":
            with col3:
                st.write("REITs Data")
            st.dataframe(df_reit.head(1000))

        elif output_choice == "Debt":
            with col3:
                st.write("Debt Data")
            st.dataframe(df_debt.head(1000))



        elif output_choice == "Basic":
            with col3:
                st.write("Basic Data")
            st.dataframe(df_basic.head(1000))





        statement_sheet = st.button("click here to see financial statements", key="show_statements")

        if statement_sheet:
            with st.expander("Financial Statements", expanded=True):
                st.write("Income Statement")
                st.dataframe(financial.head(1000))
                st.write("Balance Sheet")
                st.dataframe(balance.head(1000))
                st.write("Cash Flow Statement")
                st.dataframe(cashflow.head(1000))

elif model_selection == "Technical Data":
    st.subheader("Technical Data ")
    nation = st.selectbox(
    "select a stock market", options=["Saudi Arabia","United States"], index=None
    )
    if nation is None:
        st.info("Please select a stock market")
        st.stop()



    if nation == "Saudi Arabia":
        stock = st.text_input("Please insert Ticker",help="For example 2222 for Saudi Aramco")
        if not stock.upper().endswith(".SR"):
            stock = stock + ".SR"
    if nation == "United States":
        stock = st.text_input("Please insert Ticker",help="For example MSFT for Microsoft")
        stock = stock
        if stock == "Taj":
            st.info("why is Saj in the taj mahal")
            st.stop()
        elif stock == "taj":
            st.info("my bad :(")
            st.stop()
    if stock == "":
        st.stop()

    if stock is None:
        st.warning("Please select a stock")
        st.stop()



    stock= yf.Ticker(stock)
    data = stock.history("1y")
    name = stock.info.get("longName")

    if name is None:
        st.warning("Please select a stock")
        st.stop()
    st.write(name + ": Has been selected")

    length = st.selectbox(
    "Select Data Length ", options=["1","2","3","4","5"],help="length of data set in years", index=None
    )
    if length is None:
        st.warning("Please select length")
        st.stop()

    if length is None:
        st.warning("Please select a length")
        st.stop()
    length = str(length) + "y"
    data = stock.history(length)


    data = data.reset_index()
    data["Date"] = pd.to_datetime(data["Date"]).dt.date
    data = data[["Date","Close","High","Low","Volume"]]
    data = data.set_index("Date")
    close = data["Close"]





    data["ma20"] = data["Close"].rolling(20).mean()
    data["ma50"] = data["Close"].rolling(50).mean()

    data["returns"] = np.log(close/close.shift(1))
    returns_table = data[["returns"]]
    cumulative_returns = np.cumsum(returns_table)
    ma_table = data[["Close","ma20","ma50"]]
    price_table = data["Close"]



    candlestick_data = stock.history(length,auto_adjust=False)
    candlestick_data = candlestick_data.dropna(subset=['Open', 'High', 'Low', 'Close'])
    candlestick_data.columns = candlestick_data.columns.get_level_values(0)
    candlestick_recent = candlestick_data.tail(60)
    candlestick_graph, axlist = mpf.plot(candlestick_recent,type='candle',style='charles',title=f"{name} Candlestick Graph",ylabel='Price',volume=True,returnfig=True)


    technical_final = st.selectbox("select output would like to see",
    options=["All","Candlestick Graph","Moving Average graph","Cumulative Returns Graph","Closing Price Graph","Moving Average Data","Cumulative Returns Data"],index=None)

        

    if technical_final == "Candlestick Graph":
        with st.expander("Candlestick Graph", expanded=True):
            st.pyplot(candlestick_graph)
    elif technical_final == "Moving Average graph":
        with st.expander("Moving Average Graph", expanded=True):
            st.line_chart(ma_table)
    elif technical_final == "Cumulative Returns Graph":
        with st.expander("Cumulative Returns Graph", expanded=True):
            st.line_chart(cumulative_returns)
    elif technical_final == "Closing Price Graph":
        with st.expander("Closing Price Graph", expanded=True):
            st.line_chart(price_table)
    elif technical_final == "Moving Average Data":
        with st.expander("Moving Average Data", expanded=True):
            st.dataframe(ma_table.head(2000))
    elif technical_final == "Cumulative Returns Data":
        with st.expander("Returns Data", expanded=True):
            st.dataframe(cumulative_returns.head(2000))
    elif technical_final == "All":
        with st.expander("All",expanded=True):
            st.subheader("Candlestick Graph")
            st.write()
            st.pyplot(candlestick_graph)
            st.write()
            st.subheader("Moving Average Graph")
            st.write()
            st.line_chart(ma_table)
            st.write()
            st.subheader("Cumulative Returns Graph")
            st.write()
            st.line_chart(cumulative_returns)
            st.write()
            st.subheader("Closing Price Graph")
            st.write()
            st.line_chart(price_table)
            st.write()
            st.subheader("Moving Average Data")
            st.write()
            st.dataframe(ma_table.head(2000))
            st.write()
            st.subheader("Returns Data")
            st.write()
            st.dataframe(cumulative_returns.head(2000))
            





        
    else:
        st.info("please make your choice")
        st.stop()


else:
    st.info("Please select a model")