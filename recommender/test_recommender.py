from recommender import CocktailRecommender

if __name__ == '__main__':
    recomender = CocktailRecommender(cocktail_file='data/ccc_cocktails.xml', taxonomy_file='data/taxonomy_taste.csv', general_taxonomy_file='data/general_taxonomy.csv', k_top=3, penalty_step=0.1, train_ratio=0.8, random_state=42)

    names = recomender.case_base._get_cocktail_names()
    print("")
    # print(names)
    ingredients = recomender.case_base.all_ingredients
    print("")
    # print(ingredients)
    ingredients_taxonomy = recomender.case_base.all_ingredients_by_taxonomy
    print("")
    # print(ingredients_taxonomy)
    print("")
    print()
    dic_ingr_step = recomender.case_base.get_steps_by_ingredients()


    #print('=============== GROUND TRUTH EXPERIMENTS =================')
    # Exotic fruit passion
    #input_ingredients = ['Lemonade','Blue curacao','passion fruit syrup','lemon juice','ice cube']
    # Cocktail appetizer
    #input_ingredients = ['dry white wine', 'sugar', 'lemon', 'orange', 'rum','sparkling water']
    # Porto flip
    #input_ingredients = ['Porto','cognac','egg','cinnamon','nutmeg','cane sugar syrup','ice cube']

    # print('========== QUERY SIMULATIONS =================')
    #input_ingredients = ['white wine', 'apple','pineapple juice','mint']
    #input_ingredients = ['martini', 'orange','lemon juice','lime zest','ice cube','brown sugar']
    #input_ingredients = ['coffee liqueur','sparkling mineral water']
    #input_ingredients = ['get_27', 'beer', 'grenadine', 'tabasco sauce', 'vanilla sugar', 'melon', 'egg']
    input_ingredients = ['sparkling wine', 'cointreau', 'lemon', 'cane sugar syrup', 'ice cube']

    print('============== COCKTAIL RECOMMENDER ===============')
    # recomender.case_base.save_xml('proba.xml')
    recomender.get_recommendation(input_ingredients)

    # print('\n ============= BEGIN TEST ============')
    # Remember to change the train ratio number!
    recomender.test()
