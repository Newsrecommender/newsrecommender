#!/usr/bin/env python2
from math import*
import re
import logging
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA, TruncatedSVD
import seaborn as sns
import nltk as nl
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import os
from scipy.spatial.distance import jaccard
#from scrapy.conf import settings
#from ConfigParser import SafeConfigParser



logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class AnalyzeArticles:
    def __init__(self):
        # The values below can be changed to tweak the recommender algorithm
        self.n_most_similar = 10
        self.n_features_title = 25
        self.n_features_content = 50
        #commented by shwenag
        #self.n_features_tags = 25
        self.n_features_total = 30

        # Do not change the values below
        self.df = None
        self.df_article_vectors = None
        self.similarity_score_dict = {}
        self.X = None
        self.X_title = None
        self.X_content = None
        self.type = 'Cos'
        self.is_pca = 'PCA'
        self.is_weight = 'TF-IDF'


    def run(self):
        """
        Load and transform the  articles, train a content-based recommender system and make a recommendation for each
         article.
        :return:
        """
        self.load_articles()
        self.vectorize_articles()
        self.reduce_dimensionality_articles()
        self.visualize_data()#Dont want to see the visualization now
        self.find_similar_articles()
        self.save_output_to_csv()

    # Load data
    def load_articles(self):
        """
        Loads the DataFrame with all the  articles. 
        Return: DataFrame with the title, content, tags and author of all  articles
        """
        #parser = SafeConfigParser()
        #parser.read('Config.ini')
        #file_path = settings['IP_FILE_PATH']
        #file_name = settings['IP_FILE_NAME']
        
        #logging.debug("Directory Name : {0} and File name is {1} \n".format(file_path,file_name))
        
        #logging.debug("Directory Name : {0} and File name is {1} \n".format(parser.get('Article_input_dir', 'ip_file_path'),parser.get('Article_input_file', 'ip_file_name'))    
        file_path = '/Users/shwetanknagar/Downloads/Personal/Project Eventstreet/Boconni Project'
        file_name = os.path.basename("TrainSet700_User_Ratings.xlsx")
        path = os.path.join(file_path, file_name)
        #commented by shwenag
        #self.df = pd.read_csv('TrainSet700_User_Ratings.xlsx', encoding='utf-8')         # Load articles in a DataFrame
        self.df = pd.read_excel(path,  na_values=['NA'], parse_cols = "A,B,C")
        #self.df = self.df[['Sno', 'title', 'content_text']]  # Slice to remove redundant columns
        #commenting the below by shwenag
        logging.debug("Number of articles: {0} and no of columns are {1} \n".format(len(self.df),self.df.shape))      

    def vectorize_articles(self):
        self.vectorize_title()    # Add title as dummies# Vectorize article
        self.vectorize_content()  # Add content as dummies
        #Commented by shwenag
        #self.vectorize_tags()     # Add title as dummies
        # Concatenate all article vectors, i.e. title and content
        article_metrics = (self.X_title, self.X_content)
        self.X = np.concatenate(article_metrics, axis=1)#shwenag - dont know why this is done??
        logging.debug("Number of features in total DataFrame: {0}".format(self.X.shape[1]))

    def get_vectorizer(self, ngram_range=(1, 3), min_df=2, max_df=1.0):
        """
        Define a binary CountVectorizer (Feature Presence) using n-grams and min and max document frequency
        :param ngram_range: n-grams are created for all numbers within this range
        :param min_df: min document frequency of features
        :param max_df: max document frequency of features
        :return:
        """
        if self.is_weight == 'FP':#Feature Presence
            vectorizer = CountVectorizer(ngram_range=ngram_range,
                                         tokenizer=self.tokenize,
                                         min_df=min_df,
                                         max_df=max_df,
                                         binary=True,
                                         stop_words='english')

        if self.is_weight == 'TF-IDF':#Feature Presence    
            vectorizer = TfidfVectorizer(ngram_range=ngram_range,
                                        tokenizer=self.tokenize,
                                         min_df=min_df, 
                                         max_df=max_df, 
                                         binary=True,
                                         stop_words='english')
        return vectorizer      

    @staticmethod
    def tokenize(text):
        """
        Tokenizes sequences of text and stems the tokens.
        :param text: String to tokenize
        :return: List with stemmed tokens
        """
        tokens = nl.WhitespaceTokenizer().tokenize(text)
        tokens = list(set(re.sub("[^a-zA-Z\']", "", token) for token in tokens))
        tokens = [word for word in tokens if word not in stopwords.words('english')]
        tokens = list(set(re.sub("[^a-zA-Z]", "", token) for token in tokens))
        stems = []
        stemmer = SnowballStemmer("english")
        for token in tokens:
            token = stemmer.stem(token)
            if token != "":
                stems.append(token)
        return stems

    def vectorize_title(self):
        """
        Vectorize the titles of all  articles.
        :return:
        """
        # Define vectorizer and apply on content to obtain an M x N array
        vectorizer = self.get_vectorizer(ngram_range=(1, 2),
                                         min_df=2)
        self.X_title = vectorizer.fit_transform(self.df['title'])
        self.X_title = self.X_title.toarray()
        self.X_title = np.array(self.X_title, dtype=float)
        logging.debug("Number of features in title: {0}".format(len(vectorizer.vocabulary_)))
        # Reduce dimensionality of title features
        self.X_title = self.reduce_dimensionality(self, self.X_title, self.n_features_title)

    def vectorize_content(self):
        """
        Vectorize the content of all  articles.
        :return:
        """
        # Define vectorizer and apply on content to obtain an M x N array
        vectorizer = self.get_vectorizer(ngram_range=(1, 1),
                                         min_df=4,
                                         max_df=0.3)
        self.X_content = vectorizer.fit_transform(self.df['content_text'])
        self.X_content = self.X_content.toarray()
        self.X_content = np.array(self.X_content, dtype=float)
        logging.debug("Number of features in content: {0}".format(len(vectorizer.vocabulary_)))
        # Reduce dimensionality of content features
        self.X_content = self.reduce_dimensionality(self, self.X_content, n_features=self.n_features_content)    

    def reduce_dimensionality_articles(self):
        """
        Reduce the dimensionality of the vectorized articles.
        :return:
        """
        # Reduce dimensionality
        self.X = self.reduce_dimensionality(self, self.X, n_features=self.n_features_total)

    @staticmethod
    def reduce_dimensionality(self, X, n_features):
        """
        Apply PCA or SVD to reduce dimension to n_features.
        :param X:
        :param n_features:
        :return:
        """
        # Initialize reduction method: PCA or SVD
        if self.is_pca == 'PCA':
           reducer = PCA(n_components=n_features)

        #reducer = PCA(n_components=n_features)
        if self.is_pca == 'SVD':
            reducer = TruncatedSVD(n_components=n_features)
        
        # Fit and transform data to n_features-dimensional space
        reducer.fit(X)
        self.X = reducer.transform(X)
        logging.debug("Reduced number of features to {0}".format(n_features))
        logging.debug("Percentage explained: %s\n" % reducer.explained_variance_ratio_.sum())
        return X

    def prepare_dataframe(self, X):
        """
        Prepare DataFrame for further use, e.g. finding similar articles or visualizing articles.
        :param X:
        :return: Dataframe with all  articles and its corresponding vectorized coordinates + other article metrics
        """
        df_article_vectors = pd.DataFrame(None)
        #df_article_vectors['tags_first'] = self.df['tags_first']
        #df_article_vectors['author'] = self.df['author']
        df_article_vectors['title'] = self.df['title']
        df_article_vectors['numbers'] = range(0, len(df_article_vectors))
        df_article_vectors['coordinates'] = df_article_vectors['numbers'].apply(lambda index: X[index, :])
        del df_article_vectors['numbers']
        # Initialize dataframe by appending new columns to store the titles of the n most similar articles
        for i in range(0, self.n_most_similar):
            df_article_vectors['most_similar_'+str(i+1)] = ""
        return df_article_vectors

    # Visualize data
    def visualize_data(self):
        """
        Transform the DataFrame to the 2-dimensional case and visualizes the data. The first tags are used as labels.
        :return:
        """
        logging.debug("Preparing visualization of DataFrame")
        # Reduce dimensionality to 2 features for visualization purposes
        X_visualization = self.reduce_dimensionality(self, self.X, n_features=2)
        df = self.prepare_dataframe(X_visualization)
        # Set X and Y coordinate for each articles
        df['X coordinate'] = df['coordinates'].apply(lambda x: x[0])# shwenag ...No clue whats happening??
        df['Y coordinate'] = df['coordinates'].apply(lambda x: x[1])# shwenag ...No clue whats happening??
        '''
        # Create a list of markers, each tag has its own marker
        n_tags_first = len(self.df['tags_first'].unique())
        markers_choice_list = ['o', 's', '^', '.', 'v', '<', '>', 'D']
        markers_list = [markers_choice_list[i % 8] for i in range(n_tags_first)]
        '''
        # Create scatter plot
        sns.lmplot("X coordinate",
                   "Y coordinate",
                   #hue="tags_first",#commented by shwenag
                   data=df,
                   fit_reg=False,
                   #markers=markers_list,#commented by shwenag
                   scatter_kws={"s": 150})
        # Adjust borders and add title
        sns.set(font_scale=2)
        sns.plt.title('Visualization of  articles in a 2-dimensional space')
        sns.plt.subplots_adjust(right=0.80, top=0.90, left=0.12, bottom=0.12)
        # Show plot
        sns.plt.show()

    def find_similar_articles(self):
        """
        Find the n most similar articles for each  article in the DataFrame
        :return:
        """
        # Prepare DataFrame by assigning each article in the DataFrame its corresponding coordinates
        self.df_article_vectors = self.prepare_dataframe(self.X)
        # Calculate similarity for all  articles and defines the n most similar articles
        self.calculate_similarity_scores_of_all_articles()
        # Find the n most similar articles using the similarity score dictionary
        self.find_n_most_similar_articles()
        # Remove redundant columns
        del self.df_article_vectors['coordinates']#shwenag dont know what the heck this is doing??

    def calculate_similarity_scores_of_all_articles(self):
        """
        Calculate the similarity scores of all  articles compared to all other articles.
        :return:
        """
        # Iterate over each article in DataFrame
        for index1, row1 in self.df_article_vectors.iterrows():
            # Initialize a dict to store the similarity scores to all other articles in
            similarity_scores = {}
            # Iterate again over all articles to calculate the similarity between article 1 and 2
            for index2, row2 in self.df_article_vectors.iterrows():
                if index1 != index2:
                    similarity_scores[index2] = self.calculate_similarity(row1['coordinates'], row2['coordinates'],self.type)#dont know what row1['coordinates'] would fetch
            # Save in dictionary
            self.similarity_score_dict[index1] = similarity_scores

    def find_n_most_similar_articles(self):
        """
        Find the n most similar articles with the highest similarity score for each  article in the DataFrame.
        :return:
        """
        # Iterate over each article in DataFrame
        for index, row in self.df_article_vectors.iterrows():
            # Get the similarity scores of the current article compared to all other articles
            similarity_scores = self.similarity_score_dict[index]
            # Find the highest similarity scores in the similarity_score_dict until we have found the n most similar.
            for i in range(0, self.n_most_similar):
                # Find most similar article, i.e. with highest cosine similarity. Note: if Euclidean distance, then min!
                most_similar_article_index = max(similarity_scores, key=similarity_scores.get)
                most_similar_article_score = similarity_scores[most_similar_article_index]
                del similarity_scores[most_similar_article_index]
                # Find corresponding title and set it as most similar article i in DataFrame
                title = self.df_article_vectors.loc[most_similar_article_index]['title'].encode('utf-8')
                title_plus_score = "{} ({:.2f})".format(title, most_similar_article_score)
                self.df_article_vectors.set_value(index, 'most_similar_'+str(i+1), title_plus_score)

    def calculate_similarity(self, article1, article2, type):
        """
        Calculate the similarity between two articles, e.g. the cosine similarity or the Euclidean distance.
        :param article1: coordinates (feature values) of article 1
        :param article2: coordinates (feature values) of article 2
        :return:
        """
        if self.type == 'Cos':
            similarity = self.cosine_similarity(article1, article2)  # Cosine similarity formula
        if self.type == 'Euc':
            similarity = self.euclidean_distance(article1, article2)  # Euclidean distance formula   
        '''
        if self.type == 'Jac':
            similarity = self.calculate_jaccard_score(article1, article2)  # jaccard distance formula      
        '''
        similarity = "{0:.2f}".format(round(similarity, 2))
        return float(similarity)

    @staticmethod
    def cosine_similarity(x, y):
        def square_rooted(v):
            return round(sqrt(sum([a * a for a in v])), 3)
        numerator = sum(a * b for a, b in zip(x, y))
        denominator = square_rooted(x) * square_rooted(y)
        return round(numerator/float(denominator), 3)

    @staticmethod
    def euclidean_distance(x, y):
        return np.linalg.norm(x-y)     
    '''
    def calculate_jaccard_score(dataset, vector1, vector2):
        jaccard_score = jaccard(dataset[vector1], dataset[vector2])
        return jaccard_score    
    '''

    """
    Save output DataFrame to csv file
    :return:
    """
    
    def save_output_to_csv(self):

        file_path = '/Users/shwetanknagar/Downloads/Personal/Project Eventstreet/Boconni Project'
        file_name = os.path.basename("ContentOutput.csv")
        path = os.path.join(file_path, file_name)
        #file_name = 'output.csv'
        try:
            self.df_article_vectors.to_csv(file_name, encoding='utf-8', sep=',')
        except IOError:
            logging.warning("Error while trying to save output file to %s!" % file_name)       
    
if __name__ == "__main__":
    AnalyzeArticles().run()        