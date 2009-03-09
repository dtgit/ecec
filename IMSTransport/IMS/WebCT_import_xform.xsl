<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:imscp="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:fn="http://www.w3.org/2005/02/xpath-functions"
    xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2"                
    xmlns:cwsp="http://www.dspace.org/xmlns/cwspace_imscp"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
    xmlns:ocw="http://ocw.mit.edu/xmlns/ocw_imscp"
    xmlns:eduCommons="http://cosl.usu.edu/xsd/eduCommonsv1.2"
    xmlns:imsct="http://www.imsproject.org/content"
    xmlns:lom="http://www.imsproject.org/metadata"
    xmlns:webct="http://www.webct.com/IMS"
    xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p2.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd http://cosl.usu.edu/xsd/eduCommonsv1.2 eduCommonsv1.2.xsd">

    <xsl:output method="xml" indent="yes" />
    
    <xsl:template match="/imsct:manifest">
        <manifest>
            <xsl:attribute name="version">
                <xsl:text>1.0</xsl:text>
            </xsl:attribute>
            <xsl:attribute name="identifier">
                <xsl:value-of select="@identifier"/>
            </xsl:attribute>
            <xsl:attribute name="xsi:schemaLocation">
                <xsl:text>http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p2.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd http://cosl.usu.edu/xsd/eduCommonsv1.2 eduCommonsv1.2.xsd</xsl:text>
            </xsl:attribute>
            <metadata>
                <xsl:value-of select="unparsed-entity-uri('http://www.google.com')"/>
                <schema>IMS Content</schema>
                <schemaversion>1.2</schemaversion>
                <xsl:call-template name="general" >
                    <xsl:with-param name="title" select="imsct:metadata/lom:lom/lom:general/lom:title/lom:langstring"/>
                    <xsl:with-param name="identifier" select="@identifier"/>
                </xsl:call-template>
            </metadata>
            <organizations>
                <organization>
                    <xsl:attribute name="identifier">
                        <xsl:value-of select="imsct:organizations/imsct:organization/@identifier"/>
                    </xsl:attribute>
                    <xsl:apply-templates select=".//imsct:manifest">
                        <xsl:with-param name="section" select="'organizations'"/>
                    </xsl:apply-templates>
                 </organization>
            </organizations>
            <resources>
            <xsl:apply-templates select=".//imsct:manifest">
                <xsl:with-param name="section" select="'resources'"/>
            </xsl:apply-templates>
             </resources>
        </manifest>
    </xsl:template>
  
    
    <xsl:template match="imsct:manifest">
        <xsl:param name="section"/>
        <xsl:variable name="manifest_type" select="imsct:metadata//lom:learningresourcetype/lom:value/lom:langstring"/>
        <xsl:variable name="manifest_title" select="imsct:metadata//lom:title/lom:langstring"/>
        <xsl:variable name="manifest_id" select="@identifier"/>
        
        <xsl:if test="$manifest_type='Content Module' ">
            <xsl:call-template name="resource">
                <xsl:with-param name="section" select="$section"/>
                <xsl:with-param name="title" select="$manifest_title"/>
                <xsl:with-param name="file_name" select="concat($manifest_id,'.html')"/>
                <xsl:with-param name="isvis" select="//imsct:item[@identifierref=$manifest_id]/@isvisible"/>
             </xsl:call-template>
        </xsl:if>
        
        <xsl:apply-templates select="imsct:resources/imsct:resource">
            <xsl:with-param name="manifest_type" select="$manifest_type"/>
            <xsl:with-param name="manifest_title" select="$manifest_title"/>
            <xsl:with-param name="section" select="$section"/>
            <xsl:with-param name="manifest_id" select="$manifest_id"/>
        </xsl:apply-templates>
    </xsl:template>    
 
    
    
    <xsl:template match="imsct:resources/imsct:resource">
        <xsl:param name="manifest_title"/>
        <xsl:param name="manifest_type"/>
        <xsl:param name="section"/>
        <xsl:param name="manifest_id"/>
        <xsl:variable name="identifier" select="@identifier"/>
        <xsl:if test="imsct:file">
            <xsl:if test="imsct:file/@href != ''">
            <xsl:choose>
                <xsl:when test="$manifest_type='Glossary'">
                    <xsl:call-template name="Glossary">
                        <xsl:with-param name="manifest_title" select="$manifest_title"/>
                        <xsl:with-param name="manifest_id" select="$manifest_id"/>
                        <xsl:with-param name="section" select="$section"/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:when test="$manifest_type='Image Database'">
                    <xsl:apply-templates select="imsct:file">
                        <xsl:with-param name="section" select="$section"/>
                        <xsl:with-param name="manifest_type" select="$manifest_type"/>
                        <xsl:with-param name="manifest_id" select="$manifest_id"/>
                        <xsl:with-param name="manifest_title" select="$manifest_title"/>
                        <xsl:with-param name="database" select="@href"/>
                    </xsl:apply-templates>
                </xsl:when>
                <!--xsl:when test="$manifest_type='Organizer Page'">
                    <xsl:call-template name="OrgPage"/>
                </xsl:when-->
                <xsl:when test="$manifest_type='Single Page'">
                    <xsl:call-template name="SinglePage">
                        <xsl:with-param name="manifest_title" select="$manifest_title"/>
                        <xsl:with-param name="manifest_id" select="$manifest_id"/>
                        <xsl:with-param name="section" select="$section"/>                        
                    </xsl:call-template>
                </xsl:when>
                <xsl:when test="$manifest_type='Content Module'">
                    <xsl:call-template name="ContentModule">
                        <xsl:with-param name="manifest_title" select="$manifest_title"/>
                        <xsl:with-param name="manifest_id" select="$manifest_id"/>
                        <xsl:with-param name="section" select="$section"/>                        
                    </xsl:call-template>
                </xsl:when>
                <xsl:when test="$manifest_type='URL' ">
                    <xsl:call-template name="URL">
                        <xsl:with-param name="manifest_title" select="$manifest_title"/>
                        <xsl:with-param name="manifest_id" select="$manifest_id"/>
                        <xsl:with-param name="manifest_type" select="$manifest_type"/>
                        <xsl:with-param name="section" select="$section"/>     
                    </xsl:call-template>
                </xsl:when>
            </xsl:choose>
        </xsl:if>
        </xsl:if>    
    </xsl:template>
    
    
    
    <xsl:template name="ContentModule">
        <xsl:param name="section"/>
        <xsl:param name="manifest_title"/>
        <xsl:param name="manifest_id"/>
        <xsl:variable name="identifier" select="@identifier"/>
        <xsl:if test="@type='webcontent'">        
            <xsl:call-template name="resource">
                <xsl:with-param name="section" select="$section"/>
                <xsl:with-param name="title" select="//imsct:item[@identifierref=$identifier]/imsct:title"/>
                <xsl:with-param name="file_name">
                    <xsl:call-template name="ChangeExtension">
                        <xsl:with-param name="file_name" select="imsct:file/@href"/>
                    </xsl:call-template>
                </xsl:with-param>
                <xsl:with-param name="isvis" select="'false'"/>                
            </xsl:call-template>    
        </xsl:if>
    </xsl:template>
    
    
    <xsl:template name="Glossary">
        <xsl:param name="section"/>
        <xsl:param name="manifest_title"/>
        <xsl:param name="manifest_id"/>
        <xsl:call-template name="resource">
            <xsl:with-param name="section" select="$section"/>
            <xsl:with-param name="title" select="$manifest_title"/>
            <xsl:with-param name="file_name">
                <xsl:call-template name="ChangeExtension">
                    <xsl:with-param name="file_name" select="imsct:file/@href"/>
                </xsl:call-template>
            </xsl:with-param>
            <xsl:with-param name="isvis" select="//imsct:item[@identifierref=$manifest_id]/@isvisible"/>                
        </xsl:call-template>
    </xsl:template>
    
    
    <xsl:template match="imsct:file">
        <xsl:param name="section"/>
        <xsl:param name="manifest_type"/>
        <xsl:param name="manifest_id"/>
        <xsl:param name="manifest_title"/>
        <xsl:param name="database"/>
        
        <xsl:if test="$manifest_type='Image Database'">
            <xsl:variable name="title">
                <xsl:choose>
                    <xsl:when test="@href = $database">
                        <xsl:value-of select="$manifest_title"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:call-template name="getTitle">
                            <xsl:with-param name="file_path" select="@href"/>
                        </xsl:call-template> 
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:variable name="isvis">
                <xsl:choose>
                    <xsl:when test="@href = $database">
                        <xsl:value-of select="//imsct:item[@identifierref=$manifest_id]/@isvisible"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="'false'"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:call-template name="resource">
                <xsl:with-param name="section" select="$section"/>
                <xsl:with-param name="manifest_type" select="$manifest_type"/>
                <xsl:with-param name="title" select="$title"/>
                <xsl:with-param name="file_name">
                    <xsl:call-template name="ChangeExtension">
                        <xsl:with-param name="file_name" select="@href"/>
                    </xsl:call-template>
                </xsl:with-param>
                <xsl:with-param name="isvis" select="$isvis"/>                
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
    
    <xsl:template name="getTitle">
        <xsl:param name="file_path"/>
        <xsl:variable name="rfile_path">
            <xsl:call-template name="reverse3">
                <xsl:with-param name="theString" select="@href"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="trim_rfile_path" select="substring-before($rfile_path,'/')"/>
        <xsl:variable name="file_name">
            <xsl:choose>
                <xsl:when test="$trim_rfile_path">
                    <xsl:call-template name="reverse3">
                        <xsl:with-param name="theString" select="$trim_rfile_path"/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="reverse3">
                        <xsl:with-param name="theString" select="$rfile_path"/>
                    </xsl:call-template>
                </xsl:otherwise>
            </xsl:choose>    
        </xsl:variable>
        <xsl:variable name="wext_file_name" select="substring-before($file_name,'.')"/>
        <xsl:choose>
            <xsl:when test="$wext_file_name">
                <xsl:value-of select="$wext_file_name"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$file_name"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    
    <xsl:template name="reverse3">
        <xsl:param name="theString" />
        <xsl:param name="reversedString" />
        <xsl:choose>
            <xsl:when test="$theString">
                <xsl:call-template name="reverse3">
                    <xsl:with-param name="theString"
                        select="substring($theString, 2)" />
                    <xsl:with-param name="reversedString"
                        select="concat(substring($theString, 1, 1),
                        $reversedString)" />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$reversedString" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    
    <xsl:template name="ChangeExtension">
        <xsl:param name="file_name"/>
        <xsl:choose>
            <xsl:when test="substring($file_name,string-length($file_name)-3,4)='.xml'">
                <xsl:value-of select="concat(substring($file_name,1,string-length($file_name)-4),'.html')"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$file_name"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    
    <xsl:template name="OrgPage"/>

    
 
    <xsl:template name="URL">
        <xsl:param name="section"/>
        <xsl:param name="manifest_title"/>
        <xsl:param name="manifest_id"/>
        <xsl:param name="manifest_type"/>
        <xsl:call-template name="resource">
            <xsl:with-param name="section" select="$section"/>
            <xsl:with-param name="file_name" select="concat(@identifier,'.html') "/>                        
            <xsl:with-param name="title" select="$manifest_title"/>
            <xsl:with-param name="manifest_type" select="$manifest_type"/>
            <xsl:with-param name="isvis" select="//imsct:item[@identifierref=$manifest_id]/@isvisible"/>
        </xsl:call-template>
    </xsl:template>    
    
    
    <xsl:template name="SinglePage">
        <xsl:param name="section"/>
        <xsl:param name="manifest_title"/>
        <xsl:param name="manifest_id"/>
        <xsl:call-template name="resource">
            <xsl:with-param name="section" select="$section"/>
            <xsl:with-param name="file_name">
                <xsl:call-template name="ChangeExtension">
                    <xsl:with-param name="file_name" select="imsct:file/@href"/>
                </xsl:call-template>
            </xsl:with-param>            
            <xsl:with-param name="title" select="$manifest_title"/>
            <xsl:with-param name="isvis" select="//imsct:item[@identifierref=$manifest_id]/@isvisible"/>
        </xsl:call-template>
    </xsl:template>
    
    
    <xsl:template name="resource">
        <xsl:param name="section"/>
        <xsl:param name="title"/>
        <xsl:param name="file_name"/>
        <xsl:param name="manifest_type"/>
        <xsl:param name="isvis"/>
        <xsl:variable name="res_id" select="generate-id()"/>
        <xsl:variable name="org_id" select="concat($res_id,'_O')"/>
        <xsl:choose>
            <xsl:when test="$section='resources'">
                <xsl:call-template name="res_resource">
                    <xsl:with-param name="title" select="$title"/>
                    <xsl:with-param name="identifier" select="$res_id"/>
                    <xsl:with-param name="file_name" select="$file_name"/>
                    <xsl:with-param name="manifest_type" select="$manifest_type"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:when test="$section='organizations' ">
                <xsl:call-template name="org_item">
                    <xsl:with-param name="title" select="$title"/>
                    <xsl:with-param name="isvis" select="$isvis"/>
                    <xsl:with-param name="identifier" select="$org_id"/>
                    <xsl:with-param name="identifierref" select="$res_id"/>
                </xsl:call-template>
            </xsl:when>
        </xsl:choose> 
    </xsl:template>
    
    
    
    <xsl:template name="res_resource">
        <xsl:param name="identifier"/>
        <xsl:param name="title"/>
        <xsl:param name="file_name"/>
        <xsl:param name="manifest_type"/>
        <resource>
            <xsl:attribute name="identifier">
                <xsl:value-of select="$identifier"/>
            </xsl:attribute>
            <xsl:attribute name="type">
                <xsl:choose>
                    <xsl:when test="$manifest_type='URL' ">
                        <xsl:value-of select="'external link'"/>
                    </xsl:when>
                    <xsl:otherwise>
                         <xsl:text>webcontent</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <metadata>
                <imsmd:lom>
                    <xsl:call-template name="general">
                        <xsl:with-param name="title" select="$title"/>
                        <xsl:with-param name="identifier" select="$identifier"/>
                    </xsl:call-template>
                </imsmd:lom>
                <eduCommons:eduCommons>
                    <eduCommons:license category="Site Default"/>
                    <eduCommons:clearedCopyright>false</eduCommons:clearedCopyright>
                    <eduCommons:accessible>false</eduCommons:accessible>
                </eduCommons:eduCommons>
            </metadata>
                <file>
                    <xsl:attribute name="href">
                        <xsl:value-of select="$file_name"/>
                    </xsl:attribute>
               </file>
        </resource>    
    </xsl:template>

    
    <xsl:template name="org_item">
        <xsl:param name="title"/>
        <xsl:param name="identifier"/>
        <xsl:param name="isvis"/>
        <xsl:param name="identifierref"/>
        <item>   
            <xsl:attribute name="identifier">
                <xsl:value-of select="$identifier"/>      
            </xsl:attribute>
            <xsl:attribute name="identifierref">
                <xsl:value-of select="$identifierref"/>
            </xsl:attribute>
            <xsl:attribute name="isvisible" >
                <xsl:value-of select="$isvis"/>
            </xsl:attribute>      
            <title>
                <xsl:value-of select="$title"/>
            </title>
        </item>
    </xsl:template>

    
    <xsl:template name="general">
        <xsl:param name="title"/>
        <xsl:param name="identifier"/>
        <imsmd:general>
            <imsmd:identifier>
                <xsl:value-of select="$identifier"/>
            </imsmd:identifier>
            <imsmd:title>
                <imsmd:langstring xml:lang="en">
                    <xsl:value-of select="$title"/>                            
                </imsmd:langstring>                 
            </imsmd:title>
        </imsmd:general>
    </xsl:template>
    
</xsl:stylesheet>
