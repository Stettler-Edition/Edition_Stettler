<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:alto="http://www.loc.gov/standards/alto/ns-v4#">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>

  <!-- ============================================================
       XSLT 1/2 : ALLÉGER
       - Convertit <Shape><Polygon POINTS="..."/></Shape> en commentaire XML
       - Déplace l'attribut BASELINE dans un commentaire sur la TextLine
       Pour restaurer l'original, utiliser alto_restaurer.xsl
       ============================================================ -->

  <!-- Règle par défaut : copie tout à l'identique -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Sur chaque TextLine : copie l'élément mais sans l'attribut BASELINE,
       et insère un commentaire contenant le BASELINE avant le contenu -->
  <xsl:template match="alto:TextLine">
    <xsl:copy>
      <!-- Copie tous les attributs SAUF BASELINE -->
      <xsl:apply-templates select="@*[not(name() = 'BASELINE')]"/>
      <!-- Stocke BASELINE dans un commentaire pour pouvoir le restaurer -->
      <xsl:if test="@BASELINE">
        <xsl:comment>BASELINE:<xsl:value-of select="@BASELINE"/></xsl:comment>
      </xsl:if>
      <!-- Copie les éléments enfants (Shape sera traité par sa propre règle) -->
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Convertit <Shape> en commentaire XML -->
  <xsl:template match="alto:Shape">
    <xsl:comment>SHAPE:<xsl:value-of select="alto:Polygon/@POINTS"/></xsl:comment>
  </xsl:template>

</xsl:stylesheet>
