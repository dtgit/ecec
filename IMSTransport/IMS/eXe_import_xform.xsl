<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    version="1.0"
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:imscp="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
    xmlns:eduCommons="http://cosl.usu.edu/xsd/eduCommonsv1.2">
   
    <xsl:output method="xml" indent="yes"/>
    
    <xsl:template match="/">
        <manifest xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p2.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd http://cosl.usu.edu/xsd/eduCommonsv1.2 http://cosl.usu.edu/xsd/educommonsv1.2.xsd">
            <xsl:attribute name="identifier">
                <xsl:value-of select="imscp:manifest/@identifier"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </manifest>
    </xsl:template>
    
    <xsl:template match="imscp:metadata">
        <metadata>
            <schema>IMS Content</schema>
            <schemaversion>1.2</schemaversion>
        </metadata>
    </xsl:template>
    
    <xsl:template match="imscp:organizations">
        <organizations>
            <xsl:apply-templates select="imscp:organization"/>
        </organizations>
    </xsl:template>
    
    <xsl:template match="imscp:organization">
        <organization>
            <xsl:attribute name="identifier">
                <xsl:value-of select="@identifier"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </organization>
    </xsl:template>
    
    <xsl:template match="imscp:title">
        <title>
            <xsl:value-of select="."/>
        </title>
    </xsl:template>
    
    <xsl:template match="imscp:item">
        <item>
            <xsl:attribute name="identifier">
                <xsl:value-of select="@identifier"/>
            </xsl:attribute>
            <xsl:attribute name="identifierref">
                <xsl:value-of select="@identifierref"/>
            </xsl:attribute>
            <xsl:attribute name="isvisible">
                <xsl:value-of select="@isvisible"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </item>
    </xsl:template>
    
    <xsl:template match="imscp:resources">
        <resources>
            <xsl:apply-templates select="imscp:resource"/>
        </resources>
    </xsl:template>
    
    <xsl:template match="imscp:resource">
        <xsl:variable name="identifier" select="@identifier"/>
        <xsl:variable name="title" select="/imscp:manifest/imscp:organizations//imscp:item[@identifierref=$identifier]/imscp:title"/>
        <xsl:variable name="restype" select="@type"/>
        <xsl:variable name="reshref" select="@href"/>
        <xsl:for-each select="imscp:file">
            <resource>
                <xsl:choose>
                    <xsl:when test="@href=$reshref">
                        <xsl:attribute name="identifier">
                            <xsl:value-of select="$identifier"/>
                        </xsl:attribute>
                        <xsl:attribute name="type">
                            <xsl:value-of select="$restype"/>
                        </xsl:attribute>
                        <xsl:attribute name="href">
                            <xsl:value-of select="@href"/>
                        </xsl:attribute>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:attribute name="identifier">
                            <xsl:value-of select="concat('RES', generate-id())"/>
                        </xsl:attribute>
                        <xsl:attribute name="type">
                            <xsl:text>unknown</xsl:text>
                        </xsl:attribute>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:choose>
                    <xsl:when test="@href=$reshref">
                        <metadata>
                            <imsmd:lom>
                                <imsmd:general>
                                    <imsmd:title>
                                        <imsmd:langstring xml:lang="en">
                                            <xsl:value-of select="$title"/>
                                        </imsmd:langstring>
                                    </imsmd:title>
                                </imsmd:general>
                            </imsmd:lom>
                            <xsl:choose>
                                <xsl:when test="$title='Home'">
                                    <eduCommons:eduCommons>
                                        <eduCommons:objectType>Course</eduCommons:objectType>
                                        <eduCommons:license category="Site Default"/>
                                        <eduCommons:clearedCopyright>false</eduCommons:clearedCopyright>
                                    </eduCommons:eduCommons>
                                </xsl:when>
                            </xsl:choose>
                        </metadata>
                    </xsl:when>
                    <xsl:otherwise>
                        <metadata>
                            <imsmd:lom>
                            <imsmd:general>
                                <imsmd:title>
                                    <imsmd:langstring xml:lang="en">
                                        <xsl:value-of select="@href"/>
                                    </imsmd:langstring>
                                </imsmd:title>
                            </imsmd:general>
                            </imsmd:lom>
                            <eduCommons:eduCommons>
                                <eduCommons:license category="Site Default"/>
                                <eduCommons:clearedCopyright>false</eduCommons:clearedCopyright>
                            </eduCommons:eduCommons>
                        </metadata>
                    </xsl:otherwise>
                </xsl:choose>
                <file>
                    <xsl:attribute name="href">
                        <xsl:value-of select="@href"/>
                    </xsl:attribute>
                </file>
            </resource>
        </xsl:for-each>
    </xsl:template>
    
   
</xsl:stylesheet>
