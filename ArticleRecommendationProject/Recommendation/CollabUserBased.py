import yaml
import pandas as pd
import numpy as np
import sys
import os
from math import sqrt
import matplotlib
import matplotlib.pyplot as plot
import networkx as nx

class Collabuserbased(object):
    """User-User Collaberative Filtering."""
    def __init__(self):
        self.object = object

    def get_script_directory(self):
        """
        This function returns the directory of the script in scrip mode
        In interactive mode returns interpreter name. """

        path = os.path.realpath(sys.argv[0])
        if os.path.isdir(path):
            return path
        else:
            return os.path.dirname(path)

    def similarity_score(self, person1 ,person2):

    # this Returns the ration euclidean distancen score of person 1 and 2
    # To get both rated items by person 1 and 2
    both_viewed = {}

    for item in self.dataset[person1]:
        if item in self.dataset[person2]:
            both_viewed[item] = 1

        # The Conditions to check if they both have common rating items
        if len(both_viewed) == 0:
            return 0

        # Finding Euclidean distance
        sum_of_eclidean_distance = []

        for item in self.dataset[person1]:
            if item in self.dataset[person2]:
                sum_of_eclidean_distance.append(pow(self.dataset[person1][item] - self.dataset[person2][item], 2))
        sum_of_eclidean_distance = sums(sum_of_eclidean_distance)

        return 1/(1+sqrt(sum_of_eclidean_distance))

def person_correlation(person1, person2):

   # To get both rated items
    both_rated = {}
    for item in self.dataset[person1]:
        if item in self.dataset[person2]:
            both_rated[item] = 1

    number_of_ratings = len(both_rated)

    # Checking for ratings in common
    if number_of_ratings == 0:
        return 0

    # Add up all the preferences of each user
    person1_preferences_sum = sum([self.dataset[person1][item] for item in both_rated])
    person2_preferences_sum = sum([self.dataset[person2][item] for item in both_rated])

    # Sum up the squares of preferences of each user
    person1_square_preferences_sum = sum([pow(self.dataset[person1][item],2) for item in both_rated])
    person2_square_preferences_sum = sum([pow(self.dataset[person2][item],2) for item in both_rated])

    # Sum up the product value of both preferences for each item
    product_sum_of_both_users = sum([self.dataset[person1][item] * self.dataset[person2][item] for item in both_rated])

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
    scores = [(person_correlation(person, other_person), other_person) for other_person in self.dataset if other_person != person]

    # Sort the similar persons so the highest scores person will appear at the first
    scores.sort()
    scores.reverse()
    return scores[0:number_of_users]

def user_recommendations(person):

    # Gets recommendations for a person by using a weighted average of every other user's rankings
    totals = {}
    simSums = {}
    rankings_list =[]
    for other in self.dataset:
        # don't compare me to myself
        if other == person:
            continue
        sim = person_correlation(person,other)

        # ignore scores of zero or lower
        if sim <=0:
            continue
        for item in self.dataset[other]:
        # Similrity * score
            totals.setdefault(item,0)
            totals[item] += self.dataset[other][item]* sim
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
