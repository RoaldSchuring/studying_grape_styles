import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import numpy as np
import PIL
import pandas as pd
from operator import itemgetter

import os
os.environ['PROJ_LIB'] = r'C:\Users\roald\Anaconda3\pkgs\proj4-5.2.0-ha925a31_1\Library\share'

from mpl_toolkits.basemap import Basemap


# this function prints the most frequently appearing top-level descriptors for a set of wines
def generate_descriptor_info(dataframe, cluster):
    all_descriptors = pd.read_csv('chardonnay_descriptors.csv')
    all_descriptors.head()

    cluster_x = dataframe.loc[dataframe['cluster_label'] == cluster].reset_index()
    unpacked_cluster_x = (pd.melt(cluster_x.descriptor_level_3.apply(pd.Series).reset_index(),
                                  id_vars=['index'],
                                  value_name='descriptor')
                          .set_index(['index'])
                          .drop('variable', axis=1)
                          .dropna()
                          .sort_index()
                          ).reset_index()

    descriptor_mapping = unpacked_cluster_x.merge(all_descriptors, left_on='descriptor', right_on='descriptor_level_3',
                                                  how='left')
    descriptor_mapping.drop_duplicates(subset=['index', 'descriptor'], inplace=True)
    descriptor_mapping.set_index('index', inplace=True)
    descriptor_mapping = descriptor_mapping[['descriptor', 'descriptor_level_1']]

    descriptor_class_counts = Counter(descriptor_mapping['descriptor_level_1']).most_common(12)
    descriptor_percs = [(i[0], i[1] / len(descriptor_mapping)) for i in descriptor_class_counts]

    descriptor_percs.sort(key=itemgetter(1), reverse=True)
    descriptor_percs = [(i[0], '{0:.0%}'.format(i[1])) for i in descriptor_percs]
    print(descriptor_percs)


# this function generates a wordcloud given a dataframe with wine descriptor info
def generate_wordcloud(wines_in_cluster, level, category=None, color=None, title=None):

    mask_bottle = np.array(PIL.Image.open("wine_bottle_icon.jpg"))

    list_text = list(wines_in_cluster[level])
    one_cluster_text = [item for sublist in list_text for item in sublist]

    all_descriptors = pd.read_csv('chardonnay_descriptors.csv')

    if category is None:
        refined_one_cluster_text = one_cluster_text
    else:
        just_category_descriptors = all_descriptors.loc[all_descriptors['descriptor_level_1'] == category]
        just_category_descriptors_list = list(set(just_category_descriptors[level]))
        refined_one_cluster_text = [t for t in one_cluster_text if t in just_category_descriptors_list]

        plt.ylabel(category.capitalize(), fontsize=20)

    descriptor_value_counts = Counter(refined_one_cluster_text).most_common(20)

    wordcloud_dict = dict()
    for descriptor in descriptor_value_counts:
        wordcloud_dict[descriptor[0]] = descriptor[1]

    if color is None:
        word_cloud = WordCloud(width=1200, height=400, background_color='white', mask=mask_bottle, relative_scaling=0.3,
                               colormap='gist_heat').fit_words(wordcloud_dict)
    else:
        word_cloud = WordCloud(width=1200, height=400, background_color='white', mask=mask_bottle, relative_scaling=0.3,
                               color_func=lambda *args, **kwargs: color).fit_words(wordcloud_dict)

    plt.imshow(word_cloud, interpolation='bilinear')

    if title:
        plt.title(title, fontsize=16)

    plt.yticks([])
    plt.xticks([])

    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)


# this function generates a map with circles based on the frequency with which various observations appear
def gen_map(wines_in_cluster, color):
    clustered_wines_for_mapping = wines_in_cluster.groupby(['Country', 'Latitude', 'Longitude'])[
        'Name'].count().reset_index()

    m = Basemap(llcrnrlon=-180, llcrnrlat=-65, urcrnrlon=180, urcrnrlat=80)
    m.drawmapboundary(fill_color='white', linewidth=0)
    m.fillcontinents(color='grey', alpha=0.3)
    m.drawcoastlines(linewidth=0.1, color="white")

    clustered_wines_for_mapping['labels_enc'] = pd.factorize(clustered_wines_for_mapping['Country'])[0]

    m.scatter(clustered_wines_for_mapping['Longitude'], clustered_wines_for_mapping['Latitude'],
              s=clustered_wines_for_mapping['Name'] * 5, alpha=0.8, c=color
              )


# this function generates a bar chart
def generate_bar_chart(wines_in_cluster, variable, x_label, number_of_bars, color):
    bar_values = wines_in_cluster[variable].value_counts(normalize=True)

    if bar_values.index.dtype == 'float64':
        bar_values = bar_values.sort_index()
        bar_values = bar_values.loc[bar_values.index > 0]
        bar_values = bar_values.head(number_of_bars)
        tick_labels_int = [int(n) for n in list(bar_values.index)]
        plt.bar(np.arange(number_of_bars), bar_values, width=0.5, tick_label=tick_labels_int, color=color)
        average_var_value = format(np.mean(wines_in_cluster[variable]), '.2f')
        plt.text(s='Average: ' + average_var_value, x=-0.5, y=1.28 * max(bar_values), fontsize=12)
    else:
        bar_values = bar_values.head(number_of_bars)
        plt.bar(np.arange(number_of_bars), bar_values, width=0.5, tick_label=bar_values.index, color=color)

    for e, label in enumerate(list(bar_values)):
        percentage_label = '{0:.0%}'.format(label)
        plt.text(s=percentage_label, x=e, y=1.1 * label, ha='center', va='bottom', fontsize=12)

    plt.ylim(bottom=0, top=2 * max(bar_values))
    plt.yticks([])

    plt.text(x=-0.5, y=1.5 * max(bar_values), s=x_label, fontsize=16)

    for pos in ['right', 'top', 'left']:
        plt.gca().spines[pos].set_visible(False)


# this function generates a histogram
def generate_histogram(wines_in_cluster, variable, min_value, max_value, title, color, binsize):
    wines_in_cluster_refined = wines_in_cluster.copy()
    wines_in_cluster_refined.dropna(subset=[variable], axis=0, inplace=True)
    (wines_in_cluster_refined[variable].replace('[\$,)]', '', regex=True, inplace=True))
    (wines_in_cluster_refined[variable].replace('[\%,)]', '', regex=True, inplace=True))

    wines_in_cluster_refined[variable] = wines_in_cluster_refined[variable].astype(float)

    n, bins, patches = plt.hist(x=list(wines_in_cluster_refined[variable]), bins=binsize, range=(min_value, max_value),
                                alpha=0.5, rwidth=1, density=True, stacked=True, color=color)

    #     plt.title(title, fontsize=12, pad=2)
    plt.xlim(xmin=min_value, xmax=max_value)
    plt.xticks(ticks=np.arange(min_value, max_value + 1, (max_value - min_value) / binsize), fontsize=12)

    #     plt.ylabel('Frequency', fontsize=12)
    maxfreq = n.max()
    plt.ylim(ymax=2 * max(n))
    plt.yticks([])

    unity_values = n / n.sum()
    percentage_labels = ['{0:.0%}'.format(nr) for nr in unity_values]

    for i in range(binsize):
        plt.text(x=(min_value + i * (max_value - min_value) / binsize + 0.3 * (max_value - min_value) / binsize),
                 y=(max(n) / 20 + n[i]),
                 s=percentage_labels[i], fontsize=12)

    average_var_value = format(np.mean(wines_in_cluster_refined[variable]), '.2f')
    #     plt.text(s='Average: ' + average_var_value, x=0.4*(max_value+min_value), y=1.28*maxfreq, fontsize=12)

    #     plt.text(x=min_value+0.1*(max_value-min_value), y=1.5*max(n), s=title, fontsize=16)
    plt.text(s='Average: ' + average_var_value, x=min_value, y=1.3 * maxfreq, fontsize=12)

    plt.text(x=min_value, y=1.5 * max(n), s=title, fontsize=16)

    for pos in ['right', 'top', 'left']:
        plt.gca().spines[pos].set_visible(False)


# this function generates information with the number of wines in a cluster and the % of total this makes up
def generate_cluster_info(wines_in_cluster, all_wines):
    cluster_size = len(wines_in_cluster.index)
    total_nr_wines = len(all_wines.index)

    proportion_of_total = '{0:.0%}'.format(cluster_size / total_nr_wines)

    label_text_1 = str(cluster_size) + ' Wines in Cluster'
    label_text_2 = '(' + str(proportion_of_total) + ' of total)'

    #     fig2 = plt.figure(figsize=(5, 2))
    plt.text(x=1, y=1, s=label_text_1, size=20, ha='center', va='center',
             bbox=dict(boxstyle='square', fc="white", edgecolor='white'))
    plt.text(x=1, y=0.7, s=label_text_2, size=16, style='italic', ha='center', va='center',
             bbox=dict(boxstyle='square', fc="white", edgecolor='white'))

    plt.xlim((-1, 3))
    plt.ylim((0, 1.2))
    plt.axis('off')


# this function produces a visual with bar charts, histograms, wordclouds and maps summarizing the characteristics of a cluster
def generate_cluster_visual(filtered_dataframe, full_dataframe, title):

    subplot_grid = (20, 3)

    plt.subplot2grid(subplot_grid, (0, 0), rowspan=4)
    generate_cluster_info(filtered_dataframe, full_dataframe)

    plt.subplot2grid(subplot_grid, (4, 0), rowspan=4)
    generate_wordcloud(wines_in_cluster=filtered_dataframe, level='descriptor_level_3', category='fruit', color='#223344')

    plt.subplot2grid(subplot_grid, (8, 0), rowspan=4)
    generate_wordcloud(wines_in_cluster=filtered_dataframe, level='descriptor_level_3', category='oak', color='#916e31')

    plt.subplot2grid(subplot_grid, (12, 0), rowspan=4)
    generate_wordcloud(wines_in_cluster=filtered_dataframe, level='descriptor_level_3', category='acid', color='#c88c27')

    plt.subplot2grid(subplot_grid, (16, 0), rowspan=4)
    generate_wordcloud(wines_in_cluster=filtered_dataframe, level='descriptor_level_3', category='body', color='#581845')

    plt.subplot2grid(subplot_grid, (0, 1), colspan=2, rowspan=10)
    gen_map(filtered_dataframe, '#223344')

    plt.subplot2grid(subplot_grid, (10, 1), rowspan=5)
    generate_bar_chart(filtered_dataframe, 'Country', 'Top 5 Countries', 5, '#223344')

    plt.subplot2grid(subplot_grid, (10, 2), rowspan=5)
    generate_bar_chart(filtered_dataframe, 'Province', 'Top 5 Provinces', 5, '#223344')

    plt.subplot2grid(subplot_grid, (15, 1), rowspan=5)
    generate_bar_chart(filtered_dataframe, 'Age', 'Age (years)', 5, '#c88c27')

    plt.subplot2grid(subplot_grid, (15, 2), rowspan=5)
    generate_histogram(filtered_dataframe, variable='Price', min_value=0, max_value=100, title='Price (dollars)', color='#916e31', binsize=10)

    plt.subplots_adjust(wspace=0.08, hspace=5)
    plt.suptitle(title, fontsize=30)
    plt.show()
