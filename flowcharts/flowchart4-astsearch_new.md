# astsearch_new

```mermaid
flowchart TD
    A[/"~"/.coias/orbit_data/以下の\n画像枚数分のsearch_astB.txtたち/] --- B[[make_gathered_search_astB.py]]
    C[/"~"/.coias/orbit_data/以下の\nbright_asteroid_MPC_names_in_the_field.txt/] --- B
    B --> D[/search_astB.txt/]
    B --> E[/bright_asteroid_MPC_names_in_the_field.txt\nカレントディレクトリにコピー/]
    D --- F[[match2D.py]]
    G[/warp*_bin.dat/] --- H[[astsearch1M2_optimized.py]]
    H --> I[/listb2.txt/]
    I --- F
    F --> J[/match.txt/]
    F --> K[/nomatch.txt/]
    J --- L[[change_data_to_mpc_format.py]]
    K --- L
    L --> M[/numbered_all.txt\nnumbered_mpc.txt\nnumbered_disp.txt/]
    L --> N[/karifugo_all.txt\nkarifugo_mpc.txt\nkarifugo_disp.txt/]
    L --> O[/unknown_all.txt\nunknown_mpc.txt\nunknown_disp.txt/]
    M --> P[[いくつかの処理とcatコマンドによる連結]]
    N --> P
    O --> P
    P --> Q[/all.txt/]
    P --> R[/mpc.txt/]
    P --> S[/disp.txt/]

    subgraph predict
        A1[/"~"/.coias/past_pre_repo_data/\nyyyy-mm-dd/coefficients_for_predict.txt/] --- B1[[make_predicted_disp.py]]
        B1 --> C1[/predicted_disp.txt/]
    end

    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src5_astsearch_new/make_gathered_search_astB.py"
    click F "https://github.com/COIAS-program/COIAS_program_github/blob/main/src5_astsearch_new/match2D.py"
    click H "https://github.com/COIAS-program/COIAS_program_github/blob/main/src5_astsearch_new/astsearch1M2_optimized.py"
    click L "https://github.com/COIAS-program/COIAS_program_github/blob/main/src5_astsearch_new/change_data_to_mpc_format.py"
    click B1 "https://github.com/COIAS-program/COIAS_program_github/blob/main/src5_astsearch_new/make_predicted_disp.py"
    
    click A "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample3/search_astB.txt"
    click C "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/bright_asteroid_MPC_names_in_the_field.txt"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/search_astB.txt"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample1/warp01_bin.dat"
    click I "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/listb2.txt"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/match.txt"
    click K "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/nomatch.txt"
    click M "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/numbered_all_mpc_disp.txt"
    click N "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/karifugo_all_mpc_disp.txt"
    click O "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/unknown_all_mpc_disp.txt"
    click Q "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/all.txt"
    click R "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/mpc.txt"
    click S "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/disp.txt"
    click A1 "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/coefficients_for_predict.txt"
    click C1 "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample4/predicted_disp.txt"
``````