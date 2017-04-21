<schema xmlns="http://purl.oclc.org/dsdl/schematron">
    <pattern>
        <title>Attribute usage</title>
        <!-- Elements that contains a dot in their name -->
        <rule context="*[contains(name(), '.')]">
            <!-- Check that there is no parent's attributes with the same name -->
            <assert test="not(../@*[name() = substring-after(name(current()), '.')])">
                The attribute <name /> is defined twice.
            </assert>
        </rule>
    </pattern>
</schema>