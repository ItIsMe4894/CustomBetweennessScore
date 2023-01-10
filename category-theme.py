import pandas as pd

categoriesThemesDf = pd.read_csv("Themes_and_topics_-_flat (2).csv", sep=';')
pathsDf = pd.read_csv('graph_combinations_all.csv')

themesPerCategory = {}
categoriesPerTheme = {}
mediatingNodes = {}
peoplePerCategory = {}

for index, row in categoriesThemesDf.iterrows():
    themesPerCategory[row['Category - shorted named']] = row['Theme']
    if row['Theme'] not in categoriesPerTheme:
        categoriesPerTheme[row['Theme']] = 0
    categoriesPerTheme[row['Theme']] += 1
    peoplePerCategory[row['Category - shorted named']] = row['CountForClustering']


for index, row in pathsDf.iterrows():
    for fromCol, toCol in [['from', 'to'], ['to', 'from']]:
        mediatingNode = row[fromCol]
        themeOne = themesPerCategory[mediatingNode]
        themeTwo = themesPerCategory[row[toCol]]
        rowName = mediatingNode + '|' + themeOne + '|' + themeTwo
        if mediatingNode not in mediatingNodes:
            mediatingNodes[mediatingNode] = {}

        if rowName not in mediatingNodes[mediatingNode]:
            mediatingNodes[mediatingNode][rowName] = 0

        mediatingNodes[mediatingNode][rowName] += 1

### Simple tables with just the amount of paths
for mediatingNode, rows in mediatingNodes.items():
    f = open('simplePaths/' + mediatingNode + '.csv', "w")
    f.write('"Mediating Node","Theme 1","Theme 2","# of paths"' + "\n")
    for row, numberPaths in rows.items():
        values = row.split('|')
        f.write('"' + values[0] + '","' + values[1] + '","' + values[2] + '","' + str(numberPaths) + '"' + "\n")
    f.close()


totalCombinations = {}
totalScore = 0
totalPathForCategory = {}

### Combinations of the themes per category
for mediatingNode, rows in mediatingNodes.items():
    f = open('themeCombinations/' + mediatingNode + '.csv', "w")
    f.write('"Mediating Node","Theme 1","Theme 2","Normalized Score"' + "\n")
    combinationsDone = []
    scoreForCategory = 0
    for mainRow, mainRowNumberPaths in rows.items():
        themeOne = mainRow.split('|')[2]
        for subRow, subRowNumberPaths in rows.items():
            subRowValues = subRow.split('|')
            themeTwo = subRowValues[2]
            if themeTwo == themeOne:
                continue
            if themeOne + '|' + themeTwo in combinationsDone:
                continue
            if themeTwo + '|' + themeOne in combinationsDone:
                continue
            combinationsDone.append(themeOne + '|' + themeTwo)
            combinationsDone.append(themeTwo + '|' + themeOne)
            sharedPaths = min(mainRowNumberPaths, subRowNumberPaths)
            score = round(sharedPaths / (categoriesPerTheme[themeOne] * categoriesPerTheme[themeTwo]) * peoplePerCategory[mediatingNode], 3)

            f.write('"' + mediatingNode + '","' + themeOne + '","' + themeTwo + '",""' + str(score) + '"' + "\n")

            scoreForCategory += score

            if themeOne + '|' + themeTwo not in totalCombinations and themeTwo + '|' + themeOne not in totalCombinations:
                totalCombinations[themeOne + '|' + themeTwo] = {'categories': [mediatingNode], 'score': score}
                continue

            combinationKey = ''
            if themeOne + '|' + themeTwo in totalCombinations:
                combination = totalCombinations[themeOne + '|' + themeTwo]
                combinationKey = themeOne + '|' + themeTwo
            if themeTwo + '|' + themeOne in totalCombinations:
                combination = totalCombinations[themeTwo + '|' + themeOne]
                combinationKey = themeTwo + '|' + themeOne
            if combination == '':
                print('ERROR')

            if score > combination['score']:
                combination['categories'] = [mediatingNode]
                combination['score'] = score
            if score == combination['score'] and mediatingNode not in combination['categories']:
                combination['categories'].append(mediatingNode)

            totalCombinations[combinationKey] = combination

    totalPathForCategory[mediatingNode] = scoreForCategory
    totalScore += scoreForCategory
    f.close()

highscoresFile = open('highscores.csv', 'w')
highscoresFile.write('"Theme 1","Theme 2","Category","Normalized Score"' + "\n")
for combinationKey, combination in totalCombinations.items():
    themes = combinationKey.split('|')
    for category in combination['categories']:
        highscoresFile.write('"' + themes[0] + '","' + themes[1] + '","' + category + '","' + str(combination['score']) + '"' + "\n")
    
highscoresFile.close()

pathAverages = open('averages.csv', 'w')
pathAverages.write('"Category","Score"' + "\n")
for category, scoreForCategory in totalPathForCategory.items():
    score = scoreForCategory / totalScore
    pathAverages.write('"' + category + '","' + str(round(score, 3)) + '"' + "\n")


pathAverages.close()
