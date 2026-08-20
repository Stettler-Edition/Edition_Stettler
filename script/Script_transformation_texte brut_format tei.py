#!/usr/bin/env python3
"""
transform_tei.py

Transforme un XML "brut" du type :

    <div type="page" n="1">
        <lb/><line>Premiere ligne (titre)</line>
        <lb/><line>Deuxieme ligne...</line>
        ...
    </div>

en une structure TEI du type :

    <div type="page" n="1">
        <pb facs="#facs_p1" n="1"/>
        <fw type="pageNum" place="top-right">1</fw>
        <head><choice><orig>Premiere ligne (titre)</orig><reg></reg></choice></head>
        <p>
            <lb/><choice><orig>Deuxieme ligne...</orig><reg></reg></choice>
            ...
        </p>
    </div>

Regle appliquee : dans chaque <div type="page">, la PREMIERE <line> devient
le <head>, toutes les suivantes deviennent des <choice> a l'interieur d'un <p>.
Les balises <reg> sont laissees VIDES : c'est vous qui les completerez ensuite
dans Oxygen.

Usage :
    python3 transform_tei.py entree.xml sortie.xml
"""

import re
import sys
from io import BytesIO
from lxml import etree


def _reparer_racine_fermee_trop_tot(raw_text: str) -> str:
    """
    Corrige un bug frequent d'extraction ou la balise racine se ferme
    immediatement (ex: "<extraction></extraction>") alors que tout le
    contenu reel (les <div type="page">...) se trouve APRES, hors de
    toute racine. Dans ce cas :
      - on retire la fermeture prematuree de la racine,
      - on rajoute la fermeture de la racine a la toute fin du fichier
        (si elle n'y est pas deja).
    Si le fichier est deja bien forme, le texte est renvoye inchange.
    """
    match = re.match(
        r'^\s*(<\?xml[^>]*\?>\s*)?<(\w+)([^>]*)>\s*</\2>\s*',
        raw_text,
    )
    if not match:
        return raw_text  # rien a reparer, structure normale

    xml_decl = match.group(1) or ""
    racine = match.group(2)
    attrs = match.group(3)
    reste = raw_text[match.end():]

    corrige = f"{xml_decl}<{racine}{attrs}>\n{reste}"
    if not corrige.rstrip().endswith(f"</{racine}>"):
        corrige = corrige.rstrip() + f"\n</{racine}>\n"

    print(
        f"[Reparation automatique] La balise racine <{racine}> se fermait "
        f"immediatement ; le contenu qui suivait a ete replace a l'interieur.",
        file=sys.stderr,
    )
    return corrige


# Numero de page (inclus) jusqu'auquel la 1ere ligne est le head.
# Au-dela (pages 42 a 101 dans le cas present), c'est la 2e ligne qui est le head,
# et la 1ere ligne devient une ligne normale de <p>, placee avant le <head>.
SEUIL_PAGE_HEAD_EN_PREMIERE_LIGNE = 41


def _qn(ns_uri, tag):
    """Retourne le nom de balise qualifie (Clark notation) si un namespace est actif."""
    return f"{{{ns_uri}}}{tag}" if ns_uri else tag


def _new_el(ns_uri, tag):
    """Cree un nouvel element dans le bon namespace (ou sans namespace si ns_uri est None)."""
    if ns_uri:
        return etree.Element(_qn(ns_uri, tag), nsmap={None: ns_uri})
    return etree.Element(tag)


def _new_sub(ns_uri, parent, tag):
    return etree.SubElement(parent, _qn(ns_uri, tag))


def _make_choice_lb(ns_uri, parent: etree._Element, line: etree._Element) -> None:
    """Ajoute <lb/><choice><orig>texte</orig><reg/></choice> dans parent."""
    _new_sub(ns_uri, parent, "lb")
    choice = _new_sub(ns_uri, parent, "choice")
    orig = _new_sub(ns_uri, choice, "orig")
    orig.text = (line.text or "").strip()
    _new_sub(ns_uri, choice, "reg")  # reste vide


def _make_head(ns_uri, line: etree._Element) -> etree._Element:
    """Construit <head><choice><orig>texte</orig><reg/></choice></head>."""
    head = _new_el(ns_uri, "head")
    choice = _new_sub(ns_uri, head, "choice")
    orig = _new_sub(ns_uri, choice, "orig")
    orig.text = (line.text or "").strip()
    _new_sub(ns_uri, choice, "reg")  # reste vide
    return head


def transform_page_div(div: etree._Element, ns_uri) -> None:
    """Transforme le contenu d'un <div type="page"> en place."""
    n_str = div.get("n", "")
    try:
        n_int = int(n_str)
    except ValueError:
        n_int = None  # numero non numerique : on applique la regle par defaut (head = 1ere ligne)

    # Recupere toutes les <line> du div, dans l'ordre
    lines = div.findall(_qn(ns_uri, "line"))
    if not lines:
        return  # rien a transformer

    new_children = []

    # 1. <pb facs="#facs_pN" n="N"/>
    pb = _new_el(ns_uri, "pb")
    pb.set("facs", f"#facs_p{n_str}")
    pb.set("n", n_str)
    new_children.append(pb)

    # 2. <fw type="pageNum" place="top-right">N</fw>
    fw = _new_el(ns_uri, "fw")
    fw.set("type", "pageNum")
    fw.set("place", "top-right")
    fw.text = n_str
    new_children.append(fw)

    apres_seuil = n_int is not None and n_int > SEUIL_PAGE_HEAD_EN_PREMIERE_LIGNE

    if not apres_seuil:
        # Regle A (pages <= 41, ou n non numerique) : la 1ere ligne est le head.
        new_children.append(_make_head(ns_uri, lines[0]))

        if len(lines) > 1:
            p = _new_el(ns_uri, "p")
            for line in lines[1:]:
                _make_choice_lb(ns_uri, p, line)
            new_children.append(p)
    else:
        # Regle B (pages 42 a 101) : la 1ere ligne est une ligne normale de <p>,
        # placee AVANT le head ; la 2e ligne est le head ; le reste suit dans un <p>.
        if len(lines) >= 1:
            p_avant = _new_el(ns_uri, "p")
            _make_choice_lb(ns_uri, p_avant, lines[0])
            new_children.append(p_avant)

        if len(lines) >= 2:
            new_children.append(_make_head(ns_uri, lines[1]))

        if len(lines) > 2:
            p_apres = _new_el(ns_uri, "p")
            for line in lines[2:]:
                _make_choice_lb(ns_uri, p_apres, line)
            new_children.append(p_apres)

    # On vide le div puis on reinsere : on garde les attributs (type, n) du div
    for child in list(div):
        div.remove(child)
    div.text = None
    for new_child in new_children:
        div.append(new_child)


def transform_file(input_path: str, output_path: str) -> None:
    with open(input_path, encoding="utf-8-sig") as f:
        raw_text = f.read()

    raw_text = _reparer_racine_fermee_trop_tot(raw_text)

    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(BytesIO(raw_text.encode("utf-8")), parser)
    root = tree.getroot()

    # Detection d'un eventuel namespace par defaut (ex: TEI, xmlns="http://www.tei-c.org/ns/1.0")
    ns_uri = None
    if root.tag.startswith("{"):
        ns_uri = root.tag[1:root.tag.index("}")]

    # On cherche tous les <div type="page"> du document, ou la racine elle-meme
    # si c'est directement un <div type="page">.
    div_tag = _qn(ns_uri, "div")
    if ns_uri:
        page_divs = root.xpath(
            './/ns:div[@type="page"]', namespaces={"ns": ns_uri}
        )
    else:
        page_divs = root.xpath('.//div[@type="page"]')
    if root.tag == div_tag and root.get("type") == "page":
        page_divs = [root] + page_divs

    if not page_divs:
        print("Aucun <div type=\"page\"> trouve dans le fichier.", file=sys.stderr)
        return

    for div in page_divs:
        transform_page_div(div, ns_uri)

    tree.write(
        output_path,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage : python3 transform_tei.py entree.xml sortie.xml", file=sys.stderr)
        sys.exit(1)

    transform_file(sys.argv[1], sys.argv[2])
    print(f"Transformation terminee : {sys.argv[2]}")
