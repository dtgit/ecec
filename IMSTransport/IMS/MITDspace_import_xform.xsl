<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:imscp="http://www.imsglobal.org/xsd/imscp_v1p1"
    xmlns:imsmd="http://www.imsglobal.org/xsd/imsmd_v1p2" xmlns:lom="http://ocw.mit.edu/xmlns/LOM"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:cwsp="http://www.dspace.org/xmlns/cwspace_imscp"
    xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
    xmlns:ocw="http://ocw.mit.edu/xmlns/ocw_imscp"
    xmlns:eduCommons="http://cosl.usu.edu/xsd/eduCommonsv1.2" version="1.0">

    <xsl:output method="xml" indent="yes"/>

    <xsl:template match="/">
        <manifest
            xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p2.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd">
            <xsl:attribute name="identifier">
                <xsl:value-of select="imscp:manifest/@identifier"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </manifest>
    </xsl:template>

    <xsl:template match="imscp:manifest/imscp:metadata">
        <metadata>
            <schema>IMS Content</schema>
            <schemaversion>1.2</schemaversion>
        </metadata>
    </xsl:template>

    <xsl:template match="imscp:manifest/imscp:organizations">
        <organizations>
            <xsl:attribute name="default">
                <xsl:value-of select="concat('ORG',@default)"/>
            </xsl:attribute>
            <xsl:apply-templates/>
        </organizations>
    </xsl:template>

    <xsl:template match="imscp:organization">
        <organization>
            <xsl:attribute name="identifier">
                <xsl:value-of select="concat('ORG',@identifier    )"/>
            </xsl:attribute>
            <xsl:apply-templates select="imscp:item"/>
        </organization>
    </xsl:template>

    <xsl:template match="imscp:title">
        <title>
            <xsl:value-of select="."/>
        </title>
    </xsl:template>

    <xsl:template match="imscp:item">
        <xsl:if test="@ocw:sectionTemplateType = 'CourseHomePage' ">
            <item identifier="indexitem" identifierref="index">
                <xsl:apply-templates select="imscp:title"/>
            </item>
        </xsl:if>
        <item>
            <xsl:attribute name="identifier">
                <xsl:value-of select="concat('ITM',generate-id())"/>
            </xsl:attribute>
            <xsl:attribute name="identifierref">
                <xsl:value-of select="@identifierref"/>
            </xsl:attribute>
            <xsl:choose>
                <xsl:when test="@ocw:sectionTemplateType and (@ocw:sectionTemplateType != '')">
                    <xsl:attribute name="isvisible">
                        <xsl:text>true</xsl:text>
                    </xsl:attribute>
                </xsl:when>
            </xsl:choose>
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
        <xsl:if test="/imscp:manifest/imscp:organizations//imscp:item[@identifierref=$identifier]/@ocw:sectionTemplateType = 'CourseHomePage' ">
            <resource identifier="index" type="webcontent">
                <metadata>
                    <imsmd:lom>
                        <imsmd:general>
                            <imsmd:identifier>index</imsmd:identifier>
                            <imsmd:title>
                                <imsmd:langstring xml:lang="x-none">
                                    <xsl:value-of select="imscp:metadata/lom:lom/lom:general/lom:title"/>
                                 </imsmd:langstring>
                            </imsmd:title>
                        </imsmd:general>
                    </imsmd:lom>
                    <eduCommons:eduCommons>
                        <eduCommons:objectType>Course</eduCommons:objectType>
                        <eduCommons:license category="Site Default"/>
                        <eduCommons:clearedCopyright>false</eduCommons:clearedCopyright>
                        <eduCommons:accessible>false</eduCommons:accessible>
                    </eduCommons:eduCommons>
                </metadata>
                <file href="index.html"/>
            </resource>
        </xsl:if>
        <xsl:apply-templates select="imscp:file"/>
    </xsl:template>
    
    
    <xsl:template match="imscp:file">
        <xsl:variable name="identifier" select="../@identifier"/>
        <xsl:variable name="filecount" select="count(../imscp:file)"/>
        <xsl:variable name="home" select="/imscp:manifest/imscp:organizations//imscp:item[@identifierref=$identifier]/@ocw:sectionTemplateType"/>
        <xsl:variable name="restype" select="../@type"/>
        <xsl:variable name="reshref" select="../@href"/>
        <xsl:variable name="title" select="../imscp:metadata/lom:lom/lom:general/lom:title"/>
        
        <xsl:variable name="fidentifier">
            <xsl:choose>
                <xsl:when test="$filecount > 1 and not ($reshref = @href)">
                    <xsl:value-of select="concat($identifier,generate-id())"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$identifier"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
                
        <resource>
            <xsl:attribute name="identifier">
                <xsl:value-of select="$fidentifier"/>
            </xsl:attribute>
            <xsl:attribute name="type">
                    <xsl:variable name="contenttype" select="../@type"/>
                    <xsl:choose>
                        <xsl:when test="$filecount > 1 and not ($reshref = @href) or string-length($contenttype) = 0">
                            <xsl:value-of select=" 'webcontent' "/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$contenttype"/>        
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:attribute>
             
            
                <metadata>
                    <imsmd:lom>
                        <imsmd:general>
                            <imsmd:identifier> 
                                <xsl:value-of select="$fidentifier"/>
                            </imsmd:identifier>                 
                            <imsmd:title>
                                <imsmd:langstring>
                                    <xsl:attribute name="xml:lang">
                                        <xsl:variable name="language" select="../imscp:metadata/lom:lom/lom:general/lom:title/lom:string/@language"/>
                                        <xsl:choose>
                                            <xsl:when test="string-length($language) = 0">
                                                <xsl:value-of select=" 'x-none' "/>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:value-of select="$language"/>        
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:attribute>
                                <xsl:choose>
                                    <xsl:when test="$filecount > 1 and not ($reshref = @href) or string-length($title)=0">
                                        <xsl:call-template name="getFilename">
                                            <xsl:with-param name="file_path" select="@href"/>
                                        </xsl:call-template>
                                    </xsl:when> 
                                    <xsl:otherwise>
                                        <xsl:value-of select="$title"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                </imsmd:langstring>
                            </imsmd:title>
                            

                            <xsl:apply-templates select="../imscp:metadata/lom:lom/lom:general/lom:language"/>
                            <xsl:apply-templates select="../imscp:metadata/lom:lom/lom:general/lom:description"/>
                            <xsl:apply-templates select="../imscp:metadata/lom:lom/lom:classification"/>
                        </imsmd:general>
                        
                            <xsl:apply-templates select="../imscp:metadata/lom:lom/lom:lifeCycle"/>
                            <xsl:apply-templates select="../imscp:metadata/lom:lom/lom:technical" />
                            <xsl:apply-templates select="../imscp:metadata/lom:lom/lom:rights"/>
                    </imsmd:lom>
                    <xsl:if test="$home='CourseHomePage' ">
                        <eduCommons:eduCommons>
                            <eduCommons:excludeFromNav>
                                true
                            </eduCommons:excludeFromNav>
                            <eduCommons:homePagePath>
                                    <xsl:variable name="base_dir" select="//@xml:base"/>
                                    <xsl:value-of select="concat($base_dir,@href) "/>
                            </eduCommons:homePagePath>
                        </eduCommons:eduCommons>
                      </xsl:if>  
                </metadata>
            
            <file>
                <xsl:attribute name="href">
                    <xsl:variable name="base_dir" select="//@xml:base"/>
                    <xsl:value-of select="concat($base_dir,@href) "/>
                </xsl:attribute>
            </file>
        </resource>
    </xsl:template>
    
    
    <!-- rules for the lom:rights section -->
    <xsl:template match="lom:rights">
        <imsmd:rights>
            <imsmd:copyrightandotherrestrictions>
                <imsmd:source>
                    <imsmd:langstring xml:lang="x-none">
                        <xsl:value-of select="lom:copyrightAndOtherRestrictions/lom:source"/>
                    </imsmd:langstring>
                </imsmd:source>
                <imsmd:value>
                    <imsmd:langstring xml:lang="x-none">
                        <xsl:value-of select="lom:copyrightAndOtherRestrictions/lom:value"/>
                    </imsmd:langstring>
                </imsmd:value>
            </imsmd:copyrightandotherrestrictions>
            <imsmd:description>
                <imsmd:langstring xml:lang="x-none">
                    <xsl:value-of select="lom:description/lom:string"/>
                </imsmd:langstring>
            </imsmd:description>
        </imsmd:rights>
    </xsl:template>
    
    <!-- rules for lom:technical section -->
    
    <xsl:template match="lom:technical">
        <imsmd:technical>
            <xsl:apply-templates select="lom:format"/>
            <xsl:apply-templates select="lom:size"/>
            <xsl:apply-templates select="lom:location"></xsl:apply-templates>
         </imsmd:technical>
    </xsl:template>
    
    <xsl:template match="lom:format">
        <imsmd:format>
            <xsl:value-of select="."/>
        </imsmd:format>
    </xsl:template>
    
    <xsl:template match="lom:size">
        <imsmd:size>
            <xsl:value-of select="."/>
        </imsmd:size>
    </xsl:template>

    <xsl:template match="lom:location">
        <imsmd:location>
            <xsl:value-of select="."/>
        </imsmd:location>
    </xsl:template>
    
    <!-- rules for lom:general section -->
    <xsl:template match="lom:language">
        <imsmd:language>
            <xsl:value-of select="."/>
        </imsmd:language>
    </xsl:template>
    
    <xsl:template match="lom:description">
        <imsmd:description>
            <xsl:apply-templates select="lom:string"/>
        </imsmd:description>
    </xsl:template>
    
    <xsl:template match="lom:classification">
        <xsl:apply-templates select="lom:keyword"/>
    </xsl:template>
    
    <xsl:template match="lom:keyword">
        <imsmd:keyword>
            <xsl:apply-templates select="lom:string"/>
        </imsmd:keyword>
    </xsl:template>
    
    
    <!-- rules for the lom:lifeCycle section -->
    
    <xsl:template match="lom:lifeCycle">
        <imsmd:lifecycle>
            <xsl:apply-templates select="lom:contribute"/>
        </imsmd:lifecycle>
    </xsl:template>
    
    <xsl:template match="lom:contribute">
        <imsmd:contribute>
            <xsl:apply-templates select=" lom:role"/>
            <imsmd:centity>
                <imsmd:vcard>
                    <xsl:text>BEGIN:VCARD
                    </xsl:text>
                    <xsl:text>FN:</xsl:text>
                    <xsl:value-of select="lom:entity"/>
                    <xsl:text>
                    </xsl:text>
                    <xsl:text>END:VCARD</xsl:text>
                </imsmd:vcard>
            </imsmd:centity>
            <imsmd:date>
                <imsmd:datetime>
                    <xsl:value-of select="lom:date/lom:dateTime"/>
                </imsmd:datetime>
            </imsmd:date>
        </imsmd:contribute>
    </xsl:template>
    
    <xsl:template match="lom:role">
        <imsmd:role>
            <imsmd:source>
                <imsmd:langstring>
                    <xsl:attribute name="xml:lang">
                        <xsl:value-of select="'x-none'"/>
                    </xsl:attribute>
                    <xsl:value-of select="substring-after(lom:source,'OCW_')"/>
                </imsmd:langstring>
            </imsmd:source>
            <imsmd:value>
                <imsmd:langstring>
                    <xsl:attribute name="xml:lang">
                        <xsl:value-of select="'x-none'"/>
                    </xsl:attribute>
                    <xsl:value-of select="lom:value"/>
                </imsmd:langstring>               
            </imsmd:value>
        </imsmd:role>
    </xsl:template>
    
    <!-- generic rules -->

    <xsl:template match="lom:string">
        <xsl:variable name="language" select="@language"/>
        <imsmd:langstring>
            <xsl:attribute name="xml:lang">
                <xsl:choose>
                    <xsl:when test="string-length($language) = 0">
                        <xsl:value-of select=" 'x-none' "/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$language"/>        
                    </xsl:otherwise>
                    </xsl:choose>
            </xsl:attribute>
            <xsl:value-of select="."/>
        </imsmd:langstring>
    </xsl:template>
    
    <xsl:template match="adlcp:location"> </xsl:template>

    
    <!-- the following rules are for retrieving a title from a reference --> 
    <xsl:template name="getFilename">
        <xsl:param name="file_path"/>
        <xsl:variable name="rfile_path">
            <xsl:call-template name="reverse_chars">
                <xsl:with-param name="string_var" select="@href"/>
            </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="trim_rfile_path" select="substring-before($rfile_path,'/')"/>
        <xsl:variable name="file_name">
            <xsl:choose>
                <xsl:when test="$trim_rfile_path">
                    <xsl:call-template name="reverse_chars">
                        <xsl:with-param name="string_var" select="$trim_rfile_path"/>
                    </xsl:call-template>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:call-template name="reverse_chars">
                        <xsl:with-param name="string_var" select="$rfile_path"/>
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

    <xsl:template name="reverse_chars">
        <xsl:param name="string_var"/>
        <xsl:param name="rstring"/>
        <xsl:choose>
            <xsl:when test="$string_var">
                <xsl:call-template name="reverse_chars">
                    <xsl:with-param name="string_var" select="substring($string_var, 2)"/>
                    <xsl:with-param name="rstring"
                        select="concat(substring($string_var, 1, 1),
                        $rstring)"
                    />
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$rstring"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
