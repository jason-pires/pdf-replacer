
# Create a comprehensive mermaid flowchart for the PDF placeholder replacement workflow

diagram_code = """
flowchart TD
    Start([Start: Contract Request]) --> Step1
    
    Step1[<b>1. Database Query</b><br/>PostgreSQL Data Retrieval]
    Step1 --> SQL[SQL Query:<br/>SELECT clinica_nome,<br/>paciente_nome, valor_total<br/>FROM contratos]
    SQL --> Data1[(Database Fields:<br/>clinica_nome<br/>paciente_nome<br/>valor_total)]
    
    Data1 --> Step2[<b>2. Data Mapping</b><br/>DatabaseToDataMapper]
    Step2 --> Mapper[map_db_to_placeholders&#40;&#41;<br/>Convert DB columns to<br/>placeholder format]
    Mapper --> Data2[Mapped Data:<br/>20 placeholders ready]
    
    Data2 --> Step3{<b>3. Validation</b><br/>Check Required Fields}
    Step3 -->|Valid| Valid[✓ All fields present<br/>20/20 placeholders filled]
    Step3 -->|Invalid| Invalid[✗ Missing fields<br/>Example: cpfpaciente]
    Invalid --> Error([Error: Return validation failure])
    
    Valid --> Step4[<b>4. PDF Generation</b><br/>ReportLab Overlay]
    Step4 --> Replace[replace_and_get_pdf&#40;&#41;<br/>Substitute placeholders<br/>in PDF template]
    Replace --> PDFBytes[Output: PDF bytes<br/>Performance: 0.5-1.0 sec]
    
    PDFBytes --> Step5{<b>5. Output Distribution</b><br/>Save or Send PDF}
    Step5 --> S3[AWS S3<br/>Cloud Storage]
    Step5 --> Email[Email<br/>Direct Send]
    Step5 --> Sign[Digital Signature<br/>DocuSign/OneFlow]
    
    S3 --> End([Complete: PDF Delivered])
    Email --> End
    Sign --> End
    
    Note1[Total: 20 placeholders<br/>Dynamic: procedimentos]
    
    style Step1 fill:#B3E5EC,stroke:#1FB8CD,stroke-width:3px
    style Step2 fill:#A5D6A7,stroke:#2E8B57,stroke-width:3px
    style Step3 fill:#FFEB8A,stroke:#D2BA4C,stroke-width:3px
    style Step4 fill:#FFCDD2,stroke:#DB4545,stroke-width:3px
    style Step5 fill:#9FA8B0,stroke:#5D878F,stroke-width:3px
    
    style Valid fill:#A5D6A7,stroke:#2E8B57,stroke-width:2px
    style Invalid fill:#FFCDD2,stroke:#DB4545,stroke-width:2px
    style Error fill:#FFCDD2,stroke:#DB4545,stroke-width:2px
    
    style SQL fill:#E3F2FD,stroke:#1FB8CD,stroke-width:2px
    style Mapper fill:#E8F5E9,stroke:#2E8B57,stroke-width:2px
    style Replace fill:#FFEBEE,stroke:#DB4545,stroke-width:2px
    
    style Data1 fill:#B3E5EC,stroke:#1FB8CD,stroke-width:2px
    style Data2 fill:#A5D6A7,stroke:#2E8B57,stroke-width:2px
    style PDFBytes fill:#FFCDD2,stroke:#DB4545,stroke-width:2px
    
    style S3 fill:#E3F2FD,stroke:#5D878F,stroke-width:2px
    style Email fill:#E3F2FD,stroke:#5D878F,stroke-width:2px
    style Sign fill:#E3F2FD,stroke:#5D878F,stroke-width:2px
    
    style Start fill:#E8F5E9,stroke:#2E8B57,stroke-width:2px
    style End fill:#E8F5E9,stroke:#2E8B57,stroke-width:2px
    
    style Note1 fill:#FFF9E6,stroke:#D2BA4C,stroke-width:2px,stroke-dasharray: 5 5
"""

# Create the mermaid diagram using the helper function
create_mermaid_diagram(diagram_code, 'workflow.png', 'workflow.svg', width=1400, height=1000)
