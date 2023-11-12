# libraries
import numpy as np
import matplotlib.pyplot as plt
 
# width of the bars
barWidth = 0.3
 
# Choose the height of the blue bars
bars1 = [10]
 
# Choose the height of the cyan bars
bars2 = [10]
 
# Choose the height of the cyan bars
bars3 = [5.885]
 
# Choose the height of the error bars (bars1)
yer1 = [0]
 
# Choose the height of the error bars (bars2)
yer2 = [0]

# Choose the height of the error bars (bars2)
yer3 = [11.10]
 
# The x position of bars
r1 = np.arange(len(bars1))
r2 = [x + barWidth for x in r1]
r3 = [x + barWidth for x in r2]
 
# Create blue bars
plt.bar(r1, bars1, width = barWidth, color = 'blue', edgecolor = 'black', yerr=yer1, capsize=7, label='ideafix')
 
# Create cyan bars
plt.bar(r2, bars2, width = barWidth, color = 'cyan', edgecolor = 'black', yerr=yer2, capsize=7, label='hashpipe')
 
# Create cyan bars
plt.bar(r3, bars3, width = barWidth, color = 'red', edgecolor = 'black', yerr=yer3, capsize=7, label='smash') 

# general layout
plt.xticks([r + barWidth for r in range(len(bars1))], [''])
plt.ylabel('Size in MBs')
plt.legend()
 
# Show graphic
plt.show()
