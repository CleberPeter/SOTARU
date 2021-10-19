import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt

leaders = []
times = []

data_1_2 = []

with open('ideal_network.txt') as file:
        for line in file:
            fields = line.split(',')
            leader_field = fields[0]
            time_field = fields[1]

            time = float(time_field.split(':')[1][1:-1])

            leaders.append(leader_field.split(':')[1][1:])
            times.append(time)

            if time >= 1000 and time <= 2000:
                data_1_2.append(time)

data = times

# Plot histogram of all data.
plt.figure(1)
plt.hist(data, bins=500, density=True, stacked=True)

# Fit a normal distribution to the data:
plt.figure(2)
mu, std = norm.fit(data_1_2)

plt.hist(data_1_2, bins=25, density=True, stacked=True, alpha=0.6)

# Plot the PDF.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)

plt.plot(x, p, 'k', linewidth=2)

title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
plt.title(title)


plt.show()
