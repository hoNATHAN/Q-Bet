from Levenshtein import jaro_winkler

teams = ['astralis', 'spirit', 'aurora-gaming', 'furia', 'nip', 'mibr', 'natus-vincere', 'the-mongolz', 'virtus-pro', 'oddik', 'g2', 'pain-gaming', 'big', 'hotu', 'm80-cs-go', 'gamerlegion', 'falcons-esports', 'vitality', 'mousesports', 'wildcard-gaming', 'faze', 'flyquest', 'liquid', 'complexity', '3dmax', 'saw', 'betclic-apogee-esports', 'rare-atom', 'legacy-br', 'eternal-fire', 'imperial', 'the-huns-esports', 'tyloo-cs-go', 'nemiga', 'nrg', 'lynn-vision', 'heroic', 'mindfreak', 'housebets', 'imperial-female', 'betboom-team', 'passion-ua', 'cloud9', 'fnatic', 'og', 'bestia', '9z', 'red-canids-cs-go', 'atox', 'ence', 'rooster', 'sangal', '9-pandas', 'alternate-attax-cs-go', 'amkal', 'bleed-esports-cs', 'parivision', 'true-rippers', 'future', 'revenant-cs', 'sashi-esport', 'jijiehao', 'themongolz', 'betboom', 'monte', 'betboom-20', 'gaimingladiators', 'pera', 'forze', 'boss', 'bad-news-kangaroos', 'steel-helmet', 'ecstatic', 'rebels-gaming-cs', 'apeks']

target = 'navi'

for team in teams:
    distance = jaro_winkler(team, target)
    print(team)
