import yaml
import pandas as pd
import numpy as np
import sys
import os
from math import sqrt
import matplotlib
import matplotlib.pyplot as plot
import networkx as nx

# Returns the directory of the script (only in script mode)
# But returns interpreter name in interactive mode.
def get_script_directory():
    path = os.path.realpath(sys.argv[0])
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)
path = get_script_directory()
print (path)
os.chdir(path)

# import config files
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
print (ratings_file)
# os.chdir(path)
# print(cfg['project_test_conf']['path_cwd'])
# print (user_ratings_csv)
user_ratings = pd.read_csv(ratings_file, index_col=ratings_index)
articles_db = pd.read_csv(articles_file, index_col=ratings_index)
objects_list = list(user_ratings.index)
user_ratings_T = user_ratings.transpose()
dataset = user_ratings_T.to_dict()
# print (dataset)

def similarity_score(Article1,Article2):

    # this Returns the ration euclidean distancen score of person 1 and 2

    # To get both rated items by person 1 and 2
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

# print (similarity_score('Article_1','Article_658'))

def pearson_correlation(Article1,Article2):

    # To get both rated items
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
		r = numerator_value/denominator_value
		return r

print (pearson_correlation('Article_1','Article_5'))

def most_similar_users(Article1,number_of_users):
	# returns the number_of_users (similar persons) for a given specific person.
	scores = [(pearson_correlation(Article1,other_person),other_person) for other_person in dataset if  other_person != Article1 ]
	# Sort the similar persons so that highest scores person will appear at the first
	scores.sort()
	scores.reverse()
	return (scores[0:number_of_users][0][1])


#most_similar_users('Article_1', 2)

#objects_list

def get_recommendations(objects, no_of_recommendations):
    recommended_articles = []
    input_articles = []
    for article in objects:
        # print (article, most_similar_users(article,2)[0][1], most_similar_users(article,2)[1][1])
        input_articles.append(article)
        recommended_articles.append(most_similar_users(article,no_of_recommendations))
        # recommended_articles.append((article, most_similar_users(article,no_of_recommendations)))
    return input_articles,recommended_articles

Article, recommended_article = get_recommendations(objects_list, 5)
# print (Article)
print(recommended_article)

recommended_article_title = []
for content in recommended_article:
    recommended_article_title.append(articles_db.Title[content])
# print recommended_article_title

input_article_title = []
for content in Article:
    input_article_title.append(articles_db.Title[content])
# print input_article_title


# Create Output DataFrame
df = pd.DataFrame()
df['Article'] = Article
df['Recommendation'] = recommended_article
df['News'] = input_article_title
df['Recommended_News'] = recommended_article_title
df = df.set_index('Article', drop=True, append=False, inplace=False, verify_integrity=False)

df.to_csv(Output_Recommendations)