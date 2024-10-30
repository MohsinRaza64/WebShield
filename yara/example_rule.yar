rule ExampleMalwareDetection
{
    meta:
        description = "Detects Example Malware based on specific strings and byte patterns"
        author = "YourName"
        date = "2024-10-30"
        version = "1.0"
        
    strings:
        $string1 = "malicious_keyword"
        $string2 = { 6A 40 68 00 30 00 00 6A 14 8D 91 }    // Hexadecimal byte pattern
        $string3 = /http:\/\/malicious-domain\.com/         // Regex pattern

    condition:
        any of ($string*)
}
