<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:my="urn:tei2tex"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="tei my xs">

  <xsl:output method="text" encoding="UTF-8" omit-xml-declaration="yes"/>
  <xsl:strip-space elements="*"/>

  <!-- ============================================================
       Fonction d'échappement LaTeX.
       Le \ doit être traité en premier, et sans jamais re-scanner
       le texte déjà produit (sinon les backslashes injectés par
       l'échappement seraient eux-mêmes ré-échappés).
       ============================================================ -->
  <xsl:function name="my:escape-latex" as="xs:string">
    <xsl:param name="input" as="xs:string"/>
    <xsl:variable name="s1" select="replace($input, '\\', '\\textbackslash{}')"/>
    <xsl:variable name="s2" select="replace($s1, '&amp;', '\\&amp;')"/>
    <xsl:variable name="s3" select="replace($s2, '%', '\\%')"/>
    <xsl:variable name="s4" select="replace($s3, '\$', '\\\$')"/>
    <xsl:variable name="s5" select="replace($s4, '#', '\\#')"/>
    <xsl:variable name="s6" select="replace($s5, '_', '\\_')"/>
    <xsl:variable name="s7" select="replace($s6, '\{', '\\{')"/>
    <xsl:variable name="s8" select="replace($s7, '\}', '\\}')"/>
    <xsl:variable name="s9" select="replace($s8, '~', '\\textasciitilde{}')"/>
    <xsl:variable name="s10" select="replace($s9, '\^', '\\textasciicircum{}')"/>
    <xsl:variable name="s11" select="replace($s10, '&#x23AF;', '&#x2014;')"/>
    <xsl:sequence select="$s11"/>
  </xsl:function>

  <!-- ============================================================
       Concatène le texte "reg" d'une séquence de <choice>, en ne
       gardant que <reg> (jamais <orig>).
       - un <reg/> vide est simplement ignoré (mot/segment non
         régularisé, souvent barré ou illisible dans le manuscrit) ;
       - si un fragment se termine par un tiret de coupure de mot
         "-" ou par le signe de continuation "¬" utilisé dans ce
         témoin, on NE remet PAS d'espace avant le fragment suivant,
         pour ne pas couper le mot qui continue sur la ligne/page
         suivante ; sinon on insère une espace simple entre les
         fragments.
       ============================================================ -->
  <xsl:function name="my:join-choices" as="xs:string">
    <xsl:param name="choices" as="element()*"/>
    <xsl:choose>
      <xsl:when test="empty($choices)">
        <xsl:sequence select="''"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="first" select="$choices[1]"/>
        <xsl:variable name="rest" select="$choices[position() gt 1]"/>
        <xsl:variable name="raw" select="normalize-space($first/tei:reg)"/>
        <xsl:variable name="clean" select="if ($raw = '') then '' else my:escape-latex(normalize-unicode($raw, 'NFC'))"/>
        <xsl:variable name="tail" select="my:join-choices($rest)"/>
        <xsl:choose>
          <xsl:when test="$clean = ''">
            <xsl:sequence select="$tail"/>
          </xsl:when>
          <xsl:when test="ends-with($clean, '-') or ends-with($clean, '¬') or $tail = ''">
            <xsl:sequence select="concat($clean, $tail)"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:sequence select="concat($clean, ' ', $tail)"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:function>

  <!-- ============================================================
       Racine : squelette du document LaTeX
       ============================================================ -->
  <xsl:template match="/tei:TEI">
    <xsl:text>% Fichier généré automatiquement depuis le TEI (contenu des &lt;reg&gt; uniquement)&#10;</xsl:text>
    <xsl:text>\documentclass[12pt]{article}&#10;</xsl:text>
    <xsl:text>\usepackage{fontspec} % compiler avec xelatex (ou lualatex si polyglossia y est installé)&#10;</xsl:text>
    <xsl:text>\usepackage{polyglossia}&#10;</xsl:text>
    <xsl:text>\setmainlanguage{french}&#10;</xsl:text>
    <xsl:text>\usepackage[margin=2.5cm]{geometry}&#10;</xsl:text>
    <xsl:text>\usepackage{parskip}&#10;</xsl:text>
    <xsl:text>\usepackage{reledmac} % numérotation automatique des lignes du PDF&#10;</xsl:text>
    <xsl:text>\firstlinenum{1}&#10;</xsl:text>
    <xsl:text>\linenumincrement{5}&#10;</xsl:text>
    <xsl:text>\title{</xsl:text>
    <xsl:value-of select="my:escape-latex(normalize-space(.//tei:titleStmt/tei:title))"/>
    <xsl:text>}&#10;</xsl:text>
    <xsl:variable name="subtitle" select="normalize-space(.//tei:publicationStmt/tei:p)"/>
    <xsl:if test="$subtitle != ''">
      <xsl:text>\date{</xsl:text>
      <xsl:value-of select="my:escape-latex($subtitle)"/>
      <xsl:text>}&#10;</xsl:text>
    </xsl:if>
    <xsl:text>\author{}&#10;</xsl:text>
    <xsl:text>\begin{document}&#10;</xsl:text>
    <xsl:text>\maketitle&#10;&#10;</xsl:text>
    <xsl:text>\beginnumbering&#10;</xsl:text>
    <xsl:apply-templates select=".//tei:text/tei:body"/>
    <xsl:text>\endnumbering&#10;&#10;</xsl:text>
    <xsl:text>\end{document}&#10;</xsl:text>
  </xsl:template>

  <!-- une <div> = une page du manuscrit -->
  <xsl:template match="tei:body">
    <xsl:apply-templates select="tei:div"/>
  </xsl:template>

  <xsl:template match="tei:div">
    <xsl:apply-templates select="tei:head"/>
    <xsl:apply-templates select="tei:p"/>
  </xsl:template>

  <!-- un head peut être encodé en <choice><orig/><reg/></choice>
       (rare, variantes orthographiques) ou en simple texte
       (cas le plus fréquent : millésimes "1792.", etc.) -->
  <xsl:template match="tei:head">
    <xsl:variable name="txt">
      <xsl:choose>
        <xsl:when test=".//tei:choice">
          <xsl:value-of select="my:join-choices(.//tei:choice)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="my:escape-latex(normalize-unicode(normalize-space(.), 'NFC'))"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:if test="$txt != ''">
      <xsl:text>\subsection*{</xsl:text>
      <xsl:value-of select="$txt"/>
      <xsl:text>}&#10;&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="tei:p">
    <xsl:variable name="txt" select="my:join-choices(.//tei:choice)"/>
    <xsl:if test="$txt != ''">
      <xsl:text>\pstart&#10;</xsl:text>
      <xsl:value-of select="$txt"/>
      <xsl:text>&#10;\pend&#10;&#10;</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- tout le reste (teiHeader, facsimile, xenoData...) est ignoré -->
  <xsl:template match="text()"/>

</xsl:stylesheet>
