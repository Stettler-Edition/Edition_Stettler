from pathlib import Path
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

# Dossier contenant les fichiers ALTO
DOSSIER_ALTO = Path("ALTO")

# Fichier XML de sortie
FICHIER_SORTIE = Path("Stettler_extraction_complet.xml")

# Namespace ALTO
NS = {"alto": "http://www.loc.gov/standards/alto/ns-v4#"}

# Début du fichier XML
sortie = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<extraction xmlns="http://www.tei-c.org/ns/1.0">',
]

# Parcours des 101 pages
for numero in range(1, 102):

    fichier = DOSSIER_ALTO / f"Stettler_vol.1_p.{numero}.xml"

    if not fichier.exists():
        print(f"⚠️ Fichier absent : {fichier}")
        continue

    print(f"Traitement de la page {numero} : {fichier.name}")

    # Lecture du fichier ALTO
    arbre = ET.parse(fichier)
    racine = arbre.getroot()

    # Page
    sortie.append(f'  <div type="page" n="{numero}">')

    # Recherche de toutes les TextLine
    for textline in racine.findall(".//alto:TextLine", NS):

        # Recherche du String contenu dans la TextLine
        string = textline.find("alto:String", NS)

        if string is not None:

            # Récupération du contenu
            contenu = string.get("CONTENT")

            if contenu:
                sortie.append(f"    <lb/><line>{escape(contenu)}</line>")

    sortie.append("  </div>")

# Fin du document
sortie.append("</extraction>")

# Écriture du fichier final
FICHIER_SORTIE.write_text(
    "\n".join(sortie),
    encoding="utf-8"
)

print()
print("✅ Extraction terminée !")
print(f"Fichier créé : {FICHIER_SORTIE.resolve()}")