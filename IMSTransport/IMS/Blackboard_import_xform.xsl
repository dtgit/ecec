<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    version="1.0"
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
    xmlns:bb="http://www.blackboard.com/content-packaging/">
    
    <xsl:output method="xml" indent="yes"/>
    
    <xsl:template match="/">
        <manifest xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p2.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p4.xsd http://cosl.usu.edu/xsd/eduCommonsv1.2 http://cosl.usu.edu/xsd/educommonsv1.2.xsd">
            <xsl:attribute name="identifier">
                <xsl:value-of select="manifest/@identifier"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </manifest>
    </xsl:template>
    
    <xsl:template match="organizations">
        <organizations>
            <xsl:apply-templates/>
        </organizations>
    </xsl:template>
    
    <xsl:template match="organization">
        <organization>
            <xsl:attribute name="identifier">
                <xsl:value-of select="@identifier"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </organization>
    </xsl:template>
    
    <xsl:template match="organization/item">
        <item>
            <xsl:attribute name="identifier">
                <xsl:value-of select="@identifier"/>
            </xsl:attribute>
            <xsl:attribute name="identifierref">
                <xsl:value-of select="@identifierref"/>
            </xsl:attribute>
            <xsl:attribute name="isvisible">
                <xsl:text>true</xsl:text>
            </xsl:attribute>
            <xsl:apply-templates/>
        </item>
    </xsl:template>
    
    <xsl:template match="item">
        <item>
            <xsl:attribute name="identifier">
                <xsl:value-of select="@identifier"/>
            </xsl:attribute>
            <xsl:attribute name="identifierref">
                <xsl:value-of select="@identifierref"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </item>
    </xsl:template>
    
    <xsl:template match="title">
        <title>
            <xsl:value-of select="."/>
        </title>
    </xsl:template>
    
    <xsl:template match="resources">
        <resources>
            <xsl:apply-templates select="resource"/>
        </resources>
    </xsl:template>
    
    <xsl:template match="resource">
        <xsl:variable name="identifier" select="@identifier"/>
        <xsl:variable name="title" select="/manifest/organizations//item[@identifierref=$identifier]/title"/>
        <xsl:variable name="visible" select="/manifest/organizations//item[@identifierref=$identifier]"/>
        <xsl:variable name="resid" select="@identifier"/>
        <xsl:variable name="restype" select="@type"/>
        <xsl:variable name="resbase" select="concat(@xml:base, '/')"/>
        <xsl:variable name="docfilename" select="concat(@xml:base, '.html')"/>
        <xsl:choose>
            <xsl:when test="$restype='resource/x-bb-document' or $visible">
                <resource>
                    <xsl:attribute name="identifier">
                        <xsl:choose>
                            <xsl:when test="$visible">
                                <xsl:value-of select="$identifier"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="generate-id()"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                    <xsl:attribute name="type">
                        <xsl:text>webcontent</xsl:text>
                    </xsl:attribute>
                    <metadata>
                        <imsmd:lom>
                            <imsmd:general>
                                <imsmd:title>
                                    <imsmd:langstring xml:base="en">
                                        <xsl:value-of select="$title"/>
                                    </imsmd:langstring>
                                </imsmd:title>
                            </imsmd:general>
                        </imsmd:lom>
                    </metadata>
                    <file>
                        <xsl:attribute name="href">
                            <xsl:value-of select="$docfilename"/>
                        </xsl:attribute>
                    </file>
                </resource>
            </xsl:when>
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="file">
                <xsl:for-each select="file">
                    <xsl:variable name="pos">
                        <xsl:number value="position()" format="1"/>
                    </xsl:variable>
                    <resource>
                        <xsl:choose>
                            <xsl:when test="$pos=1">
                                <xsl:attribute name="identifier">
                                    <xsl:value-of select="$resid"/>
                                </xsl:attribute>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:attribute name="identifier">
                                    <xsl:value-of select="generate-id()"/>
                                </xsl:attribute>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:attribute name="type">
                            <xsl:value-of select="$restype"/>
                        </xsl:attribute>
                        <metadata>
                            <imsmd:lom>
                                <imsmd:general>
                                    <imsmd:title>
                                        <imsmd:langstring xml:lang="en">
                                            <xsl:choose>
                                                <xsl:when test="$title">
                                                    <xsl:value-of select="$title"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="@href"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </imsmd:langstring>
                                    </imsmd:title>
                                </imsmd:general>    
                            </imsmd:lom>
                        </metadata>
                        <file>
                            <xsl:attribute name="href">
                                <xsl:value-of select="concat($resbase, translate(@href, '\', '/'))"/>
                            </xsl:attribute>
                        </file>
                    </resource>
                </xsl:for-each>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>
