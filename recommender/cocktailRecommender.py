from .cocktailRecommenderInterface import CocktailRecommenderInterface
from .case_base import CaseBase, Cocktail
import random
import csv


class CocktailRecommender(CocktailRecommenderInterface):
    def __init__(self, cocktail_file, taxonomy_file, general_taxonomy_file, k_top=2, penalty_step=0.1, retain_threshold=0.75, train_ratio=0.8, random_state=42):

        self.case_base = CaseBase(cocktail_file=cocktail_file, taxonomy_file=taxonomy_file, penalty_step=penalty_step, train_ratio=train_ratio, random_state=random_state)
        self.general_taxonomy_file = general_taxonomy_file
        self.k_top = k_top
        self.retrain_threshold = retain_threshold
        self._query_cocktail = None
        self._most_similar = None
        self.taxonomy_file = taxonomy_file
        self.adapted_cocktail_name = None

    def get_general_taxonomy(self):
        """ Return a list of four categories of cocktail classification"""

        with open(self.general_taxonomy_file, 'r') as infile:
            # read the file as a dictionary for each row ({header : value})
            reader = csv.DictReader(infile)
            data = {}
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value)
                    except KeyError:
                        data[header] = [value]

        # extract the variables you want
        fruits = data['fruits']
        alco = data['alcohols']
        nonalco = data['non-alcohols']
        others = data['others']

        return fruits, alco, nonalco, others

    def get_cocktail(self, cocktail_name):
        return self.case_base.get_cocktail(cocktail_name)

    def get_recommended_cocktail(self):
        return self._query_cocktail

    def get_all_cocktails(self):
        return self.case_base.get_all_cocktails()

    def get_recommendation(self, user_query):
        # Create query cocktail
        input_ingredients_by_taxonomy = self.case_base.get_taxonomy(user_query)
        self._query_cocktail = Cocktail(ingredients=user_query, ingredients_by_taxonomy=input_ingredients_by_taxonomy)

        # CBR cycle
        self._retrieve()  # Retrieve
        print('····· Retrieved cocktails (top '+ str(self.k_top)+') ·····')
        [print(c.name) for c in self._most_similar]  # Print most similar cocktail names
        steps, covered = self._adaptation()  # Adapt
        random_selected_names = covered

        if len(covered) >= 2:
            random_selected_names = random.choices(covered, k=2)

        if len(random_selected_names) == 2:
            name_adapted_recipe = 'Cocktail with ' + covered[0] + ' and ' + covered[1]
        elif len(covered) == 1:
            name_adapted_recipe = 'Cocktail with ' + covered[0]
        else:
            name_adapted_recipe = None

        if (len(steps) == 0 and (len(self._query_cocktail.ingredients_by_taxonomy['alcohol']) != 0 or len(self._query_cocktail.ingredients_by_taxonomy['juice'])) != 0):
            steps = ["Mix all ingredients"]
            if self._query_cocktail.ingredients_by_taxonomy['alcohol']:
                name_adapted_recipe = 'Cocktail with ' + str(self._query_cocktail.ingredients_by_taxonomy['alcohol'][0])
            elif self._query_cocktail.ingredients_by_taxonomy['juice']:
                name_adapted_recipe = 'Cocktail with ' + str(self._query_cocktail.ingredients_by_taxonomy['juice'][0])
            else:
                name_adapted_recipe = 'Cocktail with ' + str(self._query_cocktail.ingredients_by_taxonomy['alcohol'][0]) + ' and ' + str(self._query_cocktail.ingredients_by_taxonomy['juice'][0])

        elif len(steps) == 0:
            name_adapted_recipe = None

        if not self.adapted_cocktail_name:
            self.adapted_cocktail_name = name_adapted_recipe
        self._query_cocktail.name = name_adapted_recipe


        print('\n····· Final recommended recipe: ·····')
        print('Steps:')
        i = 0
        for step in steps:
            splitted_steps = step.split('.')
            for single_step in splitted_steps:
                if single_step != '':
                    print(i + 1, ' - ', single_step)
                    i += 1

        if self.adapted_cocktail_name:
            print('Recommended cocktail name: ', self.adapted_cocktail_name)
        else:
            print('The system is not able to find any recipe.')

        self._query_cocktail.preparation = steps  # Save preparation

        # To show cocktail in the web
        return self._query_cocktail

    def set_user_evaluation(self, user_eval):
        self._learning(user_eval)  # Learn

    def test(self):
        for name, cocktail in self.case_base.cocktails_test.items():
            print('Cocktail test name:', name)
            input_ingredients = cocktail.ingredients
            print('Ingredients in ', name, ':', input_ingredients)
            print("Reference preparation:")
            [print(step + 1, ' - ', cocktail.preparation[step], '\n') for step in range(len(cocktail.preparation))]
            print()
            print('Top similar cocktails for ', name, ':')
            self.get_recommendation(input_ingredients)
            print()

    def _retrieve(self):
        """Retrieves similar cocktails based on user ingredients query and preferences"""
        assert self._query_cocktail is not None
        cocktails_similarity = self.case_base.get_sim_cocktails(self._query_cocktail)
        self._most_similar = self.case_base.retrieve_cocktails(cocktails_similarity, self.k_top)

    def _adaptation(self):
        """
        Returns the preparation steps given a set of similar cocktails, user query and the preference
        :param :
        :return:
        """
        # start
        covered = []
        subsitute = []
        steps = []
        print('\n······ Initalize adaptation ······ \n')
        idx = 0
        print('Try to add steps from the top similar cocktails recipes that include query ingredients:')
        for cocktail in self._most_similar.keys():
            covered_new = set(self._query_cocktail.ingredients).intersection(set(cocktail.ingredients))
            if len(self._query_cocktail.ingredients) == len(cocktail.ingredients) and len(self._query_cocktail.ingredients) == len(covered_new):
                steps = [[i, cocktail.preparation[i]] for i in range(len(cocktail.preparation))]
                covered = self._query_cocktail.ingredients
                self.adapted_cocktail_name = cocktail.name
                break
            # go through all the steps in each cocktail
            for k in range(len(cocktail.preparation)):
                add = 0
                # go through all the ingredients that could have step
                for j in covered_new:
                    if j in cocktail.preparation[k]:
                        covered.append(j)
                        add = 1
                # add the steps that have ingredients of the new recipe
                if [k, cocktail.preparation[k]] not in steps and add == 1:
                    steps.append([k, cocktail.preparation[k]])
                    # search for ingredients in step to remove
                    for c_ingredient in cocktail.ingredients:
                        if c_ingredient in cocktail.preparation[k] and c_ingredient not in self._query_cocktail.ingredients:
                            if [idx, c_ingredient] not in subsitute:
                                subsitute.append([idx, c_ingredient])
                    idx += 1

        covered = list(set(covered))
        not_covered = list(set(self._query_cocktail.ingredients) - set(covered))
        print()
        print('==> Steps:')
        [print(step) for a, step in steps]
        print()
        print('Ingredients covered', covered)
        print('Ingredients not_covered', not_covered)
        if subsitute:
            print('Substitute', subsitute)


        print('\nTry to replace leftover ingredients with uncovered ingredients if they share a taxonomy:')
        # try to replace leftover ingredients with uncovered ingredients if they share a taxonomy
        dic_ingr_tax_nc = {}
        dic_ingr_tax_sub = {}
        for idx, ingredient in subsitute:
            dic_ingr_tax_sub[ingredient] = self.case_base.get_taxonomy(ingredient)
            comun_taxonomy_max = 0
            new_covered = ""
            new_substituted = ""

            for option in not_covered:
                dic_ingr_tax_nc[option] = self.case_base.get_taxonomy(option)
                comun_taxonomy = set(dic_ingr_tax_sub[ingredient]).intersection(set(dic_ingr_tax_nc[option]))
                # search for the option with most common taxonomys
                if len(comun_taxonomy) > comun_taxonomy_max:
                    comun_taxonomy_max = len(comun_taxonomy)
                    new_covered = option

            if new_covered != "":
                steps[idx][1] = steps[idx][1].replace(str(ingredient), str(new_covered))
                covered.append(new_covered)
                subsitute.remove([idx, ingredient])

            not_covered = list(set(self._query_cocktail.ingredients) - set(covered))
        print()
        print('==> Steps:')
        [print(step) for a, step in steps]
        print()
        print('Ingredients covered', covered)
        print('Ingredients not_covered', not_covered)
        if subsitute:
            print('Substitute', subsitute)

        # try to replace leftover ingredients with ingredients from the recipe, even if they are repeated, if they share taxonomy
        print()
        print('\nTry to replace leftover ingredients with ingredients from the recipe, even if they are repeated, if they share taxonomy:')
        for idx, ingredient in subsitute:

            dic_ingr_tax_sub[ingredient] = self.case_base.get_taxonomy(ingredient)
            comun_taxonomy_max = 0
            new_covered = ""
            new_substituted = ""

            for option in self._query_cocktail.ingredients:
                dic_ingr_tax_nc[option] = self.case_base.get_taxonomy(option)
                comun_taxonomy = set(dic_ingr_tax_sub[ingredient]).intersection(set(dic_ingr_tax_nc[option]))
                if len(comun_taxonomy) > comun_taxonomy_max:
                    comun_taxonomy_max = len(comun_taxonomy)
                    new_covered = option
                    new_substituted = [idx, ingredient]

            if new_covered != "":
                steps[idx][1] = steps[idx][1].replace(str(new_substituted[1]), str(new_covered))
                subsitute.remove(new_substituted)

        # ordenador los steps en un orden logico
        print()
        print('==> Steps:')
        [print(step) for a, step in steps]
        print()
        print('Ingredients covered', covered)
        print('Ingredients not_covered', not_covered)
        if subsitute:
            print('Substitute', subsitute)

        # add a step of another cocktail that has an uncovered ingredient
        print('\nAdd a step of another cocktail that has an uncovered ingredient:')
        if not_covered:
            dic = self.case_base.get_steps_by_ingredients()
            ingr_step_dic = dic[0]
            ingr_step_dic_unic = dic[1]
            # try adding the step without more ingredients and with an order that is not currently in the steps
            # If it is not possible, add the shorter one.
            for ingredient in not_covered:
                #print(ingr_step_dic_unic.get(ingredient))
                if ingr_step_dic_unic.get(ingredient) != [] and ingr_step_dic_unic.get(ingredient) != None:
                    shortest = ingr_step_dic_unic.get(ingredient)[0]
                    #print('solito', ingr_step_dic_unic.get(ingredient))
                    for k, step in ingr_step_dic_unic.get(ingredient):
                        if steps == []:
                            covered.append(ingredient)
                            steps.append([k, step])
                            break
                        else:
                            if k not in list(zip(*steps))[0]:
                                covered.append(ingredient)
                                steps.append([k, step])
                                break
                            else:
                                if len(step) < len(shortest[1]):
                                    shortest = [k, step]

                    if ingredient not in covered:
                        steps.append(shortest)
                        covered.append(ingredient)

            not_covered = list(set(self._query_cocktail.ingredients) - set(covered))
            print()
            print('==> Steps:')
            [print(step) for a, step in steps]
            print()
            print('Ingredients covered', covered)
            print('Ingredients not_covered', not_covered)
            if subsitute:
                print('Substitute', subsitute)

            print('\nAdd a step of another cocktail that has an uncovered ingredient 2:')
            # add one of the steps of another cocktail that has fewer leftover ingredients,
            # taking into account common taxonomies
            for ingredient in not_covered:

                to_add_common = []
                to_add_taxonomy = []
                numer_com_max, numer_com_tax_max = 0, -1
                # select the step among the 3 with the least ingredients left over, the one with the most common taxonomies
                #print('con mas', ingr_step_dic.get(ingredient))
                if ingr_step_dic.get(ingredient) != [] and ingr_step_dic.get(ingredient) != None:
                    steps_sort = sorted(ingr_step_dic.get(ingredient), key=lambda x: len(x[2]), reverse=True)[0:3]
                    #print('steps_sort', steps_sort)
                    for k, step, list_ingr in steps_sort:
                        list_taxonomy = []
                        numer_com = len((set(self._query_cocktail.ingredients)).intersection(set(list_ingr) - set(ingredient)))
                        for ingr in list_ingr:
                            list_taxonomy.extend(self.case_base.get_taxonomy(ingr))
                        numer_com_tax = len(set(list_taxonomy).intersection(set(self._query_cocktail.taxonomy_types)))
                        if numer_com > numer_com_max:
                            to_add_common = [k, step, list_ingr]
                        if numer_com_tax > numer_com_tax_max:
                            to_add_taxonomy = [k, step, list_ingr]

                    if to_add_common != []:
                        to_add = to_add_common
                    elif to_add_taxonomy != []:
                        to_add = to_add_taxonomy
                    else:
                        break
                    for s_ingredient in to_add[2]:

                        dic_ingr_tax_sub[s_ingredient] = self.case_base.get_taxonomy(s_ingredient)
                        comun_taxonomy_max = 0
                        new_covered = ""

                        for option in self._query_cocktail.ingredients:
                            dic_ingr_tax_nc[option] = self.case_base.get_taxonomy(option)
                            comun_taxonomy = set(dic_ingr_tax_sub[s_ingredient]).intersection(
                                set(dic_ingr_tax_nc[option]))

                            if len(comun_taxonomy) > comun_taxonomy_max:
                                comun_taxonomy_max = len(comun_taxonomy)
                                new_covered = option

                        if new_covered != "":
                            to_add[1] = to_add[1].replace(str(s_ingredient), str(new_covered))

                    steps.append([to_add[0], to_add[1]])
                    covered.append(ingredient)

        steps = sorted(steps, key=lambda x: x[0])

        not_covered = list(set(self._query_cocktail.ingredients) - set(covered))
        print()
        print('==> Steps:')
        [print(step) for a, step in steps]
        print()
        print('Ingredients covered', covered)
        print('Ingredients not_covered', not_covered)
        if subsitute:
            print('Substitute', subsitute)

        steps = [step for a, step in steps]
        return steps, covered

    def _evaluation(self):
        """Evaluates the preparation steps and decides to retain the case or not"""
        while True:
            evaluation = input("Cocktail evaluation (bad, good, neutral): ")
            if evaluation in ['bad', 'good', 'neutral']:
                break
        return evaluation

    def _learning(self, evaluation):
        """
        Stores the case into case library if evaluation is positive, penalizes most similar cocktails if evaluation is negative
        :param evaluation: evaluation of the generated cocktail preparation
        """
        if evaluation == 'good':
            sim = max([x[0] for x in self._most_similar.values()])
            if sim < self.retrain_threshold:
                self.case_base.add_cocktail(self._query_cocktail, self.adapted_cocktail_name)
        elif evaluation == 'bad':
            for cocktail_name in self._most_similar:
                self.case_base.penalize_cocktail(cocktail_name)
