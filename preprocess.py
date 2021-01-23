sum_list = ['homs_sum', 'rape_sum', 'rob_sum', 'violent_crime', 'State']
rate_list = ['homs_per_100k', 'rape_per_100k', 'rob_per_100k', 'violent_per_100k', 'State']


def data_filtering_geochart(state, crime, year_range, data_crime):
    pop = data.population_engineers_hurricanes()
    if year_range is not None:
        data_crime = data_crime.loc[data_crime["year"].between(year_range[0], year_range[1])]
    results = data_crime.groupby('State')['violent_per_100k'].sum()
    results.to_frame()
    results_df = pd.merge(results, pop, how = 'right', left_on = 'State', right_on = 'state')
    return results_df

    
