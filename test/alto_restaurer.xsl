<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:alto="http://www.loc.gov/standards/alto/ns-v4#">

  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>

  <!-- ============================================================
       XSLT 2/2 : RESTAURER
       - Relit les commentaires <!--BASELINE:...--> et les remet
         comme attribut BASELINE sur la TextLine
       - Relit les commentaires <!--SHAPE:...--> et reconstruit
         l'élément <Shape><Polygon POINTS="..."/></Shape>
       ============================================================ -->

  <!-- Règle par défaut : copie tout à l'identique -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Sur chaque TextLine : restaure l'attribut BASELINE depuis le commentaire -->
  <xsl:template match="alto:TextLine">
    <xsl:copy>
      <!-- Copie les attributs existants -->
      <xsl:apply-templates select="@*"/>
      <!-- Restaure BASELINE depuis le commentaire enfant -->
      <xsl:for-each select="comment()[starts-with(normalize-space(.), 'BASELINE:')]">
        <xsl:attribute name="BASELINE">
          <xsl:value-of select="normalize-space(substring-after(., 'BASELINE:'))"/>
        </xsl:attribute>
      </xsl:for-each>
      <!-- Copie les enfants (les commentaires BASELINE et SHAPE seront traités) -->
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Supprime les commentaires BASELINE (devenus attributs) -->
  <xsl:template match="comment()[starts-with(normalize-space(.), 'BASELINE:')]"/>

  <!-- Reconstruit <Shape><Polygon .../></Shape> depuis le commentaire SHAPE -->
  <xsl:template match="comment()[starts-with(normalize-space(.), 'SHAPE:')]">
    <xsl:element name="Shape" namespace="http://www.loc.gov/standards/alto/ns-v4#">
      <xsl:element name="Polygon" namespace="http://www.loc.gov/standards/alto/ns-v4#">
        <xsl:attribute name="POINTS">
          <xsl:value-of select="normalize-space(substring-after(., 'SHAPE:'))"/>
        </xsl:attribute>
      </xsl:element>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
