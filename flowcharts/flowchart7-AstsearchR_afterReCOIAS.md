# AstsearchR_afterReCOIAS

```mermaid
flowchart TD
    n[/mpc4.txt/] --- o[[apply_manual_delete_to_report.py]]
    p[/newall.txt/] --- o
    q[/redisp.txt/] --- o
    E[/manual_delete_list.txt/] --- o
    o --> A
    o --> C
    o --> D
    A[/mpc4_2.txt<br>mpc4_m.txt/] --- B[[merge_manual]]
    C[/newall_2.txt<br>newall_m.txt/] --- B
    D[/redisp_2.txt<br>redisp_manual.txt/] --- B

    B --> F[/mpc4_automanual.txt/]
    B --> G[/newall_automanual.txt/]
    B --> H[/redisp_automanual.txt/]
    B --> I[/H_conversion_list_automanual.txt/]
    l[/manual_name_modify_list.txt/] --- J
    F --- J[[apply_manual_name_modify.py]]
    G --- J
    H --- J
    I --- J
    J --> K[/mpc4_automanual2.txt/]
    J --> L[/newall_automanual2.txt/]
    J --> M[/redisp_automanual2.txt/]
    J --> N[/H_conversion_list_automanual2.txt/]
    K --- O[[deldaburi4.py]]
    O --> P[/mpc7.txt/]
    P --- Q[[findorb.py]]
    Q --> R[/result.txt/]
    Q --> S[/orbital_elements_summary_web.txt<br>or orbital_elements_summary.txt/]
    R --- T[[delLargeZansa_and_modPrecision.py]]
    T --> U[/pre_repo.txt/]
    U --- V[[reject_bright_known_asteroids_from_report.py]]
    V --> W[/pre_repo.txt/]
    X[/bright_asteroid_MPC_names_in_the_field.txt/] --- V
	W --- b[[del_duplicated_line_from_pre_repo.py]]
	c[/measure_resultテーブル/] --- b
	b --> d[/pre_repo2.txt/]
    d --- Y2[[del_duplicated_line_with_other_programs.py]]
    c2[/ObservationAPIの情報<br>~/.coias/param/itf_T09_except4.txt/] --- Y2
    Y2 --> d2[/pre_repo2_2.txt/]
    d2 --- Y[[modify_preRepo_as_H_sequential.py]]
    r[/"~/.coias/param/max_H_number.txt"/] --> Y
    s[/start_H_number.txt/] --> Y
    Y --> Z[/pre_repo3.txt/]
    Y --> a[/H_conversion_list_automanual3.txt/]
    N --- Y
    Z --- e[[komejirushi.py]]
    e --> f[/send_mpc.txt/]
    Z --- g[[store_pre_repo3.py<br>未使用]]
    g --> h[/"~"/.coias/past_pre_repo_data/以下にコピー<br>未使用/]
    g --> m[/"~"/.coias/past_pre_repo_data/<br>yyyy-mm-dd/coefficients_for_predict.txt<br>未使用/]
    a --- i[[make_final_all_and_disp.py]]
    Z --- i
    L --- i
    i --> j[/final_all.txt/]
    i --> k[/final_disp.txt/]
    i --> t[/"~/.coias/param/max_H_number.txt"/]
    S --- i
    j --- u[[make_prefixed_sendMpc_and_finalAll.py]]
    f --- u
    u --> v[/yyyymmddHHMM_id_send_mpc.txt/]
    u --> w[/yyyymmddHHMM_id_final_all.txt/]
``````

<!--
    click B1 "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/adjust_newH_manual.py"
    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/merge_manual"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/apply_manual_name_modify.py"
    click O "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/deldaburi4.py"
    click Q "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/findorb.py"
    click T "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/delLargeZansa_and_modPrecision.py"
    click V "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/reject_bright_known_asteroids_from_report.py"
    click Y "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/modify_preRepo_as_H_sequential.py"
    click b "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/del_duplicated_line_from_pre_repo2.py"
    click e "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/komejirushi.py"
    click g "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/store_pre_repo3.py"
    click i "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/make_final_all_and_disp.py"
    click o "https://github.com/COIAS-program/COIAS_program_github/blob/main/src7_AstsearchR_afterReCOIAS/apply_manual_delete_to_report.py"
    
    click F "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/mpc4_automanual.txt"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/newall_automanual.txt"
    click H "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/redisp_automanual.txt"
    click I "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/H_conversion_list_automanual.txt"
    click K "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/mpc4_automanual2.txt"
    click L "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/newall_automanual2.txt"
    click M "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/redisp_automanual2.txt"
    click N "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/H_conversion_list_automanual2.txt"
    click P "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/mpc7.txt"
    click R "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/result.txt"
    click S "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/orbital_elements_summary_web.txt"
    click U "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/pre_repo.txt"
    click W "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/pre_repo.txt"
    click X "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample2/bright_asteroid_MPC_names_in_the_field.txt"
    click Z "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/pre_repo3.txt"
    click a "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/H_conversion_list_automanual3.txt"
    click c "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/pre_repo3_sample.txt"
    click d "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/pre_repo2.txt"
    click f "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/send_mpc.txt"
    click j "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/final_all.txt"
    click k "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/final_disp.txt"
    click l "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/manual_name_modify_list.txt"
    click m "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/coefficients_for_predict.txt"
    click A "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/mpc4_2.txt"
    click C "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/newall_2.txt"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample7/redisp_2.txt"
    click r "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/max_H_number.txt"
    click s "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/start_H_number.txt"
    click t "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample5/max_H_number.txt"
-->