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
	T[/"(第二引数が省略された場合)\n~/.coias/param/max_H_number.txt"/] --> G
    G --> H[/mpc3.txt/]
    G --> I[/H_conversion_list.txt/]
    G --> U[/start_H_number.txt/]
    H --- J[[redisp.py]]
    H --> K[/mpc4.txt/]
    L[/all.txt/] --- J
    J --> M[/newall.txt/]
    J --> N[/predisp.txt/]
    N --> O[/redisp.txt/]

    subgraph correct
        P[/"(先にmanual measureモードを実行していたら)"\nmanual_delete_list2.txt/] --- Q[[correct_manual_delete_list.py]]
        R[/H_conversion_list.txt/] --- Q
        Q --> S[/manual_delete_list.txt/]
    end

    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/prempedit2.py"
    click E "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/makeHlist"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/prempedit3.py"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/redisp.py"
    click Q "https://github.com/COIAS-program/COIAS_program_github/blob/main/src6_between_COIAS_and_ReCOIAS/correct_manual_delete_list.py"
    
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
    click P "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/manual_delete_list2.txt"
    click R "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/H_conversion_list.txt"
    click S "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/manual_delete_list.txt"
    click T "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/max_H_number.txt"
    click U "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/start_H_number.txt"
``````