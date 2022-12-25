# startsearch2R

```mermaid
flowchart TD
    A[/初期画像ファイル\nwarp-HSC-フィルタ-tract番号-patch番号,patch番号-*.fits/] --- B[[binning.py]]
    L["(webCOIASの場合)"\nselected_warp_files.txt] --- B
    B --> C[/ビニング済み画像ファイル\nwarpbin-HSC-フィルタ-tract番号-patch番号,patch番号-*.fits/]
    C --- D[[subm2.py]]
    D --> E[/ビニングマスク済み画像ファイル\nwarp*_bin.fits/]
    D --> F[/*_disp-coias.png\n*_disp-coias_nonmask.png/]
    E --- G[[search_precise_orbit_directories.py]]
    G --> H[/precise_orbit_directories.txt\nhave_all_precise_orbits.txt/]
    E --- J[[findsource_auto_thresh_correct.py]]
    J --> K[/warp*_bin.dat/]

    click B "https://github.com/COIAS-program/COIAS_program_github/blob/main/src2_startsearch2R/binning.py"
    click D "https://github.com/COIAS-program/COIAS_program_github/blob/main/src2_startsearch2R/subm2.py"
    click G "https://github.com/COIAS-program/COIAS_program_github/blob/main/src2_startsearch2R/search_precise_orbit_directories.py"
    click J "https://github.com/COIAS-program/COIAS_program_github/blob/main/src2_startsearch2R/findsource_auto_thresh_correct.py"
    click H "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample1/precise_orbit_directories_and_have_all_precise_orbits.txt"
    click K "https://github.com/COIAS-program/COIAS_program_github/blob/main/flowcharts/sample1/warp01_bin.dat"
``````