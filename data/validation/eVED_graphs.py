import matplotlib.pyplot as plt

from data.validation.eVED_analysis import getVehStats, getTripStats, getTripsWeeklyDistr

vehStats = getVehStats()
tripStats = getTripStats()
tripsPerWeek = getTripsWeeklyDistr()

# Graphs

# Shows the number of unique trips recorded for each electric vehicle.
# The x-axis represents the vehicle identifier, while the y-axis indicates
# how many distinct trips were collected for that vehicle in the dataset.
TPVfigure, TPVaxis = plt.subplots(figsize=(14, 6))
TPVaxis.bar(vehStats["VehId"].astype(str), vehStats["tripCount"])
ticks = TPVaxis.get_xticks()
labels = [label.get_text() for label in TPVaxis.get_xticklabels()]
TPVaxis.set_xticks(ticks[::5])
TPVaxis.set_xticklabels(labels[::5], rotation=45)
plt.xlabel("Vehicle")
plt.ylabel("Number of Trips")
plt.title("Trips per Vehicle")
plt.show()

# Shows the temporal distribution of trips across the weeks covered by the dataset.
# Each point represents a week and the corresponding number of unique trips
# recorded during that period, allowing the identification of variations in data availability over time.
plt.figure(figsize=(14, 6))
plt.plot(tripsPerWeek["weeks"], tripsPerWeek["tripCounts"], marker="o")
plt.xlabel("Week")
plt.ylabel("Number of Trips")
plt.title("Trips per Week")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Energy consumption values are computed by aggregating the Energy_Consumption samples belonging to the same (VehId, Trip) pair and converting the resulting value from kWh to Wh.

# Summarizes the distribution of total energy consumption per trip.
# The box represents the interquartile range (IQR), the central line is the median,
# and points outside the whiskers indicate potential outliers.
plt.boxplot(tripStats["totalEnergyConsumed"], flierprops={"markersize": 3})
plt.ylabel("Energy [Wh]")
plt.title("Total Energy Consumption per Trip")
plt.show()

# Compares the distribution of trip energy consumption among the different vehicles.
# For each vehicle, the boxplot highlights median consumption, variability,
# and potential outliers, enabling a direct comparison of energy usage patterns.
tripStats.boxplot(
    column="totalEnergyConsumed",
    by="vehId",
    flierprops={"markersize": 3}
).set_xticklabels([])
plt.xlabel("Vehicle")
plt.ylabel("Energy [Wh]")
plt.title("Total Energy Consumption per Trip by Vehicle")
plt.suptitle("")
plt.tight_layout()
plt.show()

# Shows how trip energy consumption values are distributed across the dataset.
# The x-axis represents total energy consumed during a trip, while the y-axis
# indicates the number of trips falling within each energy interval.
plt.figure(figsize=(14, 6))
plt.hist(tripStats["totalEnergyConsumed"], bins=30)
plt.xlabel("Energy [Wh]")
plt.ylabel("Number of trips")
plt.title("Distribution of Total Energy Consumption per Trip")
plt.show()
