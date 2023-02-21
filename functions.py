from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
from objects import Bond
from numpy import nan
from tabula import convert_into

def etbList_AU():
    url = 'https://www.australiangovernmentbonds.gov.au/bond-types/exchange-traded-treasury-bonds/list-etbs'
    r = requests.get(url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'lxml')
    bond_list = soup.find_all(
        'td'
    )
    cols = [
        'maturity',
        'coupon',
        'ASX_code',
        'payDates'
    ]
    df = pd.DataFrame(columns=cols)
    curr_stack = []
    for i, item in enumerate(bond_list):
        to_append = item.text
        to_append = to_append.replace('\n', '')
        curr_stack += [to_append]
        if i % 4 == 3:
            pd_row = pd.DataFrame([curr_stack], columns=cols)
            df = pd.concat([df, pd_row])
            curr_stack = []
    df = df.reset_index(drop=True)
    return df

def etbList_AU_dataset():

    bond_list = etbList_AU()

    yields = []
    values = []
    value_ylds = []
    roi = []

    for i, row in bond_list.iterrows():
        code = row['ASX_code']
        fv = 100

        coupon = row['coupon'].replace('%', '')
        coupon = float(coupon)/100
        coupon = coupon/2.0 # paid each half-year period

        maturity = row['maturity']
        maturity = datetime.strptime(maturity, '%d-%b-%Y')
        time = (maturity - datetime.now()).days / 365.2522
        time = int(2*time) + 1 # number of half-year periods

        yf_bond_code = code + '.AX'
        bond_url = f'https://au.finance.yahoo.com/quote/{yf_bond_code}'
        bond_get = requests.get(bond_url, headers={'User-Agent': 'Custom'})
        bond_soup = BeautifulSoup(bond_get.text, 'lxml')
        try:
            bond_price = bond_soup.find_all( 
                'fin-streamer', {'class':'Fw(b) Fz(36px) Mb(-4px) D(ib)'}
            )[0].text
            bond_price = float(bond_price)

            # BOND OBJECT
            bond = Bond(
                face=fv, 
                price=bond_price,
                coupon=coupon,
                time=time
            )  

            # BOND YLD
            yld = bond.yld()
            yld = 2 * yld
            yld = round(100*yld, 2)
            # yld = str(yld) + '%'  

            # VALUE
            val = bond.value()
            val = round(2*val/time, 2) # annualised

            # VALUE YLD
            val_yld = bond.value_yield()
            val_yld = 2*round(val_yld*100, 2) # doubled to annualize
            # val_yld = str(val_yld) + '%'       

            # RETURN ON 1000
            roi_1000 = (1000 // bond_price) * val

            values += [val]
            value_ylds += [val_yld]
            yields += [yld]
            roi += [roi_1000]

        except IndexError:
            values += [nan]
            value_ylds += [nan]
            yields += [nan]
            roi += [nan]

    new_df_col = pd.DataFrame({
        'bond_yield (%/yr)': yields,
        'bond_value (AUD/yr)': values, 
        'bond_value_yield (%/yr)' : value_ylds, 
        'net_return_on_1000 (AUD)' : roi
        })
    new_df = bond_list.reset_index(drop=True).join(new_df_col.reset_index(drop=True), how='left')

    return new_df

def etibList_AU():
    url = "https://www.australiangovernmentbonds.gov.au/bond-types/exchange-traded-treasury-indexed-bonds/list-etibs"
    r = requests.get(url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'lxml')
    bond_list = soup.find_all(
        'td'
    )
    cols = [
        'maturity',
        'coupon',
        'ASX_code',
        'payDates'
    ]
    df = pd.DataFrame(columns=cols)
    curr_stack = []
    for i, item in enumerate(bond_list):
        to_append = item.text
        to_append = to_append.replace('\n', '')
        curr_stack += [to_append]
        if i % 4 == 3:
            pd_row = pd.DataFrame([curr_stack], columns=cols)
            df = pd.concat([df, pd_row])
            curr_stack = []
    df = df.reset_index(drop=True)
    return df

def etibList_AU_dataset():
    etib_list = etibList_AU() 
    """
    CPI estimate
    """
    cpi_url = "https://www.rba.gov.au/"
    r = requests.get(cpi_url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'lxml')
    cpi = soup.find_all(
        'p', {'class': 'value'}
    )

    cpi_curr = cpi[1].text.replace('%', '')
    cpi_curr = float(cpi_curr)/100 # annualised

    cpi_mthly_forward = cpi[2].text.replace('%', '')
    cpi_mthly_forward = float(cpi_mthly_forward)/100 # annualised
    """
    scrape table of current face-values from pdf
    """
    etib_url = "https://www.australiangovernmentbonds.gov.au/bond-types/exchange-traded-treasury-indexed-bonds/list-etibs"
    r = requests.get(etib_url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'lxml')
    uuids = [
        "1f86d089-31aa-44ce-856a-72fad9d464bc",
        "52b6e547-1dd1-461f-aa29-3b5bedbaebd9",
        "162b43af-3f00-48d3-a2e2-8dc3dc4601c5",
        "fc879ae5-efb3-48a5-97b5-446a25c75ef7"
    ]
    fv_links = []
    for uuid in uuids:
        fv_links += soup.find_all(
            'a', {'data-entity-uuid': uuid} 
        )
    fv_pdf_url = fv_links[-1].get('href')
    fv_df = convert_into(fv_pdf_url, "dumps/fvs.csv", output_format='csv', pages='all')
    fv_df = pd.read_csv("dumps/fvs.csv")
    fv_col = "Nominal Value for"

    df_rows = {
        'face_value (AUD)': [],
        'curr_yld (%/yr)': [],
        'infl_spread (%/yr)': [],
        'value_at_cpi (AUD/yr)': [],
        'value_yld_cpi (%/yr)': [],
        'value_at_cpi_fwd (AUD/yr)': [],
        'value_yld_cpi_fwd (%/yr)': [],
        'fwd_face_value (AUD)': []
    }

    for i, row in etib_list.iterrows():
        code = row['ASX_code']
        fv = fv_df[fv_df['ASX'] == code].iloc[0][fv_col]
        fv = float(fv)

        coupon = row['coupon'].replace('%', '')
        coupon = float(coupon)/100
        coupon = coupon/4.0 # paid quarterly

        maturity = row['maturity']
        maturity = datetime.strptime(maturity, '%d %B %Y')
        time = (maturity - datetime.now()).days / 365.2522
        time = int(4*time) + 1 # number of quarter-year periods

        yf_bond_code = code + '.AX'
        bond_url = f'https://au.finance.yahoo.com/quote/{yf_bond_code}'
        bond_get = requests.get(bond_url, headers={'User-Agent': 'Custom'})
        bond_soup = BeautifulSoup(bond_get.text, 'lxml')
        try:
            bond_price = bond_soup.find_all( 
                'fin-streamer', {'class':'Fw(b) Fz(36px) Mb(-4px) D(ib)'}
            )[0].text
            bond_price = float(bond_price)

            # BOND OBJECT
            bond = Bond(
                fv,
                bond_price,
                coupon,
                time
            )

            curr_fv = bond.fv 

            curr_yld = bond.yld()
            curr_yld = round(100*curr_yld*4, 2) # annualised

            infl_sprd = bond.infl_sprd()
            infl_sprd = round(100*infl_sprd, 2)

            cpi_value = bond.value_ip(cpi_curr/4)
            cpi_value = round(4*cpi_value/time, 2) # annualised
            cpi_value_yld = bond.value_ip_yld(cpi_curr/4) # annual cpi expressed quarterly
            cpi_value_yld = round(100*cpi_value_yld*4, 2) # annualised

            cpi_fwd_val = bond.value_ip(cpi_mthly_forward/4)
            cpi_fwd_val = round(4*cpi_fwd_val/time, 2) # annualised
            cpi_frwrd = bond.value_ip_yld(cpi_mthly_forward/4) # annual cpi_forward expressed quarterly
            cpi_frwrd = round(100*cpi_frwrd*4, 2) # annualised

            forward_fv = curr_fv * (1 + (cpi_frwrd/4)/100)
            forward_fv = round(forward_fv, 2)

            df_rows['face_value (AUD)'] += [curr_fv]
            df_rows['curr_yld (%/yr)'] += [curr_yld]
            df_rows['infl_spread (%/yr)'] += [infl_sprd]

            df_rows['value_at_cpi (AUD/yr)'] += [cpi_value]
            df_rows['value_yld_cpi (%/yr)'] += [cpi_value_yld]

            df_rows['value_at_cpi_fwd (AUD/yr)'] += [cpi_fwd_val]
            df_rows['value_yld_cpi_fwd (%/yr)'] += [cpi_frwrd]
            df_rows['fwd_face_value (AUD)'] += [forward_fv]

        except IndexError:
            for key in df_rows:
                df_rows[key] += [nan]

    new_df = pd.DataFrame(df_rows)
    new_df = etib_list.reset_index(drop=True).join(new_df.reset_index(drop=True), how='left')

    return new_df

# pass list of ANNUALISED lifetime inflation values (list of nums)
def etib_forcasting(lifetime_inflations):
    etib_list = etibList_AU() 
    etib_list = etib_list.drop('payDates', axis=1)
    """
    scrape table of current face-values from pdf
    """
    etib_url = "https://www.australiangovernmentbonds.gov.au/bond-types/exchange-traded-treasury-indexed-bonds/list-etibs"
    r = requests.get(etib_url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(r.text, 'lxml')
    uuids = [
        "1f86d089-31aa-44ce-856a-72fad9d464bc",
        "52b6e547-1dd1-461f-aa29-3b5bedbaebd9",
        "162b43af-3f00-48d3-a2e2-8dc3dc4601c5",
        "fc879ae5-efb3-48a5-97b5-446a25c75ef7"
    ]
    fv_links = []
    for uuid in uuids:
        fv_links += soup.find_all(
            'a', {'data-entity-uuid': uuid} 
        )
    fv_pdf_url = fv_links[-1].get('href')
    fv_df = convert_into(fv_pdf_url, "dumps/fvs.csv", output_format='csv', pages='all')
    fv_df = pd.read_csv("dumps/fvs.csv")
    fv_col = "Nominal Value for"

    df_rows = {}
    for infl in lifetime_inflations:
        df_rows[f"value_at_{infl} (AUD/yr)"] = []
        df_rows[f"value_yld_at_{infl} (%/yr)"] = []

    for i, row in etib_list.iterrows():
        code = row['ASX_code']
        fv = fv_df[fv_df['ASX'] == code].iloc[0][fv_col]
        fv = float(fv)

        coupon = row['coupon'].replace('%', '')
        coupon = float(coupon)/100
        coupon = coupon/4.0 # paid quarterly

        maturity = row['maturity']
        maturity = datetime.strptime(maturity, '%d %B %Y')
        time = (maturity - datetime.now()).days / 365.2522
        time = int(4*time) + 1 # number of quarter-year periods

        yf_bond_code = code + '.AX'
        bond_url = f'https://au.finance.yahoo.com/quote/{yf_bond_code}'
        bond_get = requests.get(bond_url, headers={'User-Agent': 'Custom'})
        bond_soup = BeautifulSoup(bond_get.text, 'lxml')
        try:
            bond_price = bond_soup.find_all( 
                'fin-streamer', {'class':'Fw(b) Fz(36px) Mb(-4px) D(ib)'}
            )[0].text
            bond_price = float(bond_price)

            # BOND OBJECT
            bond = Bond(
                fv,
                bond_price,
                coupon,
                time
            )

            for infl in lifetime_inflations:
                col1 = f"value_at_{infl} (AUD/yr)"
                col2 = f"value_yld_at_{infl} (%/yr)"
                lifetime_infl = (infl/4)/100 # expressed quarterly

                val = bond.value_ip(lifetime_infl)
                val = round(4*val/time, 2)

                val_yld = bond.value_ip_yld(lifetime_infl)
                val_yld = round(100*val_yld*4, 2) # annualised

                df_rows[col1] += [val]
                df_rows[col2] += [val_yld]

        except IndexError:
            for key in df_rows:
                df_rows[key] += [nan]

    new_df = pd.DataFrame(df_rows)
    new_df = etib_list.reset_index(drop=True).join(new_df.reset_index(drop=True), how='left')

    return new_df

