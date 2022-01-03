from scipy import stats
from haversine import haversine

import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import datetime


def load_file():
	"""
	This function will return four dataframes. (trip, station, weather, capitalbikeshare-tripdata)
	:return: dataframe
	"""

	area_name = input('Which area do you want to analyze? (Montreal, Toronto, Washington): ')
	trips_df = pd.read_csv(f'data/{area_name}/trips.csv', delimiter=',', nrows=1000000)
	stations_df = pd.read_csv(f'data/{area_name}/stations.csv', delimiter=',')
	weather_df = pd.read_csv(f'data/{area_name}/weather.csv', delimiter=',')

	was_month = input('Which month in 2020 do you want to analyze for hypothesis 4 (During April to June in 2020, '
					  'members tend to ride a longer distance than casual riders on a trip in Washington.) ? (4, 5, 6): ')
	was_trip_dis_df = pd.read_csv(f'data/Washington/20200{was_month}-capitalbikeshare-tripdata.csv',
									delimiter=',', nrows=100000)
	us_confirmed_df = pd.read_csv(f'data/us_counties_covid19_daily.csv', delimiter=',')

	return trips_df, stations_df, weather_df, was_trip_dis_df, us_confirmed_df, was_month


def data_preprocessing(trips_df, weather_df, was_trip_dis_df):
	"""
	This function will return two modified dataframes (trip and weather).

	:param: trips_df: (dataframe) the dataframe that contains the data of trips.
	:param: weather_df: (dataframe) the dataframe that contains the data of weather conditions.
	:param: was_trip_dis_df: (dataframe) the dataframe that contains the data of capital bike share trip
	"""
	trips_df = trips_df
	trips_df['start_date']= pd.to_datetime(trips_df['start_date'])
	trips_df['end_date']= pd.to_datetime(trips_df['end_date'])

	# filter the dataframe, remove the rows that the duration is smaller than zero.
	trips_df = trips_df[trips_df['duration_sec'] > 0]

	# convert date to datetime
	weather_df['date']= pd.to_datetime(weather_df['date'])

	was_trip_dis_df = was_trip_dis_df
	# There are some rows without the data
	was_trip_dis_df = was_trip_dis_df.dropna()

	return trips_df, weather_df, was_trip_dis_df


def data_analysis(new_trips_df, new_weather_df):
	"""
	This function is used to preprocess the dataset and merge the dataframe,
	then calculate the correlation and generate discriptive statistic.

	:param: new_trips_df: (dataframe) the dataframe that contains the data of trips.
	:param: new_weather_df: (dataframe) the dataframe that contains the data of weather conditions.
	"""
	new_trips_df = new_trips_df
	new_weather_df = new_weather_df

	# Hypothesis #1: Total daily trips duration depends on weather conditions.
	# convert to pandas series date type, remove the time, and add the new column called start_date_day
	new_trips_df['start_date_day'] = new_trips_df['start_date'].dt.date
	# group by the start_date_day, and summarize the duration.
	daily_trips = new_trips_df.groupby(['start_date_day'])['duration_sec'].sum()

	# set index to the date.
	new_weather_df = new_weather_df.set_index('date')

	# merge the dataframe new_weather_df and daily_trip, and drop the rows which values are N/A.
	weather_duration_relation_df = pd.concat([new_weather_df, daily_trips], axis=1)
	weather_duration_relation_df = weather_duration_relation_df.dropna()

	# generate discriptive statistic
	dis_stat = round(weather_duration_relation_df.describe(), 2)

	# preprocess the column of yearid.
	column_name_list = weather_duration_relation_df.columns.values.tolist()
	if 'yearid' in column_name_list:
		column_name_list.remove('yearid')

	# skip the final column (duration_sec).
	column_name_list = column_name_list[0:-1]

	# for i in range(len(column_name_list)):
	# 	print(f'The correlation between {column_name_list[i]} and total daily trips duration')
	# 	print(stats.pearsonr(weather_duration_relation_df[column_name_list[i]],
    #                      	 weather_duration_relation_df['duration_sec']))

	stat = round(weather_duration_relation_df.corr(), 2)

	return column_name_list, weather_duration_relation_df, stat


def member(dataframe):
	"""
	The function is calculating how many members take bikes per day. And it will return the dataframe after calculating.
	:param dataframe:  the dataframe from load file.
	:return: dataframe after calculating how many members take bike per day.
	"""

	# tranform start date
	dataframe.groupby(['start_date']).size().reset_index()
	dataframe['start_date_date'] = pd.to_datetime(dataframe['start_date']).dt.date

	# group by date
	temp_m = dataframe.groupby(['start_date_date']).size().reset_index()
	temp_m.rename(columns={0: "d_count"}, inplace=True)

	# group by isMember and date
	memdp = dataframe.groupby(['start_date_date', 'is_member']).size().reset_index()
	memdp.rename(columns={0: "m_count"}, inplace=True)
	# print(memdp)

	# outerjoin two dataframe
	outer_join = pd.merge(temp_m, memdp, on='start_date_date', how='outer')
	outer_join['date_date'] = pd.to_datetime(outer_join['start_date_date'], format='%Y/%m/%d').dt.date
	return outer_join


def cal_percentage(dataframe):
	"""
	This function is calculating the percentage of member in total.
	:param dataframe: the dataframe with column has member count and total count
	:return: dataframe with a new column calculating the percentage
	>>> (25 / 100)* 100
	25.0
	"""

	dataframe['percentage'] = (dataframe['m_count'] / dataframe['d_count']) * 100
	return dataframe


def filter_time(dataframe,year_s, month_s, date_s, year_e, month_e, date_e):
	"""
	This function is filtering the time you need in the dataset.
	:param dataframe: the dataframe you need to filter the time
	:param year_s: integer for start year
	:param month_s: integer for start month
	:param date_s: integer for start date
	:param year_e: integer for end year
	:param month_e: integer for end month
	:param date_e: integer for end date
	:return: the dataframe finishing filter time
	"""

	df_time = dataframe[(dataframe['date_date']<= datetime.date(int(year_e), int(month_e), int(date_e)))&
						(dataframe['date_date']>= datetime.date(int(year_s), int(month_s), int(date_s)))]

	return df_time


def drop_na(dataframe):
	"""
	This function is use to drop null rows in dataframe.
	:param dataframe: the dataframe you need to drop null columns.
	:return: return dataframe after dropping null columns.
	"""
	dataframe.dropna()
	return dataframe


def count_trips(dataframe):
	"""
	This function is to count trips per day.
	:param dataframe: The dataframe you for area you want to counts how many trips happened per day.
	:return: return a new dataframe after calculating.
	"""
	dataframe['started_date'] = pd.to_datetime(dataframe['started_at']).dt.date
	dataframe_c = dataframe.groupby(['started_date']).size().reset_index()
	dataframe_c.rename(columns={0: "count"}, inplace=True)
	dataframe_c.rename(columns={"started_date": "date_date"}, inplace=True)
	return dataframe_c


def daily_cases(dataframe):
	"""
	The function is used to count how many confirmed cases happened per day.
	:param dataframe: The dataframe contain cases information about confirmed cases.
	:return: a new dataframe calculate confirmed cases per day.
	"""

	dataframe['date_date'] = pd.to_datetime(dataframe['date']).dt.date
	washington_df = dataframe.loc[dataframe['state'] == 'Washington']
	washington_date_df = washington_df.set_index('date_date')

	cases_df = washington_date_df.groupby('date_date')['cases'].sum().reset_index()
	return cases_df


def plot_bar(dataframe):
	"""
	This function is plotting the bar chart from the dataframe with filtering time data.
	:param dataframe: The dataframe use to plot
	:return: The graph of plotting
	"""

	dataframe_m = dataframe.loc[dataframe["is_member"] == 0]
	dataframe_n = dataframe.loc[dataframe["is_member"] == 1]

	plt.figure(dpi=200)
	plt.bar(dataframe_m["start_date_date"], dataframe_m["m_count"], color='green',
			width=0.5, alpha = 0.5)

	plt.bar(dataframe_n["start_date_date"], dataframe_n["m_count"], color='orange',
			width=0.5, alpha = 0.5)

	plt.xlabel("Started date", fontsize=7)
	plt.ylabel("Member Count", fontsize=7)
	plt.xticks(fontsize=5)
	plt.yticks(fontsize=7)
	plt.title("Club members take bike more often", fontsize=8)
	plt.show()


def plot_scatter(column_name_list, weather_duration_relation_df):
	"""
	This function is used to preprocess the dataset and merge the dataframe,
	then calculate the correlation and generate discriptive statistic.

	:param: column_name_list: (list) the list that contains the column names of weather conditions.
	:param: weather_duration_relation_df: (dataframe) the dataframe that contains the data of weather conditions and
	total daily duration.
	"""

	column_name_list = column_name_list
	weather_duration_relation_df = weather_duration_relation_df

	fig, ax = plt.subplots(4, 5, figsize=(30,25))
	j, k = 0, 0
	for i in range(len(column_name_list)):
		ax[j, k].scatter(weather_duration_relation_df[column_name_list[i]],
						 weather_duration_relation_df['duration_sec'],
						 alpha=0.7)
		ax[j, k].set_title(column_name_list[i])
		k += 1
		if k > 4:
			j += 1
			k = 0

	fig.tight_layout()
	ax[3,4].set_axis_off()
	plt.show()


def plot_heatMap(stat):
	"""
	This function is used to preprocess the dataset and merge the dataframe,
	then calculate the correlation and generate discriptive statistic.

	:param: stat: (dataframe) the dataframe that contains the correlation between weather condition.

	"""

	stat = stat
	plt.figure(figsize = (12,8))
	sns.heatmap(stat, linewidths=.7, cmap="YlGnBu")
	plt.show()


def avg_duration(trips_df):
	"""
	This function calculates the daily average duration of trips for member riders and casual riders, and returns dataframe
	for each of them.
	:param trips_df: (dataframe) the dataframe which contains the data after data cleaning.
	:return: member_d (dataframe) the dataframe that contains the data of average daily duration of trips for member riders.
	:return: casual_d the dataframe that contains the data of average daily duration of trips for casual riders.
	"""

	# check the average duration for each member and casual rider
	total_duration = trips_df.groupby(['start_date_day', 'is_member'])['duration_sec'].sum()
	totalnum = trips_df.groupby(['start_date_day', 'is_member'])['is_member'].count()
	average_duration = round(total_duration / totalnum, 2)
	# create average duration dataframe
	avg_duration_df = average_duration.to_frame().reset_index()
	avg_duration_df.rename(columns={0: "average duration"}, inplace=True)
	# dataframe of average trip duration of member
	member_d = avg_duration_df.loc[avg_duration_df["is_member"] == 1]
	# dataframe of average trip duration of casual
	casual_d = avg_duration_df.loc[avg_duration_df["is_member"] == 0]

	return member_d, casual_d


def plot_duration(member_d, casual_d):
	"""
	This function would present a plot_bar which contains the daily average duration for member riders and casual riders.
	:param: member_d: (dataframe) the dataframe that contains the data of average daily duration of trips for member riders.
	:param: casual_d: (dataframe) the dataframe that contains the data of average daily duration of trips for casual riders.
	"""

	plt.figure(dpi=120)
	plt.plot(member_d['start_date_day'], member_d['average duration'], label='member riders')
	plt.plot(casual_d['start_date_day'], casual_d['average duration'], label='casual riders')
	plt.title('Casual riders ride longer')
	plt.xlabel('Date')
	plt.ylabel('Trip Duration (sec)')
	plt.xticks(fontsize=5)
	plt.legend()
	plt.show()


def count_distance(new_was_trip_dis_df):
	"""
	This function is used for counting the distance.
	:param: new_was_trip_dis_df: (dataframe) the dataframe that contains the data of capital bike share trip.

	>>> count_distance(new_was_trip_dis_df)

	1269.0171096
	450.7676123
	1012.2497737
	1012.2497737
	1012.2497737

	"""

	new_was_trip_dis_df = new_was_trip_dis_df
	lon_start = new_was_trip_dis_df['start_lng']
	lat_start = new_was_trip_dis_df['start_lat']
	lon_end = new_was_trip_dis_df['end_lng']
	lat_end = new_was_trip_dis_df['end_lat']
	g1 = (lon_start, lat_start)
	g2 = (lon_end, lat_end)
	ret = haversine(g1, g2) * 1000
	res = "%.7f" % ret

	return res


def add_distance_column(new_was_trip_dis_df):
	"""
	This function is used for adding the distance column.
	:param: was_trip_dis_df: (dataframe) the dataframe that contains the data of capital bike share trip.
	"""
	new_was_trip_dis_df = new_was_trip_dis_df
	new_was_trip_dis_df['distance'] = new_was_trip_dis_df.apply(lambda new_was_trip_dis_df: count_distance(new_was_trip_dis_df), axis=1)
	new_was_trip_dis_df = new_was_trip_dis_df.drop(new_was_trip_dis_df[new_was_trip_dis_df.distance == '0.0000000'].index)

	return new_was_trip_dis_df


def plot_was_member_casual_distance(final_was_trip_dis_df):
	"""
	This function is used for ploting the bart charts for analyzing the hypothesis 4.
	:param: final_was_trip_dis_df: (dataframe) the dataframe that contains the data of capital bike share trip.
	"""

	final_was_trip_dis_df = final_was_trip_dis_df
	df = final_was_trip_dis_df[['member_casual', 'distance']]
	df['distance'] = df['distance'].astype(float, errors = 'raise')
	df = df.groupby('member_casual').sum()
	df.plot(kind='bar', y='distance', use_index=True, legend=False, title='Distance of members and casual riders')
	plt.xlabel("members and casual riders", fontsize=10)
	plt.ylabel("distance", fontsize=10)
	plt.xticks(fontsize=10)
	plt.yticks(fontsize=10)
	plt.show()


def daily_distance(trip_dis_df):
	"""
	This function returns a dataframe that the daily distance in that month
	:param trip_dis_df: (dataframe) the dataframe which contains the distance of each trip
	:return: distance_df (dataframe) the dataframe contains the total distance of each day in that month
	"""
	daily_distance_df = trip_dis_df.reset_index()
	daily_distance_df = daily_distance_df[['started_at', 'distance']]
	daily_distance_df['date_date'] = pd.to_datetime(daily_distance_df['started_at']).dt.date
	daily_distance_df = daily_distance_df[['date_date', 'distance']]
	daily_distance_df['distance'] = daily_distance_df['distance'].astype(float, errors='raise')
	daily_distance_df['distance'] = round(daily_distance_df['distance'], 2)
	daily_distance_df = daily_distance_df.set_index('date_date')
	daily_distance = daily_distance_df.groupby(['date_date'])['distance'].sum()
	distance_df = daily_distance.to_frame().reset_index()
	return distance_df


def plot_disncases(dataframe):
	"""
	This function presents the plot of the relationship between daily distance and confirmed cases.
	:param dataframe: The dataframe contains average distance and number of confirmed cases.
	"""
	plt.figure(dpi=120)
	plt.plot(dataframe['date_date'], dataframe['avg_dis'], label='average distance')
	plt.bar(dataframe['date_date'], dataframe['cases'], color='green',
			width=0.5, alpha = 0.5)
	plt.title('The relationship between daily distance and confirmed cases.')
	plt.xlabel('Date')
	plt.ylabel('Average Distance (km)')
	plt.xticks(fontsize=5)
	plt.legend()
	plt.show()


if __name__ == '__main__':
	# load the files
	trips_df, stations_df, weather_df, was_trip_dis_df, us_confirmed_df, month = load_file()
	# data pre-processing
	new_trips_df, new_weather_df, new_was_trip_dis_df = data_preprocessing(trips_df, weather_df, was_trip_dis_df)
	# data analysis
	column_name_list, weather_duration_relation_df, stat = data_analysis(new_trips_df, new_weather_df)

	# Hypothesis #1: Total daily trips duration depends on weather conditions
	plot_scatter(column_name_list, weather_duration_relation_df)
	plot_heatMap(stat)

	# Hypothesis #2: Club members ride longer in a trip
	member_duration, casual_duration = avg_duration(new_trips_df)
	plot_duration(member_duration, casual_duration)

	# Hypothesis #3: Compared to casual riders, member riders have a higher possibility to take bikes
	dp_df = member(trips_df)
	dp_dff = cal_percentage(dp_df)
	plot_bar(dp_dff)

	# Hypothesis #4: During April to June in 2020, members tend to ride a longer distance than casual riders on a trip in Washington.
	final_was_trip_dis_df = add_distance_column(new_was_trip_dis_df)
	plot_was_member_casual_distance(final_was_trip_dis_df)

	final_was_trip_dis_df = add_distance_column(new_was_trip_dis_df)

	# Hypothesis #5: During April to June in 2020, as the number of confirmed cases for coronavirus increases,
	# the daily average distance of trips would decrease in Washington.
	daily_total_distance = daily_distance(final_was_trip_dis_df)

	was_trip_dis_df = drop_na(was_trip_dis_df)
	was_trip_df = count_trips(was_trip_dis_df)

	# data pre-processing for covid confirmed cases and trips data
	wcases_df = daily_cases(us_confirmed_df)
	if int(month) == 4 or int(month) == 6:
		cases_time_df = filter_time(wcases_df, 2020, int(month), 1, 2020, int(month), 30)
	else:
		cases_time_df = filter_time(wcases_df, 2020, int(month), 1, 2020, int(month), 31)
	merge_df = pd.merge(cases_time_df, was_trip_df, on='date_date', how='inner')

	merge_df_final = pd.merge(merge_df, daily_total_distance, on='date_date', how='inner')

	merge_df_final['avg_dis'] = round(merge_df_final['distance']/merge_df_final['count'],2)
	plot_disncases(merge_df_final)


