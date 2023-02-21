from numpy import nan
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.stats import linregress

def sketch(dset, column):

    bond_list = dset
    x_data = []
    y_data = []
    for i, row in bond_list.iterrows():
        try:
            y = row[column]
            y = float(y)
            y_data += [y]

            bond_code = row['ASX_code']
            x_data += [bond_code]
        except AttributeError:
            pass 

    # column plot
    plt.title(f'{column} for Aussie Bonds')
    plt.xlabel('Treasury Bonds')
    plt.ylabel(f'{column}')

    # regression plot
    x_data_time = []
    for b_code in x_data:
        # time to maturity
        maturity = bond_list.loc[bond_list['ASX_code'] == b_code, 'maturity'].iloc[0]
        try:
            maturity = datetime.strptime(maturity, '%d-%b-%Y')
        except ValueError:
            maturity = datetime.strptime(maturity, '%d %B %Y')
        time = (maturity - datetime.now()).days / 365.2522 # in years
        time = int(time) # to the nearest integer

        x_data_time += [time]

    regr_line = linregress(x=x_data_time, y=y_data)
    slope = regr_line.slope
    intercept = regr_line.intercept

    regr_vals = [
        slope*x + intercept for x in x_data_time
    ]
    plt.plot(x_data_time, y_data)
    plt.plot(x_data_time, regr_vals, '--', label=f'Regr. slope = {round(slope,4)}')

    plt.xticks(x_data_time, x_data, rotation=70)

    plt.legend()
    plt.show()
    return

def sketch_multiple(dset, columns): # pass columns to sketch in dset as list of strings

    bond_list = dset
    x_data = []

    ydatas = []
    for column in columns:
        y_data = []
        for i, row in bond_list.iterrows():
            try:
                y = row[column]
                y = float(y)
                y_data += [y]

                bond_code = row['ASX_code']
                if bond_code not in x_data:
                    x_data += [bond_code]
            except AttributeError:
                pass 
        ydatas += [y_data]

    x_data_time = []
    for b_code in x_data:
        # time to maturity
        maturity = bond_list.loc[bond_list['ASX_code'] == b_code, 'maturity'].iloc[0]
        try:
            maturity = datetime.strptime(maturity, '%d-%b-%Y')
        except ValueError:
            maturity = datetime.strptime(maturity, '%d %B %Y')
        time = (maturity - datetime.now()).days / 365.2522 # in years
        time = int(time) # to the nearest integer

        x_data_time += [time]

    plt.title('Aussie bonds')
    plt.xlabel('Treasury Bonds')
    plt.ylabel('metrics')

    for ydata in ydatas:
        lbl = columns[ydatas.index(ydata)]
        plt.plot(x_data_time, ydata, label=lbl)

    plt.xticks(x_data_time, x_data, rotation=70)

    plt.legend()
    plt.show()
    return

