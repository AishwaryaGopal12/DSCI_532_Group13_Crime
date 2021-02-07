from vega_datasets import data
import pandas as pd


crime_list = ['Homicide', 'Rape', 'Larceny', 'Aggravated Assault']
sum_list = ['homs_sum', 'rape_sum', 'rob_sum', 'agg_ass_sum']
rate_list = ['homs_per_100k', 'rape_per_100k', 'rob_per_100k', 'agg_ass_per_100k']
sum_dict = {crime_list[i]: sum_list[i] for i in range(len(crime_list))} 
rate_dict = {crime_list[i]: rate_list[i] for i in range(len(crime_list))}
crime_dict = {'Number of Crimes Commited': sum_dict, 'Crime Rate (Crimes Commited Per 100,000 People)': rate_dict}


pop = data.population_engineers_hurricanes()


def data_filtering_geochart(state, crime, metric, year_range, data_crime):
    if year_range is not None:
        data_crime = data_crime.loc[data_crime["year"].between(year_range[0], year_range[1])]
    data_crime = data_crime[data_crime['State'].isin(state)]
    crimes = [crime_dict[metric][x] for x in crime]
    results = (data_crime[['State'] + crimes]
                .melt(id_vars = "State", var_name = "crime", value_name = "crime_count")
                .groupby('State')
                .sum())
    results_df = pd.merge(results, pop, how = 'right', left_on = 'State', right_on = 'state')
    return results_df

def data_filtering_trendchart(state, crime, metric, year_range, data_crime):
    
    crimes = [crime_dict[metric][x] for x in crime]
    trend_data = data_crime[data_crime['State'].isin(state)]
    trend_data = trend_data[(trend_data['year']>=year_range[0]) & (trend_data['year']<=year_range[1])]
    trend_data = trend_data.groupby('year')[crimes].sum().reset_index()
    trend_data = trend_data.melt(id_vars = "year", var_name = "crime", value_name = "crime_count")
    trend_data = trend_data.replace({"crime" : {v: k for k, v in crime_dict[metric].items()}})

    return trend_data

def data_filtering_treemap(state, crime, metric, year_range, data_crime):

    crimes = [crime_dict[metric][x] for x in crime]
    if year_range is not None:
        data_crime = data_crime.loc[data_crime["year"].between(year_range[0], year_range[1])]
    treemap_data = data_crime[data_crime['State'].isin(state)]
    treemap_data = treemap_data.groupby('State')[crimes].sum().reset_index()
    treemap_data = treemap_data.melt(id_vars = "State", var_name = "crime", value_name = "crime_count")
    treemap_data = treemap_data.replace({"crime" : {v: k for k, v in crime_dict[metric].items()}})

    return treemap_data

def data_filtering_treemap_2(state, crime, metric, year_range, data_crime):

    crimes = [crime_dict[metric][x] for x in crime]
    if year_range is not None:
        data_crime = data_crime.loc[data_crime["year"].between(year_range[0], year_range[1])]
    treemap_data = data_crime[data_crime['State'].isin(state)]
    treemap_data = treemap_data.groupby('State')[crimes].mean().reset_index()
    treemap_data = treemap_data.melt(id_vars = "State", var_name = "crime", value_name = "crime_count")
    treemap_data = treemap_data.replace({"crime" : {v: k for k, v in crime_dict[metric].items()}})

    return treemap_data