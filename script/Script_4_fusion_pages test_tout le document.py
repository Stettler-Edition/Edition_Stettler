import sys

def concatener(fichier1: str, fichier2: str, fichier_sortie: str) -> None:
    """
    Colle le contenu de fichier2 à la suite de fichier1,
    et écrit le résultat dans fichier_sortie.
    """
    with open(fichier1, encoding='utf-8') as f1:
        contenu1 = f1.read()

    with open(fichier2, encoding='utf-8') as f2:
        contenu2 = f2.read()

    # on s'assure qu'il y a bien un retour à la ligne entre les deux
    if not contenu1.endswith('\n'):
        contenu1 += '\n'

    resultat = contenu1 + contenu2

    with open(fichier_sortie, 'w', encoding='utf-8') as fout:
        fout.write(resultat)

    print(f"Fusion terminée : {fichier_sortie}")


if __name__ == '__main__':
    # Usage : python fusionner.py fichier1.xml fichier2.xml sortie.xml
    if len(sys.argv) != 4:
        print("Usage : python fusionner.py fichier1.xml fichier2.xml sortie.xml")
        sys.exit(1)

    concatener(sys.argv[1], sys.argv[2], sys.argv[3])
