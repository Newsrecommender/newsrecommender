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
    This function returns the directory of the script in script mode
    In interactive mode returns interpreter name.
    """
    path = os.path.realpath(sys.argv[0])
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)

def similarity_score(person1,person2):

    # this Returns the ration euclidean distancen score of person 1 and 2
    # To get both rated items by person 1 and 2
    both_viewed = {}

    for item in dataset[person1]:
        if item in dataset[person2]:
            both_viewed[item] = 1

        # The Conditions to check if they both have common rating items
        if len(both_viewed) == 0:
            return 0

        # Finding Euclidean distance
        sum_of_eclidean_distance = []

        for item in dataset[person1]:
            if item in dataset[person2]:
                sum_of_eclidean_distance.append(pow(dataset[person1][item] - dataset[person2][item], 2))
        sum_of_eclidean_distance = sums(sum_of_eclidean_distance)

        return 1/(1+sqrt(sum_of_eclidean_distance))

def person_correlation(person1, person2):

   # To get both rated items
    both_rated = {}
    for item in dataset[person1]:
        if item in dataset[person2]:
            both_rated[item] = 1

    number_of_ratings = len(both_rated)

    # Checking for ratings in common
    if number_of_ratings == 0:
        return 0

    # Add up all the preferences of each user
    person1_preferences_sum = sum([dataset[person1][item] for item in both_rated])
    person2_preferences_sum = sum([dataset[person2][item] for item in both_rated])

    # Sum up the squares of preferences of each user
    person1_square_preferences_sum = sum([pow(dataset[person1][item],2) for item in both_rated])
    person2_square_preferences_sum = sum([pow(dataset[person2][item],2) for item in both_rated])

    # Sum up the product value of both preferences for each item
    product_sum_of_both_users = sum([dataset[person1][item] * dataset[person2][item] for item in both_rated])

    # Calculate the pearson score
    numerator_value = product_sum_of_both_users - (person1_preferences_sum*person2_preferences_sum/number_of_ratings)
    denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))

    if denominator_value == 0:
        return 0
    else:
        r = numerator_value / denominator_value
        return r

def most_similar_users(person, number_of_users):

    # returns the number_of_users (similar persons) for a given specific person
    scores = [(person_correlation(person, other_person), other_person) for other_person in dataset if other_person != person]

    # Sort the similar persons so the highest scores person will appear at the first
    scores.sort()
    scores.reverse()
    return scores[0:number_of_users]

def user_recommendations(person):

    # Gets recommendations for a person by using a weighted average of every other user's rankings
    totals = {}
    simSums = {}
    rankings_list =[]
    for other in dataset:
        # don't compare me to myself
        if other == person:
            continue
        sim = person_correlation(person,other)

        # ignore scores of zero or lower
        if sim <=0:
            continue
        for item in dataset[other]:
        # Similrity * score
            totals.setdefault(item,0)
            totals[item] += dataset[other][item]* sim
            # sum of similarities
            simSums.setdefault(item,0)
            simSums[item]+= sim

        # Create the normalized list

    rankings = [(total/simSums[item],item) for item,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    # returns the recommended items
    recommendataions_list = [recommend_item for score,recommend_item in rankings]
    return recommendataions_list

# Find the path of script
path = get_script_directory()
print ('Script is located at {}'.format(path))
os.chdir(path)

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
user_output_file_name = cfg['project_test_conf']['output_user_file_name']
ratings_file = os.path.join(user_ratings_files_path, user_ratings_csv_filename)
articles_file = os.path.join(articles_files_path, articles_csv_filename)
Output_User_Recommendations = os.path.join(output_file_path, user_output_file_name)


print("Configuration loaded successfully")
print ('Reading ratings from file {}'.format(ratings_file))
user_ratings = pd.read_csv(ratings_file, index_col=ratings_index)
articles_db = pd.read_csv(articles_file, index_col=ratings_index)
objects_list = list(user_ratings.index)
dataset = user_ratings.to_dict()
print user_ratings.head()

user_articles_recommendations = user_recommendations('Vikas')
print(user_articles_recommendations[0:5])

# Generating recommendation for users
news_users = list(user_ratings)
user_recommended_articles = {}
for user in news_users:
    user_recommended_articles[user] = user_recommendations(user)[0:5]
#     user_recommended_articles[user] = articles_db.Title[user_recommendations(user)[0:5]]
print (user_recommended_articles)


# # Generating recommendation for users
# news_users = list(user_ratings)
# user_recommended_articles = {}
# for user in news_users:
#     # user_recommended_articles[user] = user_recommendations(user)[0:5]
#     user_recommended_articles[user] = articles_db.Title[user_recommendations(user)[0:5]]
#
# print (user_recommended_articles)
#
df_user = pd.DataFrame()
df_user = pd.DataFrame.from_dict(user_recommended_articles)
df_user = df_user.dropna(axis=0, how='any', thresh=None, subset=None, inplace=False)
print df_user
newsreaders = list(df_user)

# user_recommendations_articles = {}
# for user in newsreaders:
#     recommended_articles_titles = []
#     temp_rec = list(df_user[user])
#     for content in temp_rec:
#         user_recommendations_articles[user] = articles_db.Title[content]
#
# print (user_recommendations_articles)

# Generating recommendation for users
news_users = list(user_ratings)
user_recommended_articles = {}
for user in news_users:
    # user_recommended_articles[user] = user_recommendations(user)[0:5]
    user_recommended_articles[user] = articles_db.Title[user_recommendations(user)[0:5]]
print type(user_recommended_articles)
print (user_recommended_articles)

df_user_reco = pd.DataFrame.from_dict(user_recommended_articles)
print df_user_reco
df_user_reco.to_csv(output_user_file_name)
