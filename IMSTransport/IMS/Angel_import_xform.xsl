<?xml version="1.0" encoding="UTF-8"?>

   
    <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
        xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
        xmlns:imscp="http://www.imsglobal.org/xsd/imscp_v1p1"
        xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"
        xmlns:lom="http://ocw.mit.edu/xmlns/LOM"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:eduCommons="http://cosl.usu.edu/xsd/eduCommonsv1.2"
        xmlns:cwsp="http://www.dspace.org/xmlns/cwspace_imscp"
        xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
        xmlns:ocw="http://ocw.mit.edu/xmlns/ocw_imscp"
        version="1.0">   
    
    
    
    <xsl:output method="xml" indent="yes" />
        
    <xsl:template match="/">
        <manifest xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p2.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd http://cosl.usu.edu/xsd/eduCommonsv1.2 eduCommonsv1.2.xsd">
            <xsl:attribute name="identifier">
                <xsl:value-of select="manifest/@identifier"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </manifest>        
    </xsl:template>
    
        <xsl:template match="manifest/organizations">
            <organizations>
                <xsl:attribute name="default">     
                    <xsl:value-of select="@default"/>
                </xsl:attribute>
                <xsl:apply-templates/>
            </organizations>
        </xsl:template>       

        <xsl:template match="organization">
            <organization>
                <xsl:attribute name="identifier">
                    <xsl:value-of select = "@identifier" />
                </xsl:attribute>
                <xsl:apply-templates/>
            </organization>
        </xsl:template>        
        
        <xsl:template match="title">
            <title>
                <xsl:value-of select="."/>
            </title>
        </xsl:template>
        
        <xsl:template match="item">
            <item>
                <xsl:variable name="identifierref" select="@identifierref"/>
                <xsl:variable name="resource" select="/manifest/resources//resource[@identifier=$identifierref]/@href"/>
                <xsl:variable name="ext" select="substring-after($resource,'.')"/>
                
                <xsl:attribute name="identifier">
                    <xsl:value-of select = "@identifier" />
                </xsl:attribute>
                <xsl:attribute name="identifierref">
                    <xsl:value-of select = "$identifierref" />
                    <xsl:value-of select="concat('.',$ext)"/>                    
                </xsl:attribute>
                <xsl:attribute name="isvisible">
                     <xsl:text>true</xsl:text>
                 </xsl:attribute>
                <xsl:apply-templates/>
            </item>
        </xsl:template>
        
        <xsl:template match="resources">
            <resources>
                <xsl:apply-templates />
            </resources>   
        </xsl:template>
        
        <xsl:template match="resource">
            <resource>
                
                
                <xsl:variable name="identifier" select="@identifier"/>
                <xsl:variable name="title" select="/manifest/organizations//item[@identifierref=$identifier]/title"/>
                
                <xsl:attribute name="identifier">
                    <xsl:value-of select="concat(@identifier,'.',substring-after(@href,'.'))"/>
                </xsl:attribute>
                <xsl:attribute name="href">
                    <xsl:value-of select="@href"/>
                </xsl:attribute>
                <xsl:attribute name="type">
                    <xsl:value-of select="@type"/>
                </xsl:attribute>
                
                <metadata>
                    <imsmd:lom>
                        <imsmd:general>
                            <imsmd:title>
                                <imsmd:langstring xml:lang="en">
                                           <xsl:value-of select="$title"/>
                                </imsmd:langstring>
                            </imsmd:title>
                        </imsmd:general>
                        <imsmd:technical>
                            
                        </imsmd:technical>
                    </imsmd:lom>
                    <eduCommons:eduCommons>
                        <xsl:if test="$title='Welcome'">
                            <eduCommons:objectType>
                                Course
                            </eduCommons:objectType>
                        </xsl:if>
                        <eduCommons:license category="Site Default"/>
                        <eduCommons:clearedCopyright>true</eduCommons:clearedCopyright>
                    </eduCommons:eduCommons>
                </metadata>
                
                
                
                <xsl:apply-templates select="file" />
            </resource>
        </xsl:template>
        

        <xsl:template match="file">
            <file>
                <xsl:attribute name="href">
                    <xsl:value-of select="translate(@href,'\','/')"/>
                </xsl:attribute>
            </file>
        </xsl:template>
        
        
        
</xsl:stylesheet>
