import pandas as pd
import numpy as np
import sys
import os
from math import sqrt
import matplotlib.pyplot as plot
import logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class AnalyzeArticlesCollab:

    def __init__(self):
    	self.distance_algo_type = 'Pearson'
    	self.type_of_collab = 'Item'

	"""
    Load and transform the  articles, train a COllab 
    """ 
	def run(self):
		self.load_articles()
        self.most_similar_users(Object1,number_of_users)

    # Load data
    """
    Loads the Dictionary with all the  articles. 
    """
    def load_articles(self):
		file_path = '/Users/shwetanknagar/Downloads/Personal/Project Eventstreet/Boconni Project'
		file_name = os.path.basename('User_Ratings_Compile.csv')
		path = os.path.join(file_path, file_name)
		user_ratings = pd.read_csv(path, index_col = 'Article')
		user_ratings = user_ratings.transpose()
		dict_user_ratings = user_ratings.to_dict()
		dataset = dict_user_ratings

	# this Returns the ration euclidean distancen score of person 1 and 2
	# To get both rated items by person 1 and 2
	def euclidean_distance(self,Object1,Object2):
		both_viewed = {}
		for item in dataset[Object1]:
	    	if item in dataset[Object2]:
	        	both_viewed[item] = 1
	        
	        # The Conditions to check if they both have common rating items
	        if len(both_viewed) == 0:
	        	return 0

	        # Finding Euclidean distance
	        sum_of_eclidean_distance = []

	        for item in dataset[Object1]:
        		if item in dataset[Object2]:
	            	sum_of_eclidean_distance.append(pow(dataset[Object1][item] - dataset[Object2][item], 2))
	        sum_of_eclidean_distance = sum(sum_of_eclidean_distance)
	        print sum_of_eclidean_distance
	        return 1/(1+sqrt(sum_of_eclidean_distance))
	# To get both rated items        
    def pearson_correlation_distance(self,Object1,Object2):
		both_rated = {}
		for item in dataset[Object1]:
			if item in dataset[Object2]:
				both_rated[item] = 1

		number_of_ratings = len(both_rated)		
		
		# Checking for number of ratings in common
		if number_of_ratings == 0:
			return 0

		# Add up all the preferences of each user
		person1_preferences_sum = sum([dataset[Object1][item] for item in both_rated])
		person2_preferences_sum = sum([dataset[Object2][item] for item in both_rated])

		# Sum up the squares of preferences of each user
		person1_square_preferences_sum = sum([pow(dataset[Object1][item],2) for item in both_rated])
		person2_square_preferences_sum = sum([pow(dataset[Object2][item],2) for item in both_rated])

		# Sum up the product value of both preferences for each item
		product_sum_of_both_users = sum([dataset[Object1][item] * dataset[Object2][item] for item in both_rated])

		# Calculate the pearson score
		numerator_value = product_sum_of_both_users - (person1_preferences_sum*person2_preferences_sum/number_of_ratings)
		denominator_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum,2)/number_of_ratings) * (person2_square_preferences_sum -pow(person2_preferences_sum,2)/number_of_ratings))
		if denominator_value == 0:
			return 0
		else:
			r = numerator_value/denominator_value
			return r


	def most_similar_users(self,Object1,number_of_users):
		# returns the number_of_users (similar persons) for a given specific person.
		if self.distance_algo_type = 'Pearson':
			scores = [(pearson_correlation_distance(Object1,other_person),other_person) for other_person in dataset if  other_person != Object1 ]
		if self.distance_algo_type = 'Euclidean':
			scores = [(euclidean_distance(Object1,other_person),other_person) for other_person in dataset if  other_person != Object1 ]
		# Sort the similar persons so that highest scores person will appear at the first
		scores.sort()
		scores.reverse()
		return scores[0:number_of_users]    	


if __name__ == "__main__":
    AnalyzeArticlesCollab().run()        