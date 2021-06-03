import numpy as np
import os
import re

import pandas as pd
from scipy.optimize import curve_fit

# fit 3D Lithium ion battery dataset
# data = os.path.join(os.getcwd(), 'liibattery3d')
pathtomodule = os.path.abspath(__file__)
dirname = os.path.dirname(pathtomodule)
data = os.path.join(dirname, 'data')


def fitliib3d():
    '''
    A curve fitting procedure to determine the discharge
    rate constant, the n factor for the discharge rate,
    and the specific capacity. We use the model outlined
    by *R. Tian & S. Park et. al.*
    https://www.nature.com/articles/s41467-019-09792-9
    Here we fit all dataset in this package, and the we
    write the output of the optimized fit parameters, for
    each dataset, in a csv file
    '''
    # load dataset
    filepath = os.path.join(data, "liibattery3d_performancelog.xls")
    dframe = pd.read_excel(filepath, sheet_name='3_CapacityRate',
                           header=[0, 1, 2])

    # Fit procedure
    # define list of fit parameters and of their standard deviations
    taus = []
    sigma_taus = []
    ns = []
    sigma_ns = []
    specificQs = []
    sigma_Qs = []
    numdataset = range(int(len(dframe.columns) / 2))
    # fit dataset
    for i in numdataset:
        # import xdata and ydata from dataframe
        xdata = dframe.iloc[:, (2 * i)].values[0:]
        ydata = dframe.iloc[:, ((2 * i) + 1)].values[0:]
        # discard null datapoints
        # and define input and output of fit function
        Rdischarge = xdata[~pd.isnull(xdata)]
        normQ = ydata[~pd.isnull(ydata)]
        # fit dataset with more than four datapoints
        # otherwise, discard
        if len(Rdischarge) >= 4:
            # parameters
            tau = 0.5
            n = 1
            specificQ = 100
            params0 = [tau, n, specificQ]  # intial guess parameter
            popt, pcov = fit(params0, xdata=Rdischarge, ydata=normQ)
            tau, n, specificQ = popt
            # standard deviation
            sigma_tau, sigma_n, sigma_Q = np.sqrt(np.diag(pcov))
        else:
            tau = 0
            n = 0
            specificQ = 0
            sigma_tau, sigma_n, sigma_Q = [0, 0, 0]
        # append optimized fit parameters to list
        taus.append(tau)
        ns.append(n)
        specificQs.append(specificQ)
        # append standard deviation of
        # error margin on fit parameters to list
        sigma_taus.append(sigma_tau)
        sigma_ns.append(sigma_n)
        sigma_Qs.append(sigma_Q)

    # Structure the optimized parameters into a dataframe
    # Define all column names of dataset from original dataframe
    colnames = list(dframe.columns)[1::2]
    # Turn the tuples if column names into lists
    for index, element in enumerate(colnames):
        colnames[index] = list(element[:-1])
        for subindex, string in enumerate(colnames[index]):
            # conserve numbers only
            colnames[index][subindex] = int(re.findall(r'\d+', string)[0])
        colnames[index] = tuple(colnames[index])
    # insert optimized parameters into dataframe
    popt_dframe = pd.DataFrame(columns=['Paper #', 'Set',
        'tau', 'n', 'Q',
        'sigma_tau', 'sigma_n', 'sigma_Q'])
    # Input paper, set numbers, optimized parameters and
    # their error margins into dataframe
    for index, element in enumerate(colnames):
        row = [int(element[0]),
               int(element[1]),
               taus[index],
               ns[index],
               specificQs[index],
               sigma_taus[index],
               sigma_ns[index],
               sigma_Qs[index]
               ]
        row_series = pd.Series(row, index=popt_dframe.columns)
        popt_dframe = popt_dframe.append(row_series, ignore_index=True)

    # Write dataframe of optimized parameters to csv file
    outputpath = os.path.join(data, "fitparametersliib3d.csv")
    popt_dframe.to_csv(path_or_buf=outputpath, index=False)
    return

# define fit procedure


def fit(params0, **kwargs):
    '''
    A curve fitting procedure to determine the discharge
    rate constant, the n factor for the discharge rate,
    and the specific capacity. We use the model outlined
    by *R. Tian & S. Park et. al.*
    https://www.nature.com/articles/s41467-019-09792-9
    Input Arguments
    params0: 1 by 3 numpy array, with elemets, tau (the
    characteristic lifetime), n (the rate discharge coef-
    ficient), and Q the specific capacity
    Keyword Arguments
    xdata: 1D numpy array, default as 'Rdischarge'
    ydata: 1D numpy array, default as normQ
    filename: string, filepath
        (csv format) first column is xdata, second, ydata
    Output Argument
    Return the optimized parameters tau, n, specificQ
    '''
    # import data
    if 'xdata' in kwargs:
        Rdischarge = kwargs['xdata']
        normQ = kwargs['ydata']
    elif 'filename' in kwargs:
        filepath = kwargs['filename']
        dframe = pd.read_csv(filepath)
        Rdischarge = dframe.iloc[:, 0].to_numpy()
        normQ = dframe.iloc[:, 1].to_numpy()

    # Fit procedure
    popt, pcov = curve_fit(fitfunc, Rdischarge, normQ, p0=params0)
    return popt, pcov

# define fit function


def fitfunc(Rdischarge, tau, n, specificQ):
    '''
    Capacity versus rate discharge model outlined by
    https://www.nature.com/articles/s41467-019-09792-9
    '''
    normQ = specificQ * (1 -
                         (Rdischarge * tau)**n *
                         (1 - np.exp(- (Rdischarge * tau)**(- n)))
                         )
    return normQ
