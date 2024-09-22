class CocktailRecommenderInterface(object):
    """ Interface for Cocktail Recommender """

    def get_general_taxonomy(self):
        """ Return a list of four categories of cocktail classification"""

    def store_cocktail(self, cocktail):
        """Add a cocktail to the training case base"""

    def get_cocktail(self, name):
        """Get a cocktail by its name """

    def get_recommended_cocktail(self):
        """Get recommended cocktail"""

    def get_all_cocktails(self):
        """ Returns all the cocktails of training case base"""

    def get_recommendation(self, user_query):
        """ Retrieve and adaptation steps
            :return cocktail_recommended
        """

    def set_user_evaluation(self, user_eval):
        """ Performs evaluation and learning steps
            :param user_eval: bad, neutral, good """

    def retrieve(self):
        """ Retrive step """

    def adaptation(self):
        """ Adaptation step """

    def evaluation(self):
        """ Evaluation step """

    def learning(self):
        """ Learning steo"""
