import yaml
import pandas as pd
import numpy as np
import sys
import os
from math import sqrt
import matplotlib
import matplotlib.pyplot as plot
import networkx as nx

def get_script_directory():
    """
    This function returns the directory of the script in scrip mode
    In interactive mode returns interpreter name.
    """
    path = os.path.realpath(sys.argv[0])
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)

def similarity_score(Article1,Article2):
    """
    This function calculates Euclidean distance between to objects
    """
    both_viewed = {}

    for item in dataset[Article1]:
        if item in dataset[Article2]:
            both_viewed[item] = 1

        # The Conditions to check if they both have common rating items
        if len(both_viewed) == 0:
            return 0

        # Finding Euclidean distance
        sum_of_euclidean_distance = []

        for item in dataset[Article1]:
            if item in dataset[Article2]:
                sum_of_euclidean_distance.append(pow(dataset[Article1][item] - dataset[Article2][item], 2))
        sum_of_euclidean_distance = sum(sum_of_euclidean_distance)
        #print (sum_of_euclidean_distance)
        return 1/(1+sqrt(sum_of_euclidean_distance))

def pearson_correlation(Article1,Article2):
    """
    This function calculates Pearson correlation between two vectors
    """
    both_rated = {}
    for item in dataset[Article1]:
        if item in dataset[Article2]:
            both_rated[item] = 1
    number_of_ratings = len(both_rated)
    # Checking for number of ratings in common
    if number_of_ratings == 0:
        return 0
    # Add up all the preferences of each user
    person1_preferences_sum = sum([dataset[Article1][item] for item in both_rated])
    person2_preferences_sum = sum([dataset[Article2][item] for item in both_rated])

    # Sum up the squares of preferences of each user
    person1_square_preferences_sum = sum([pow(dataset[Article1][item],2) for item in both_rated])
    person2_square_preferences_sum = sum([pow(dataset[Article2][item],2) for item in both_rated])

    # Sum up the product value of both preferences for each item
    product_sum_of_both_users = sum([dataset[Article1][item] * dataset[Article2][item] for item in both_rated])

    # Calculate the pearson score
    numerator_value = product_sum_of_both_users - (person1_preferences_sum*person2_preferences_sum/number_of_ratings)
    denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))
    if denominator_value == 0:
        return 0
    else:
        r = round(numerator_value/denominator_value,2)
        return round(r,2)

def find_most_similar_objects(Article1,number_of_users):
    # returns the number_of_users (similar persons) for a given specific person.
    scores = [(pearson_correlation(Article1,other_person),other_person) for other_person in dataset if  other_person != Article1 ]
    # Sort the similar persons so that highest scores person will appear at the first
    scores.sort()
    scores.reverse()
    return (scores[0:number_of_users])

def get_recommendations(objects, no_of_recommendations):
    """
    This function generates recommendations for specified object
    """
    recommended_articles = []
    input_articles = []
    for article in objects:
        # print (article, find_most_similar_objects(article,2)[0][1], find_most_similar_objects(article,2)[1][1])
        input_articles.append(article)
        recommended_articles.append(find_most_similar_objects(article,no_of_recommendations))
    return input_articles,recommended_articles

# Find the path of script
path = get_script_directory()
print ('Script is located at {}'.format(path))
os.chdir(path)
# os.chdir(r'C:\Users\vikas\Documents\Projects\EPBA_Project\NewsRecommender\Final_gitrepo\newsrecommender\ArticleRecommendationProject\Recommendation')
# import config files
print("Reading configuration")
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

user_ratings_files_path = cfg['project_test_conf']['ratings_file_path']
user_ratings_csv_filename = cfg['project_test_conf']['ratings_file_name']
articles_files_path = cfg['project_test_conf']['articles_file_path']
articles_csv_filename = cfg['project_test_conf']['articles_file_name']
ratings_index = cfg['project_test_conf']['ratings_index_column']
output_file_path = cfg['project_test_conf']['output_path']
output_file_name = cfg['project_test_conf']['output_file_name']

ratings_file = os.path.join(user_ratings_files_path, user_ratings_csv_filename)
articles_file = os.path.join(articles_files_path, articles_csv_filename)
Output_Recommendations = os.path.join(output_file_path, output_file_name)

print("Configuration loaded successfully")
print ('Reading ratings from file {}'.format(ratings_file))
user_ratings = pd.read_csv(ratings_file, index_col=ratings_index)
articles_db = pd.read_csv(articles_file, index_col=ratings_index)
objects_list = list(user_ratings.index)
user_ratings_T = user_ratings.transpose()
dataset = user_ratings_T.to_dict()

# Get recommendations
print('Calculations in progress...')
Article, recommended_article = get_recommendations(objects_list, 5)
print('Calculations completed.')
print (recommended_article)
# Create output files
print('Creating output file')
# recommended_article_title = []
# for content in recommended_article:
#     recommended_article_title.append(articles_db.Title[content])
# input_article_title = []
# for content in Article:
#     input_article_title.append(articles_db.Title[content])

df = pd.DataFrame()
df['Article'] = Article
df['Recommendation'] = recommended_article
df = df.set_index('Article', drop=True, append=False, inplace=False, verify_integrity=False)
# print (df)
df.to_csv(Output_Recommendations)
# df
print('Output file created.')
print('Check output files at {}'.format(Output_Recommendations))
