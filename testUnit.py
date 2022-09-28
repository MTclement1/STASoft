from AutomaticSegment4 import modifierPrm


fichier = open('./venv/Data/param.prm', 'r')
lines = fichier.readlines()
fichier.close()

print(modifierPrm(lines, MTtest, 6, 135, 4, 8, "ici"))