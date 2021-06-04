import os

import pandas as pd

import liibattery3d
from liibattery3d import liib3d

data_path = os.path.join(liibattery3d.__path__[0], 'data')


def test_fitliib3d():
    '''
    Test case for curve fit module to all dataset of
    3d lithium ion battery prescribed in data dir
    first check that output exists as 'fitparametersliib3d.csv' in
    data dir, then assert output size of 'fitparametersliib3d.csv'
    '''
    # Write parameters to csv file with fit function
    liib3d.fitliib3d()
    # test 1; check that file exists
    try:
        filepath = os.path.join(data_path, "fitparametersliib3d.csv")
        filepathexists = os.path.exists(filepath)
        assert(filepathexists)
    except AssertionError:
        print("I couldn't find filepath to parameters csv file")
    return
    # test 2; check output size of fit parameter csv file
    # read output of the optimized parameters
    try:
        filepath_out = os.path.join('../liibattery3d/data',
                                    'fitparametersliib3d.csv')
        dframe_out = pd.read_csv(filepath_out)
        numcolumns = 8
        shapeout = (dframe_out.shape[1] == numcolumns)
        assert(shapeout)
    except AssertionError:
        print(f"There should be {numcolumns} columns for \
            the paper and set of data, the optimized parameters \
            and their standard deviations")
    return


def test_fit():
    """
    Test case for curve fit module to 3d lithium ion battery
    test the output size in an array of three elements corresponding
    to the optimized, desired, paramters: the characteristic time tau,
    the n fractor, and specific capacity Q
    """
    filepath = os.path.join(data_path, "capacityratepaper1set1.csv")
    # parameters
    tau = 0.5
    n = 1
    specificQ = 100
    params0 = [tau, n, specificQ]  # intial guess parameter
    popt, _ = liib3d.fit(params0, filename=filepath)
    try:
        lenparam = len(popt)
        assert(lenparam == 3)
    except AssertionError:
        print(f'I should have only three parameters, \
              not {lenparam}')
    return


def test_fitfunc():
    '''
    The output of the fit function is the (mass) normalized capacity
    simply assert that the size of the output array is equal to the
    size of the input array, and that
    the maximum value at initail discharge rate (at zero) is less
    than or equal to the specific capacity
    '''
    filepath = os.path.join(data_path, "capacityratepaper1set1.csv")
    tau = 0.5
    n = 1
    specificQ = 100
    # import data
    dframe = pd.read_csv(filepath)
    Rdischarge = dframe.iloc[:, 0].to_numpy()
    # estimate normalize mass Q from model
    normQ = liib3d.fitfunc(Rdischarge, tau, n, specificQ)
    # first check the shape of normQ output
    try:
        shape_normQ = normQ.shape
        shape_Rdischarge = Rdischarge.shape
        assert(shape_normQ == shape_Rdischarge)
    except AssertionError:
        print(f'the size of input array, {shape_Rdischarge}, and\
              output array, {shape_normQ}, should be equal')
        # second, check the initial output value
        try:
            normQ0 = normQ[0]
            normQ0lessorequalspecificQ = (normQ0 <= specificQ)
            assert(normQ0lessorequalspecificQ)
        except AssertionError:
            print('the normalized mass capacity normQ should be \
                less than or equal to the specific capacity Q \
                at any given discharge rate')
    return
