import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import scipy.stats as ss

leaders = []
times = []

data_1_2 = []
data_2_3 = []
data_3_4 = []
data_4_5 = []
data_5_6 = []
data_6_7 = []
data_7_8 = []
data_8_9 = []

with open('ideal_network.txt') as file:
    for line in file:
        fields = line.split(',')
        leader_field = fields[0]
        time_field = fields[1]

        time = float(time_field.split(':')[1][1:-1])
        
        if time < 9000:
            leader = leader_field.split(':')[1][1:]
            leaders.append(int(leader[1:]))
            times.append(time)

            if time >= 1000 and time <= 2000:
                data_1_2.append(time)
            elif time >= 2000 and time <= 3000:
                data_2_3.append(time)
            elif time >= 3000 and time <= 4000:
                data_3_4.append(time)
            elif time >= 4000 and time <= 5000:
                data_4_5.append(time)
            elif time >= 5000 and time <= 6000:
                data_5_6.append(time)
            elif time >= 6000 and time <= 7000:
                data_6_7.append(time)
            elif time >= 7000 and time <= 8000:
                data_7_8.append(time)
            elif time >= 8000 and time <= 9000:
                data_8_9.append(time)

sum_elections = len(data_1_2) + len(data_2_3) + len(data_3_4) + len(data_4_5) + len(data_5_6) + len(data_6_7) + len(data_7_8) + len(data_8_9)
len_data_1_2 = 100*len(data_1_2)/sum_elections
len_data_2_3 = 100*len(data_2_3)/sum_elections
len_data_3_4 = 100*len(data_3_4)/sum_elections
len_data_4_5 = 100*len(data_4_5)/sum_elections
len_data_5_6 = 100*len(data_5_6)/sum_elections
len_data_6_7 = 100*len(data_6_7)/sum_elections
len_data_7_8 = 100*len(data_7_8)/sum_elections

data = times

##############################################
"""plt.figure(1)

plt.ylabel('frequency')
plt.xlabel('miliseconds')
plt.hist(data, bins=500)"""

##############################################
"""plt.figure(2)

mu, std = norm.fit(data_1_2)
data = np.random.normal(mu, std, 1000)

plt.hist(data, bins=25, density=True, stacked=True, alpha=0.6)

xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

plt.plot(x, p, 'k', linewidth=2)

title = "avg = %.2fs,  std = %.2fs" % (mu, std)
plt.xlabel('miliseconds')
plt.title(title)"""

##############################################
"""labels = ['1 Votação', '2 Votações', '3 Votações', '4 Votações', '5 Votações', '6 Votações', '7 Votações']
sizes = [len_data_1_2, len_data_2_3, len_data_3_4, len_data_4_5, len_data_5_6, len_data_6_7, len_data_7_8]

print(sizes)"""


##############################################
"""plt.figure(4)
plt.xlim([1, 32])
bins = np.arange(1, 32, 1) # fixed bin size
plt.xlabel('server')
plt.ylabel('frequency')
out = plt.hist(leaders, bins=bins)

x = np.linspace(0, 32, 1000)
y = 145*np.exp(-0.15*x)/np.exp(-0.15)
print(y)
plt.plot(x,y)"""
##############################################
"""plt.figure(5)
plt.xlim([1, 32])
data = np.random.randint(1, 33, 1000)
bins = np.arange(1, 34, 1) # fixed bin size
plt.hist(data, bins=bins)
plt.xlabel('server')
plt.ylabel('frequency')
"""

plt.show()