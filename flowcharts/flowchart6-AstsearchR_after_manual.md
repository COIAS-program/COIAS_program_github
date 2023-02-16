# AstsearchR_after_manual

```mermaid
flowchart TD
    A[/memo_manual.txt/] --- B[[photometry_manual_objects.py]]
    C[/warp*_bin.fits/] --- B
    B --> D[/listb3.txt/]
    D --- E[[match2E.py]]
    F[/search_astB.txt/] --- E
    E --> G[/match_manual.txt/]
    E --> H[/nomatch_manual.txt/]
    G --- I[[change_data_to_mpc_format_manual.py]]
    H --- I
    I --> J[/numbered_all_m.txt\nnumbered_mpc_m.txt\nnumbered_disp_m.txt/]
    I --> K[/karifugo_all_m.txt\nkarifugo_mpc_m.txt\nkarifugo_disp_m.txt/]
    I --> L[/unknown_all_m.txt\nunknown_mpc_m.txt\nunknown_disp_m.txt/]
    J --- M[[いくつかの処理とcatコマンドによる連結]]
    K --- M
    L --- M
    M --> N[/all_m.txt/]
    M --> O[/mpc_m.txt/]
    M --> P[/disp_m.txt/]
	c[/"(redisp.txtが空の場合)\n~/.coias/param/max_H_number.txt"/] --- Q[[make_mpc4_newall_and_redisp_manual.py]]
    N --- Q
    O --- Q
    P --- Q
    Q --> R[/newall_m.txt/]
    Q --> S[/mpc4_m.txt/]
    Q --> T[/redisp_manual.txt/]
    Q --> U[/H_conversion_list_manual.txt/]
    T --> V[/reredisp.txt/]
    W[/redisp.txt/] --- X[[apply_manual_delete_to_redisp.py]]
    Y[/manual_delete_list.txt/] --- X
    Z[/H_conversion_list.txt/] --- X
    X --> a[/redisp2.txt/]
    X --> b[/manual_delete_list2.txt/]
    a --> V

    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src8_astsearch_manual/photometry_manual_objects.py"
    click E "https://github.com/COIAS-program/COIAS_program_github/blob/main/src8_astsearch_manual/match2E.py"
    click I "https://github.com/COIAS-program/COIAS_program_github/blob/main/src8_astsearch_manual/change_data_to_mpc_format_manual.py"
    click Q "https://github.com/COIAS-program/COIAS_program_github/blob/main/src8_astsearch_manual/make_mpc4_newall_and_redisp_manual.py"
    click X "https://github.com/COIAS-program/COIAS_program_github/blob/main/src8_astsearch_manual/apply_manual_delete_to_redisp.py"
    
    click A "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/memo_manual.txt"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/listb3.txt"
    click F "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample3/search_astB.txt"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/match_manual.txt"
    click H "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/nomatch_manual.txt"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/numbered_all_mpc_disp_m.txt"
    click K "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/karifugo_all_mpc_disp_m.txt"
    click L "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/unknown_all_mpc_disp_m.txt"
    click N "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/all_m.txt"
    click O "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/mpc_m.txt"
    click P "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/disp_m.txt"
    click R "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/newall_m.txt"
    click S "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/mpc4_m.txt"
    click T "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/redisp_manual.txt"
    click U "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/H_conversion_list_manual.txt"
    click V "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/reredisp.txt"
    click W "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/redisp.txt"
    click Y "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/manual_delete_list.txt"
    click Z "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/H_conversion_list.txt"
    click a "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/redisp2.txt"
    click b "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample6/manual_delete_list2.txt"
``````