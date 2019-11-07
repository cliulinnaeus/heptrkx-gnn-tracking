from heptkx import master
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from pandas import DataFrame


dir = '../sample_data'
evtid = 21000


event = master.Event(dir, 21000)
event.read(evtid)    # data is loaded into event obj

event.particles.to_csv("ParticleData.csv")

df = pd.read_csv('ParticleData.csv', parse_dates=True)
print(df.head())


threedee = plt.figure().gca(projection='3d')
threedee.scatter(df.vx, df.vy, df.vz)
threedee.set_xlabel('vx')
threedee.set_ylabel('vy')
threedee.set_zlabel('vz')
plt.show()
