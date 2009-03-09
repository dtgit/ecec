<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:fn="http://www.w3.org/2005/02/xpath-functions" xmlns:webct="http://www.webct.com/IMS" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    
    <xsl:template match="/">
        <html><head/>
        <body>
        <table class="documentTable" style="width: 499px;" border="0" cellpadding="0" cellspacing="0">
            <thead>
            <tr><td>
                <xsl:value-of select="'keyword'"/>
            </td><td>
                    <xsl:value-of select="'definition'"/>
                </td></tr>
            </thead>
            <tbody>
        <xsl:apply-templates select="webct:glossary/webct:gloss"/>
                </tbody>
         </table>
        </body>    
        </html>
    </xsl:template>
    
    <xsl:template match="webct:glossary/webct:gloss">

            <tr>
                <xsl:attribute name="class">
                    <xsl:choose>
                        <xsl:when test="position() mod 2 = 1">
                            <xsl:value-of select="'odd'"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="'even'"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
                <td>
                <xsl:value-of select="webct:keyword"/>
                </td><td>
                    <xsl:value-of select="webct:definition"/>
             </td></tr>
    </xsl:template>       
    
</xsl:stylesheet>
