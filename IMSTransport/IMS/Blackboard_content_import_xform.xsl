<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    
    <xsl:output method="html" indent="yes"/>
    
    <xsl:template match="/CONTENT">
        <xsl:variable name="content_type" select="CONTENTHANDLER/@value"/>
        <xsl:choose>
            <xsl:when test="$content_type = 'resource/x-bb-document' or $content_type = 'resource/x-bb-assignment'">
                <xsl:value-of select="BODY/TEXT" disable-output-escaping="yes"/>
                <p>
                    <xsl:apply-templates select="FILES/FILE"/>
                </p>
            </xsl:when>
            <xsl:when test="$content_type = 'resource/x-bb-externallink'">
                <p>
                    <a>
                        <xsl:attribute name="href">
                            <xsl:value-of select="URL/@value"/>
                        </xsl:attribute>
                        <xsl:attribute name="title">
                            <xsl:value-of select="TITLE/@value"/>
                        </xsl:attribute>
                        <xsl:value-of select="TITLE/@value"/>
                    </a>
                </p>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="FILE">
        <a>
            <xsl:attribute name="href">
                <xsl:text>@X@LOCALFOLDERLOCATION@X@/</xsl:text>
                <xsl:value-of select="NAME"/>
            </xsl:attribute>
            <xsl:attribute name="title">
                <xsl:value-of select="LINKNAME/@value"/>
            </xsl:attribute>
            <xsl:value-of select="LINKNAME/@value"/>
        </a><br />    
    </xsl:template>
    
</xsl:stylesheet>
