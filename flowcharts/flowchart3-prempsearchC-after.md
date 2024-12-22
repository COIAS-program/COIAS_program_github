# prempsearchC-after

```mermaid
flowchart TD
    A[/cand4.txt/] --- B[[getinfo_karifugo2D.py]]
    B --> C[/"~"/.coias/orbit_data/以下の<br>karifugo_new2B.txt/]
    B --> D[/"~"/.coias/orbit_data/以下の<br>ra_dec_jd_time.txt/]
    C --- E[[make_search_astB_in_each_directory.py]]
    F[/"~"/.coias/orbit_data/以下の<br>numbered_new2B.txt/] --- E
    E --> G[/"~"/.coias/orbit_data/以下の<br>search_astB.txt/]
``````

<!--
    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src4_prempsearchC-after/getinfo_karifugo2D.py"
    click E "https://github.com/COIAS-program/COIAS_program_github/blob/main/src4_prempsearchC-after/make_search_astB_in_each_directory.py"

    click A "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/cand4.txt"
    click C "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample3/karifugo_new2B.txt"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample3/ra_dec_jd_time.txt"
    click F "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/numbered_new2B.txt"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample3/search_astB.txt"
-->