# AstsearchR_between_COIAS_and_ReCOIAS

```mermaid
flowchart TD
    A[/memo.txt/] --- B[[prempedit2.py]]
    C[/mpc.txt/] --- B
    B --> D[/mpc2.txt/]
    D --- E[[makeHlist]]
    E --> F[/Hlist.txt/]
    D --- G[[prempedit3.py]]
    F --- G
    G --> H[/mpc3.txt/]
    G --> I[/H_conversion_list.txt/]
    H --- J[[redisp.py]]
    H --> K[/mpc4.txt/]
    L[/all.txt/] --- J
    J --> M[/newall.txt/]
    J --> N[/predisp.txt/]
    N --> O[/redisp.txt/]

    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/prempedit2.py"
    click E "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/makeHlist"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/prempedit3.py"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/redisp.py"
    
    click A "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/memo.txt"
    click C "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/mpc.txt"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/mpc2.txt"
    click F "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/Hlist.txt"
    click H "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/mpc3.txt"
    click I "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/H_conversion_list.txt"
    click K "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/mpc4.txt"
    click L "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/all.txt"
    click M "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/newall.txt"
    click N "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/predisp.txt"
    click O "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/redisp.txt"
``````