import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

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
            leaders.append(leader_field.split(':')[1][1:])
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
print("1_2: ", str(100*len(data_1_2)/sum_elections))
print("2_3: ", str(100*len(data_2_3)/sum_elections))
print("3_4: ", str(100*len(data_3_4)/sum_elections))
print("4_5: ", str(100*len(data_4_5)/sum_elections))
print("5_6: ", str(100*len(data_5_6)/sum_elections))
print("6_7: ", str(100*len(data_6_7)/sum_elections))
print("7_8: ", str(100*len(data_7_8)/sum_elections))

data = times

# Plot histogram of all data.
plt.figure(1)
plt.hist(data, bins=500, density=True, stacked=True)

# Fit a normal distribution to the data:
plt.figure(2)

mu, std = norm.fit(data_1_2)
data_1_2 = np.random.normal(mu, std, 1000)

plt.hist(data_1_2, bins=25, density=True, stacked=True, alpha=0.6)

# Plot the PDF.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

plt.plot(x, p, 'k', linewidth=2)

title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
plt.title(title)

plt.show()
