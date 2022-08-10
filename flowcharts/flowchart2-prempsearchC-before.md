# prempsearchC-before

```mermaid
flowchart TD
    A[/"~"/.coias/param/AstMPC_dim.edb/] --- B[[searchB.py]]
    C[/"~"/.coias/param/AstMPC.edb/] --- D[[searchB_AstMPC.py]]
    B --> E[/cand_dim.txt/]
    D --> F[/cand_bright.txt/]
    D --> G[/bright_asteroid_raw_names_in_the_field.txt/]
    G --- h[[make_asteroid_name_list_in_the_field.py]]
    h --> i[/"~"/.coias/orbit_data/以下の\nbright_asteroid_MPC_names_in_the_field.txt/]
    E --> H[/cand.txt/]
    F --> H
    H --> I[/cand2.txt/]
    I --> J[/cand2b.txt/]
    J --> K[/cand3.txt/]
    J --> L[/cand4.txt/]
    K --- M[[getinfo_numbered.py]]
    M --> N[/"~"/.coias/orbit_data/以下の\nnumbered_new2B.txt/]

    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src3_prempsearchC-before/searchB.py"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/src3_prempsearchC-before/searchB_AstMPC.py"
    click h "https://github.com/COIAS-program/COIAS_program_github/blob/main/src3_prempsearchC-before/make_asteroid_name_list_in_the_field.py"
    click M "https://github.com/COIAS-program/COIAS_program_github/blob/main/src3_prempsearchC-before/getinfo_numbered2D.py"

    click E "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand_dim.txt"
    click F "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand_bright.txt"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/bright_asteroid_raw_names_in_the_field.txt"
    click i "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/bright_asteroid_MPC_names_in_the_field.txt"
    click H "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand.txt"
    click I "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand2.txt"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand2b.txt"
    click K "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand3.txt"
    click L "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand4.txt"
    click N "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/numbered_new2B.txt"
``````