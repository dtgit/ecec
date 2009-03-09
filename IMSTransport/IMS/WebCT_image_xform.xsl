<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:fn="http://www.w3.org/2005/02/xpath-functions" xmlns:didl="http://www.mpeg.org/mpeg-21/2002/01-DIDL-NS" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    
    <xsl:template match="/">
        <html><head/>
        <body>
        <table class="documentTable" style="width: 499px;" border="0" cellpadding="0" cellspacing="0">
            <thead><tr><td>
                <xsl:value-of select="'Images'"/>
            </td></tr></thead>
            <tbody>
        <xsl:apply-templates select="didl:DIDL/didl:CONTAINER/didl:ITEM"/>
                </tbody>
         </table>
        </body>    
        </html>
    </xsl:template>
    
    <xsl:template match="didl:DIDL/didl:CONTAINER/didl:ITEM">

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
                <a>
                    <xsl:attribute name="href">
                        <xsl:value-of select="didl:COMPONENT/didl:RESOURCE/@REF"/>
                    </xsl:attribute>
                    <xsl:value-of select="didl:DESCRIPTOR/didl:DESCRIPTOR/didl:STATEMENT"/>
                </a>
             </td></tr>
    </xsl:template>
    
    <xsl:template match="didl:COMPONENT">
     </xsl:template>
        
    
</xsl:stylesheet>
