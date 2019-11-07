from heptrkx import master
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from pandas import DataFrame



df = pd.read_csv('ParticleData.csv', parse_dates=True)
print(df.head())

ypos, ypos, zpos = df.vx, df.vy, df.vz
xmomentum, ymomentum, zmomentum = df.px, df.py, df.pz



"""
This function groups relatively close partiles together 

"""
def kmeans(k):

    """
    1. randomly pick k points and group particles into those k buckets
    2. compute the center of mass of each bucket
    3. update the new k points as the center of mass
    4. repeat step 2 to 3
    5. if stable, finish
    6. if max_iter is reached before stabalize, exit 

    """





