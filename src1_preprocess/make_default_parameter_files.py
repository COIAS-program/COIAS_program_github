#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2022/11/18 8:00 sugiura
###################################################################
# SExtractor と findOrb で使用するパラメータファイルを
# ~/.coias/param 以下に生成するスクリプト.
# あくまでも雛形でありパスなどはあとで適切に書き換えられる.
# 最も重要なパラメータはSExtractorのDETECT_MINAREAとDETECT_THRESHだが,
# これらはメインスクリプト実行時に引数にてオプション的に指定できる.
# その他このスクリプトに記載のパラメータの意味はよくわかっていないので
# あまり気にする必要はない.
###################################################################
import traceback
import readparam
import print_detailed_log
import PARAM

directory_path = PARAM.COIAS_DATA_PATH + "/param/"

# ---make default.conv-------------------------------------------------------------
def make_default_conv():
    filename = directory_path + "default.conv"
    file = open(filename, "w")

    file.write("CONV NORM\n")
    file.write("# 3x3 ``all-ground'' convolution mask with FWHM = 2 pixels.\n")
    file.write("1 2 1\n")
    file.write("2 4 2\n")
    file.write("1 2 1\n")

    file.close()


# ---------------------------------------------------------------------------------

# ---make default.sex--------------------------------------------------------------
def make_default_sex(DETECT_MINAREA):
    filename = "default.sex"
    file = open(filename, "w")

    file.write("# Default configuration file for SExtractor 2.5.0\n")
    file.write("# EB 2007-02-23\n")
    file.write("#\n")
    file.write("\n")
    file.write(
        "#-------------------------------- Catalog ------------------------------------\n"
    )
    file.write("\n")
    file.write("CATALOG_NAME     test.cat       # name of the output catalog\n")
    file.write(
        "CATALOG_TYPE     ASCII_HEAD     # NONE,ASCII,ASCII_HEAD, ASCII_SKYCAT,\n"
    )
    file.write(
        "                                # ASCII_VOTABLE, FITS_1.0 or FITS_LDAC\n"
    )
    file.write(
        "PARAMETERS_NAME  /path/to/coias/param/default2.param  # name of the file containing catalog contents\n"
    )
    file.write("\n")
    file.write(
        "#------------------------------- Extraction ----------------------------------\n"
    )
    file.write("\n")
    file.write(
        "DETECT_TYPE      CCD            # CCD (linear) or PHOTO (with gamma correction)\n"
    )
    file.write(
        "DETECT_MINAREA   {0:d}              # minimum number of pixels above threshold\n".format(
            DETECT_MINAREA
        )
    )
    file.write(
        "DETECT_THRESH    1.20          # <sigmas> or <threshold>,<ZP> in mag.arcsec-2\n"
    )
    file.write(
        "ANALYSIS_THRESH  1            # <sigmas> or <threshold>,<ZP> in mag.arcsec-2\n"
    )
    file.write("\n")
    file.write(
        "FILTER           Y              # apply filter for detection (Y or N)?\n"
    )
    file.write(
        "FILTER_NAME      /path/to/coias/param/default.conv   # name of the file containing the filter\n"
    )
    file.write("\n")
    file.write("DEBLEND_NTHRESH  1             # Number of deblending sub-thresholds\n")
    file.write(
        "DEBLEND_MINCONT  1            # Minimum contrast parameter for deblending\n"
    )
    file.write("\n")
    file.write(
        "CLEAN            Y              # Clean spurious detections? (Y or N)?\n"
    )
    file.write("CLEAN_PARAM      2.0            # Cleaning efficiency\n")
    file.write("\n")
    file.write(
        "MASK_TYPE        CORRECT        # type of detection MASKing: can be one of\n"
    )
    file.write("                                # NONE, BLANK or CORRECT\n")
    file.write("\n")
    file.write(
        "#------------------------------ Photometry -----------------------------------\n"
    )
    file.write("\n")
    file.write(
        "PHOT_APERTURES   20              # MAG_APER aperture diameter(s) in pixels\n"
    )
    file.write(
        "PHOT_AUTOPARAMS  2.5, 3.5       # MAG_AUTO parameters: <Kron_fact>,<min_radius>\n"
    )
    file.write(
        "PHOT_PETROPARAMS 2.0, 3.5       # MAG_PETRO parameters: <Petrosian_fact>,\n"
    )
    file.write("                                # <min_radius>\n")
    file.write("\n")
    file.write(
        "SATUR_LEVEL      40000.0        # level (in ADUs) at which arises saturation\n"
    )
    file.write("\n")
    file.write("MAG_ZEROPOINT   32.0            # magnitude zero-point\n")
    file.write(
        "MAG_GAMMA        4.0            # gamma of emulsion (for photographic scans)\n"
    )
    file.write("GAIN             3            # detector gain in e-/ADU\n")
    file.write(
        "PIXEL_SCALE      0.34            # size of pixel in arcsec (0=use FITS WCS info)\n"
    )
    file.write(
        "#------------------------- Star/Galaxy Separation ----------------------------\n"
    )
    file.write("\n")
    file.write("SEEING_FWHM      0.6            # stellar FWHM in arcsec\n")
    file.write(
        "STARNNW_NAME     default.nnw    # Neural-Network_Weight table filename\n"
    )
    file.write("\n")
    file.write(
        "#------------------------------ Background -----------------------------------\n"
    )
    file.write("\n")
    file.write(
        "BACK_SIZE        64             # Background mesh: <size> or <width>,<height>\n"
    )
    file.write(
        "BACK_FILTERSIZE  3              # Background filter: <size> or <width>,<height>\n"
    )
    file.write("\n")
    file.write("BACKPHOTO_TYPE   GLOBAL         # can be GLOBAL or LOCAL\n")
    file.write("\n")
    file.write(
        "#------------------------------ Check Image ----------------------------------\n"
    )
    file.write("\n")
    file.write(
        "CHECKIMAGE_TYPE  OBJECTS           # can be NONE, BACKGROUND, BACKGROUND_RMS,\n"
    )
    file.write(
        "                                # MINIBACKGROUND, MINIBACK_RMS, -BACKGROUND,\n"
    )
    file.write(
        "                                # FILTERED, OBJECTS, -OBJECTS, SEGMENTATION,\n"
    )
    file.write("                                # or APERTURES\n")
    file.write("CHECKIMAGE_NAME  check.fits     # Filename for the check-image\n")
    file.write("\n")
    file.write(
        "#--------------------- Memory (change with caution!) -------------------------\n"
    )
    file.write("\n")
    file.write("MEMORY_OBJSTACK  3000           # number of objects in stack\n")
    file.write("MEMORY_PIXSTACK  300000         # number of pixels in stack\n")
    file.write("MEMORY_BUFSIZE   1024           # number of lines in buffer\n")
    file.write("\n")
    file.write("\n")
    file.write(
        "#----------------------------- Miscellaneous ---------------------------------\n"
    )
    file.write("\n")
    file.write("VERBOSE_TYPE     NORMAL         # can be QUIET, NORMAL or FULL\n")
    file.write("WRITE_XML        N              # Write XML file (Y/N)?\n")
    file.write("XML_NAME         sex.xml        # Filename for XML output\n")

    file.close()


# --------------------------------------------------------------------------------

# ---make default2.param----------------------------------------------------------
def make_default2_param():
    filename = directory_path + "default2.param"
    file = open(filename, "w")

    file.write("X_IMAGE\n")
    file.write("Y_IMAGE\n")
    file.write("MAG_BEST\n")
    file.write("#MAGERR_BEST\n")
    file.write("\n")
    file.write("#KRON_RADIUS\n")
    file.write("BACKGROUND\n")
    file.write("\n")
    file.write("#THRESHOLD\n")
    file.write("#MU_THRESHOLD\n")
    file.write("FLUX_MAX\n")
    file.write("#MU_MAX\n")
    file.write("#ISOAREA_IMAGE\n")
    file.write("#ISOAREA_WORLD\n")
    file.write("\n")
    file.write("#XMIN_IMAGE\n")
    file.write("#YMIN_IMAGE\n")
    file.write("#XMAX_IMAGE\n")
    file.write("#YMAX_IMAGE\n")

    file.close()


# ---------------------------------------------------------------------------------

# ---make ObsCodes.htm-------------------------------------------------------------
def make_ObsCodes_htm():
    filename = directory_path + "ObsCodes.htm"
    file = open(filename, "w")

    file.write("<pre>\n")
    file.write("Code  Long.   cos      sin    Name\n")
    file.write("000   0.0000 0.62411 +0.77873 Greenwich\n")
    file.write("001   0.1542 0.62992 +0.77411 Crowborough\n")
    file.write("002   0.62   0.622   +0.781   Rayleigh\n")
    file.write("003   3.90   0.725   +0.687   Montpellier\n")
    file.write("004   1.4625 0.72520 +0.68627 Toulouse\n")
    file.write("005   2.231000.659891+0.748875Meudon\n")
    file.write("006   2.124170.751042+0.658129Fabra Observatory, Barcelona\n")
    file.write("007   2.336750.659470+0.749223Paris\n")
    file.write("008   3.0355 0.80172 +0.59578 Algiers-Bouzareah\n")
    file.write("009   7.4417 0.6838  +0.7272  Berne-Uecht\n")
    file.write("010   6.921240.723655+0.688135Caussols\n")
    file.write("011   8.7975 0.67920 +0.73161 Wetzikon\n")
    file.write("012   4.358210.633333+0.771306Uccle\n")
    file.write("013   4.483970.614813+0.786029Leiden\n")
    file.write("014   5.395090.728859+0.682384Marseilles\n")
    file.write("015   5.129290.615770+0.785285Utrecht\n")
    file.write("016   5.9893 0.68006 +0.73076 Besancon\n")
    file.write("017   6.849240.641946+0.764282Hoher List\n")
    file.write("018   6.7612 0.62779 +0.77578 Dusseldorf-Bilk\n")
    file.write("019   6.9575 0.68331 +0.72779 Neuchatel\n")
    file.write("020   7.3004 0.72391 +0.68767 Nice\n")
    file.write("021   8.3855 0.65701 +0.75138 Karlsruhe\n")
    file.write("022   7.7748 0.70790 +0.70409 Pino Torinese\n")
    file.write("023   8.2625 0.64299 +0.76335 Wiesbaden\n")
    file.write("024   8.7216 0.65211 +0.75570 Heidelberg-Konigstuhl\n")
    file.write("025   9.196500.660205+0.748637Stuttgart\n")
    file.write("026   7.465110.684884+0.726402Berne-Zimmerwald\n")
    file.write("027   9.1912 0.70254 +0.70929 Milan\n")
    file.write("028   9.9363 0.64686 +0.76009 Wurzburg\n")
    file.write("029  10.2406 0.59640 +0.80000 Hamburg-Bergedorf\n")
    file.write("030  11.254460.723534+0.688012Arcetri Observatory, Florence\n")
    file.write("031  11.189850.639061+0.766705Sonneberg\n")
    file.write("032  11.582950.631624+0.772706Jena\n")
    file.write(
        "033  11.711240.630900+0.773333Karl Schwarzschild Observatory, Tautenburg\n"
    )
    file.write("034  12.452460.745176+0.664656Monte Mario Observatory, Rome\n")
    file.write("035  12.575920.565008+0.822321Copenhagen\n")
    file.write("036  12.650400.747247+0.662420Castel Gandolfo\n")
    file.write("037  13.7333 0.73660 +0.67416 Collurania Observatory, Teramo\n")
    file.write("038  13.7704 0.70033 +0.71144 Trieste\n")
    file.write("039  13.1874 0.56485 +0.82243 Lund\n")
    file.write("040  13.7298 0.63019 +0.77387 Lohrmann Institute, Dresden\n")
    file.write("041  11.380830.679862+0.731012Innsbruck\n")
    file.write("042  13.064280.611721+0.788439Potsdam\n")
    file.write(
        "043  11.526430.697656+0.714269Asiago Astrophysical Observatory, Padua\n"
    )
    file.write("044  14.2559 0.75738 +0.65082 Capodimonte Observatory, Naples\n")
    file.write("045  16.3390 0.66739 +0.74227 Vienna (since 1879)\n")
    file.write("046  14.2881 0.65922 +0.74965 Klet Observatory, Ceske Budejovice\n")
    file.write("047  16.8782 0.61146 +0.78864 Poznan\n")
    file.write("048  15.840800.641709+0.764432Hradec Kralove\n")
    file.write("049  17.6067 0.5088  +0.8580  Uppsala-Kvistaberg\n")
    file.write("050  18.0582 0.51118 +0.85660 Stockholm (before 1931)\n")
    file.write("051  18.4766 0.83055 -0.55508 Royal Observatory, Cape of Good Hope\n")
    file.write("052  18.3083 0.51224 +0.85597 Stockholm-Saltsjobaden\n")
    file.write(
        "053  18.9642 0.67688 +0.73373 Konkoly Observatory, Budapest (since 1933)\n"
    )
    file.write("054  11.6654 0.56595 +0.82169 Brorfelde\n")
    file.write("055  19.9596 0.64321 +0.76316 Cracow\n")
    file.write("056  20.234180.655001+0.753470Skalnate Pleso\n")
    file.write("057  20.5133 0.71074 +0.70116 Belgrade\n")
    file.write("058  20.4950 0.57897 +0.81262 Kaliningrad\n")
    file.write("059  20.2201 0.65500 +0.75364 Lomnicky Stit\n")
    file.write("060  21.4200 0.61572 +0.78535 Warsaw-Ostrowik\n")
    file.write("061  22.298500.662142+0.746904Uzhhorod\n")
    file.write("062  22.2293 0.49440 +0.86632 Turku\n")
    file.write("063  22.4450 0.49496 +0.86601 Turku-Tuorla\n")
    file.write("064  22.7500 0.49489 +0.86605 Turku-Kevola\n")
    file.write("065  12.6318 0.67222 +0.73800 Traunstein\n")
    file.write("066  23.718170.789321+0.611946Athens\n")
    file.write("067  24.0297 0.64632 +0.76058 Lviv University Observatory\n")
    file.write("068  24.0142 0.64627 +0.76062 Lviv Polytechnic Institute\n")
    file.write("069  24.4042 0.54925 +0.83287 Baldone\n")
    file.write("070  25.2865 0.57940 +0.81233 Vilnius (before 1939)\n")
    file.write("071  24.737820.74803 +0.66185 NAO Rozhen, Smolyan\n")
    file.write("072   7.17   0.629   +0.774   Scheuren Observatory\n")
    file.write("073  26.0967 0.71549 +0.69630 Bucharest\n")
    file.write("074  26.4058 0.87518 -0.48263 Boyden Observatory, Bloemfontein\n")
    file.write("075  26.7216 0.52557 +0.84791 Tartu\n")
    file.write("076  27.8768 0.90127 -0.43225 Johannesburg-Hartbeespoort\n")
    file.write("077  28.0292 0.89819 -0.43876 Yale-Columbia Station, Johannesburg\n")
    file.write("078  28.0750 0.89824 -0.43868 Johannesburg\n")
    file.write("079  28.2288 0.90120 -0.43251 Radcliffe Observatory, Pretoria\n")
    file.write("080  28.9667 0.75566 +0.65278 Istanbul\n")
    file.write("081  27.8768 0.90127 -0.43225 Leiden Station, Johannesburg\n")
    file.write("082  15.7561 0.66929 +0.74063 St. Polten\n")
    file.write("083  30.5056 0.63918 +0.76651 Holosiivskyi district-Kyiv\n")
    file.write("084  30.3274 0.50471 +0.86041 Pulkovo\n")
    file.write("085  30.5023 0.63800 +0.76749 Kyiv\n")
    file.write("086  30.7582 0.68987 +0.72152 Odesa\n")
    file.write("087  31.3411 0.86799 +0.49495 Helwan\n")
    file.write("088  31.8250 0.86741 +0.49608 Kottomia\n")
    file.write("089  31.9747 0.68359 +0.72743 Mykolaiv\n")
    file.write("090   8.25   0.645   +0.762   Mainz\n")
    file.write("091   4.209190.703630+0.708287Observatoire de Nurol, Aurec sur Loire\n")
    file.write("092  18.5546 0.60177 +0.79601 Torun-Piwnice\n")
    file.write("093  20.3647 0.3537  +0.9322  Skibotn\n")
    file.write("094  33.9974 0.71565 +0.69620 Crimea-Simeiz\n")
    file.write("095  34.0160 0.71172 +0.70024 Crimea-Nauchnyi\n")
    file.write("096   9.4283 0.69967 +0.71215 Merate\n")
    file.write("097  34.7625 0.86165 +0.50608 Wise Observatory, Mitzpeh Ramon\n")
    file.write("098  11.569000.697916+0.714090Asiago Observatory, Cima Ekar\n")
    file.write("099  25.535290.484073+0.872114Lahti\n")
    file.write("100  24.141450.461165+0.884370Ahtari\n")
    file.write("101  36.2322 0.64403 +0.76246 Kharkiv\n")
    file.write("102  36.759530.564841+0.822468Zvenigorod\n")
    file.write("103  14.527740.695365+0.716346Ljubljana\n")
    file.write("104  10.803750.719842+0.692040San Marcello Pistoiese\n")
    file.write("105  37.5706 0.56403 +0.82302 Moscow\n")
    file.write("106  14.0711 0.69662 +0.71519 Crni Vrh\n")
    file.write("107  11.0030 0.70998 +0.70186 Cavezzo\n")
    file.write("108  11.0278 0.72367 +0.68784 Montelupo\n")
    file.write("109   3.0705 0.80241 +0.59481 Algiers-Kouba\n")
    file.write("110  39.4150 0.54316 +0.83683 Rostov\n")
    file.write("111  10.9721 0.72439 +0.68710 Piazzano Observatory, Florence\n")
    file.write("112  10.9039 0.70232 +0.70950 Pleiade Observatory, Verona\n")
    file.write("113  13.0166 0.63502 +0.77001 Volkssternwarte Drebach, Schoenbrunn\n")
    file.write(
        "114  41.4277 0.72489 +0.68702 Engelhardt Observatory, Zelenchukskaya Station\n"
    )
    file.write("115  41.440670.725004+0.686912Zelenchukskaya\n")
    file.write("116  11.5958 0.66893 +0.74094 Giesing\n")
    file.write("117  11.5385 0.66897 +0.74092 Sendling\n")
    file.write(
        "118  17.2740 0.66558 +0.74394 Astronomical and Geophysical Observatory, Modra\n"
    )
    file.write("119  42.8200 0.74731 +0.66262 Abastuman\n")
    file.write("120  13.7261 0.70489 +0.70699 Visnjan\n")
    file.write(
        "121  36.934030.648856+0.758394Kharkiv University, Chuguevskaya Station\n"
    )
    file.write("122   3.5035 0.72017 +0.69176 Pises Observatory\n")
    file.write("123  44.2917 0.76352 +0.64398 Byurakan\n")
    file.write("124   2.2550 0.72534 +0.68612 Castres\n")
    file.write("125  44.789500.747594+0.662026Tbilisi\n")
    file.write("126   9.7903 0.71893 +0.69283 Monte Viseggi\n")
    file.write("127   6.9797 0.63385 +0.77088 Bornheim\n")
    file.write("128  46.006610.623279+0.779393Saratov\n")
    file.write("129  45.92   0.777   +0.628   Ordubad\n")
    file.write("130  10.239630.700148+0.711796Lumezzane\n")
    file.write("131   4.725  0.7123  +0.6996  Observatoire de l'Ardeche\n")
    file.write("132   5.2461 0.71919 +0.69260 Bedoin\n")
    file.write("133   5.0906 0.72819 +0.68309 Les Tardieux\n")
    file.write("134  11.482450.631607+0.772773Groszschwabhausen\n")
    file.write("135  49.1210 0.56353 +0.82334 Kasan\n")
    file.write("136  48.8156 0.56282 +0.82383 Engelhardt Observatory, Kasan\n")
    file.write("137  34.8147 0.84821 +0.52790 Givatayim Observatory\n")
    file.write("138   7.5717 0.67550 +0.73494 Village-Neuf\n")
    file.write("139   7.1108 0.72526 +0.68618 Antibes\n")
    file.write("140   3.6294 0.69945 +0.71241 Augerolles\n")
    file.write("141   7.3672 0.65646 +0.75189 Hottviller\n")
    file.write("142   7.1874 0.62156 +0.78075 Sinsen\n")
    file.write("143   9.024060.692986+0.718590Gnosca\n")
    file.write("144   1.6660 0.65549 +0.75268 Bray et Lu\n")
    file.write("145   4.5597 0.62734 +0.77614 's-Gravenwezel\n")
    file.write("146  10.6673 0.71715 +0.69487 Frignano\n")
    file.write("147   8.573910.700430+0.711392Osservatorio Astronomico di Suno\n")
    file.write("148   2.0375 0.72481 +0.68667 Guitalens\n")
    file.write("149   4.2236 0.65403 +0.75396 Beine-Nauroy\n")
    file.write("150   2.1572 0.65806 +0.75045 Maisons Laffitte\n")
    file.write("151   8.7440 0.67719 +0.73346 Eschenberg Observatory, Winterthur\n")
    file.write("152  25.5633 0.57036 +0.81868 Moletai Astronomical Observatory\n")
    file.write("153   9.1747 0.66080 +0.74814 Stuttgart-Hoffeld\n")
    file.write("154  12.1043 0.68923 +0.72250 Cortina\n")
    file.write("155  10.1971 0.55864 +0.82664 Ole Romer Observatory, Aarhus\n")
    file.write("156  15.0858 0.79431 +0.60549 Catania Astrophysical Observatory\n")
    file.write("157  12.8117 0.74166 +0.66864 Frasso Sabino\n")
    file.write("158   7.6033 0.69871 +0.71333 Promiod\n")
    file.write("159  10.5153 0.72065 +0.69115 Monte Agliale\n")
    file.write("160  10.841440.722651+0.688913Castelmartini\n")
    file.write("161   8.1605 0.70725 +0.70467 Cerrina Tololo Observatory\n")
    file.write("162  15.7805 0.75988 +0.64808 Potenza\n")
    file.write("163   6.1492 0.65017 +0.75731 Roeser Observatory, Luxembourg\n")
    file.write("164   6.8861 0.66631 +0.74325 St. Michel sur Meurthe\n")
    file.write("165   1.7553 0.74984 +0.65946 Piera Observatory, Barcelona\n")
    file.write("166  16.0117 0.63730 +0.76812 Upice\n")
    file.write("167   8.5727 0.67662 +0.73398 Bulach Observatory\n")
    file.write("168  59.5472 0.54541 +0.83541 Kourovskaya\n")
    file.write("169   8.4016 0.70737 +0.70453 Airali Observatory\n")
    file.write("170   1.9206 0.75217 +0.65711 Observatorio de Begues\n")
    file.write("171  14.4697 0.81089 +0.58327 Flarestar Observatory, San Gwann\n")
    file.write("172   7.0364 0.68593 +0.72539 Onnens\n")
    file.write("173  55.5061 0.93464 -0.35447 St. Clotilde, Reunion\n")
    file.write("174  25.5131 0.46536 +0.88219 Nyrola Observatory, Jyvaskyla\n")
    file.write("175   7.6083 0.6932  +0.7188  F.-X. Bagnoud Observatory, St-Luc\n")
    file.write("176   2.8225 0.77098 +0.63475 Observatorio Astronomico de Consell\n")
    file.write("177   3.9414 0.72477 +0.68669 Le Cres\n")
    file.write("178   6.1344 0.69423 +0.71745 Collonges\n")
    file.write("179   9.0175 0.69694 +0.71507 Monte Generoso\n")
    file.write("180   3.9519 0.72571 +0.68570 Mauguio\n")
    file.write("181  55.4100 0.93288 -0.35941 Observatoire des Makes, Saint-Louis\n")
    file.write("182  55.2586 0.93394 -0.35634 St. Paul, Reunion\n")
    file.write(
        "183  41.4200 0.72496 +0.68695 Starlab Observatory, Karachay-Cherkessia\n"
    )
    file.write("184   6.0361 0.72081 +0.69097 Valmeca Observatory, Puimichel\n")
    file.write(
        "185   7.4219 0.67876 +0.73200 Observatoire Astronomique Jurassien-Vicques\n"
    )
    file.write("186  66.8821 0.77679 +0.62781 Kitab\n")
    file.write("187  17.0733 0.61314 +0.78735 Astronomical Observatory, Borowiec\n")
    file.write("188  66.895550.782059+0.621762Majdanak\n")
    file.write("189   6.1514 0.69340 +0.71823 Geneva (before 1967)\n")
    file.write("190  68.6819 0.78382 +0.61909 Gissar\n")
    file.write("191  68.7811 0.78306 +0.62006 Dushanbe\n")
    file.write("192  69.2936 0.75213 +0.65692 Tashkent\n")
    file.write("193  69.2178 0.78648 +0.61610 Sanglok\n")
    file.write("194  18.0094 0.91807 -0.39579 Tivoli\n")
    file.write("195  11.4492 0.66804 +0.74174 Untermenzing Observatory, Munich\n")
    file.write("196   7.3331 0.65296 +0.75490 Homburg-Erbach\n")
    file.write("197  12.1836 0.71739 +0.69434 Bastia\n")
    file.write("198   8.756740.662195+0.746924Wildberg\n")
    file.write("199   2.4380 0.66659 +0.74294 Buthiers\n")
    file.write("200   4.3036 0.63385 +0.77088 Beersel Hills Observatory\n")
    file.write("201   7.6033 0.69871 +0.71332 Jonathan B. Postel Observatory\n")
    file.write("202   5.8997 0.73137 +0.67971 Tamaris Observatoire, La Seyne sur Mer\n")
    file.write("203   8.9955 0.70161 +0.71021 GiaGa Observatory\n")
    file.write("204   8.7708 0.69765 +0.71430 Schiaparelli Observatory\n")
    file.write("205  11.2731 0.71478 +0.69703 Obs. Casalecchio di Reno, Bologna\n")
    file.write("206  10.5667 0.4922  +0.8677  Haagaar Observatory, Eina\n")
    file.write("207   9.3065 0.70156 +0.71025 Osservatorio Antonio Grosso\n")
    file.write("208   9.5875 0.70893 +0.70294 Rivalta\n")
    file.write("209  11.568830.697904+0.714100Asiago Observatory, Cima Ekar-ADAS\n")
    file.write("210  76.9573 0.73042 +0.68104 Alma-Ata\n")
    file.write("211  11.1764 0.72338 +0.68815 Scandicci\n")
    file.write("212 355.357470.803253+0.593708Observatorio La Dehesilla\n")
    file.write("213   2.385390.749843+0.659421Observatorio Montcabre\n")
    file.write("214  11.6569 0.66709 +0.74258 Garching Observatory\n")
    file.write("215  10.7328 0.67021 +0.73981 Buchloe\n")
    file.write("216   5.6914 0.65732 +0.75114 Observatoire des Cote de Meuse\n")
    file.write("217  77.871140.730114+0.681643Assah\n")
    file.write("218  78.4541 0.95444 +0.29768 Hyderabad\n")
    file.write("219  78.7283 0.95618 +0.29216 Japal-Rangapur\n")
    file.write("220  78.8263 0.97627 +0.21634 Vainu Bappu Observatory, Kavalur\n")
    file.write("221  16.361700.919631-0.392203IAS Observatory, Hakos\n")
    file.write("222   2.4939 0.66113 +0.74777 Yerres-Canotiers\n")
    file.write("223  80.2464 0.97427 +0.22465 Madras\n")
    file.write("224   7.501710.673178+0.737048Ottmarsheim\n")
    file.write("225 288.8250 0.7298  +0.6814  Northwood Ridge Observatory\n")
    file.write("226  11.8858 0.70293 +0.70888 Guido Ruggieri Observatory, Padua\n")
    file.write("227 281.2853 0.73683 +0.67392 OrbitJet Observatory, Colden\n")
    file.write("228  13.8750 0.70038 +0.71147 Bruno Zugna Observatory, Trieste\n")
    file.write(
        "229  14.9743 0.75936 +0.64857 G. C. Gloriosi Astronomical Observatory, Salerno\n"
    )
    file.write("230  12.0133 0.6744  +0.7363  Mt. Wendelstein Observatory\n")
    file.write("231   5.3983 0.64403 +0.76253 Vesqueville\n")
    file.write("232   1.3317 0.7500  +0.6593  Masquefa Observatory\n")
    file.write(
        "233  10.5403 0.72226 +0.68931 Sauro Donati Astronomical Observatory, San Vito\n"
    )
    file.write("234   1.128330.614951+0.785931Coddenham Observatory\n")
    file.write("235  13.113520.696669+0.714993CAST Observatory, Talmassons\n")
    file.write("236  84.9465 0.55370 +0.82995 Tomsk\n")
    file.write("237   2.7333 0.6822  +0.7288  Baugy\n")
    file.write("238  10.9094 0.50204 +0.86197 Grorudalen Optical Observatory\n")
    file.write("239   8.4114 0.64506 +0.76159 Trebur\n")
    file.write("240   8.833170.662308+0.746832Herrenberg Sternwarte\n")
    file.write("241  13.4700 0.66465 +0.74474 Schaerding\n")
    file.write("242   1.6956 0.72681 +0.68460 Varennes\n")
    file.write("243   9.4130 0.59572 +0.80050 Umbrella Observatory, Fredenbeck\n")
    file.write("244   0.000000.000000 0.000000Geocentric Occultation Observation\n")
    file.write("245                           Spitzer Space Telescope\n")
    file.write("246  14.284760.659216+0.749664Klet Observatory-KLENOT\n")
    file.write("247                           Roving Observer\n")
    file.write("248   0.000000.000000 0.000000Hipparcos\n")
    file.write("249                           SOHO\n")
    file.write("250                           Hubble Space Telescope\n")
    file.write("251 293.246920.949577+0.312734Arecibo\n")
    file.write("252 243.205120.817719+0.573979Goldstone DSS 13, Fort Irwin\n")
    file.write("253 243.110470.815913+0.576510Goldstone DSS 14, Fort Irwin\n")
    file.write("254 288.511280.736973+0.673692Haystack, Westford\n")
    file.write("255  33.186890.705965+0.705886Yevpatoriya\n")
    file.write("256 280.160170.784451+0.618320Green Bank\n")
    file.write("257 243.124610.816796+0.575252Goldstone DSS 25, Fort Irwin\n")
    file.write("258                           Gaia\n")
    file.write("259  19.225860.349828+0.933688EISCAT Tromso UHF\n")
    file.write("260 149.0661 0.85560 -0.51626 Siding Spring Observatory-DSS\n")
    file.write("261 243.140220.836325+0.546877Palomar Mountain-DSS\n")
    file.write(
        "262 289.266260.873440-0.486052European Southern Observatory, La Silla-DSS\n"
    )
    file.write("266 204.523440.941701+0.337237New Horizons KBO Search-Subaru\n")
    file.write("267 204.530440.941705+0.337234New Horizons KBO Search-CFHT\n")
    file.write("268 289.308030.875516-0.482342New Horizons KBO Search-Magellan/Clay\n")
    file.write("269 289.309140.875510-0.482349New Horizons KBO Search-Magellan/Baade\n")
    file.write("270                           Unistellar Network, Roving Observer\n")
    file.write("273                           Euclid\n")
    file.write("274                           James Webb Space Telescope\n")
    file.write("275                           Non-geocentric Occultation Observation\n")
    file.write("276  20.382790.608295+0.791076Plonsk\n")
    file.write(
        "277 356.8175 0.56158 +0.82467 Royal Observatory, Blackford Hill, Edinburgh\n"
    )
    file.write("278 116.4494 0.76818 +0.63809 Peking, Transit of Venus site\n")
    file.write("279  10.728220.631526+0.772827Seeberg Observatory, Gotha (1787-1857)\n")
    file.write("280   8.9118 0.60114 +0.79646 Lilienthal\n")
    file.write("281  11.3522 0.71448 +0.69733 Bologna\n")
    file.write("282   4.3603 0.72245 +0.68912 Nimes\n")
    file.write("283   8.8163 0.60204 +0.79579 Bremen\n")
    file.write("284  15.8311 0.60536 +0.79329 Driesen\n")
    file.write("285   2.3708 0.66135 +0.74759 Flammarion Observatory, Juvisy\n")
    file.write("286 102.7883 0.90694 +0.42057 Yunnan Observatory\n")
    file.write("290 250.107990.842743+0.537438Mt. Graham-VATT\n")
    file.write("291 248.400240.849471+0.526470LPL/Spacewatch II\n")
    file.write("292 285.1058 0.76630 +0.64033 Burlington, New Jersey\n")
    file.write("293 285.5899 0.76936 +0.63668 Burlington remote site\n")
    file.write(
        "294 285.8467 0.76031 +0.64739 Astrophysical Obs., College of Staten Island\n"
    )
    file.write(
        "295 283.0000 0.7789  +0.6251  Catholic University Observatory, Washington\n"
    )
    file.write(
        "296 286.2200 0.73660 +0.67407 Dudley Observatory, Albany (after 1893)\n"
    )
    file.write("297 286.819  0.7203  +0.6913  Middlebury\n")
    file.write("298 287.3408 0.74943 +0.65988 Van Vleck Observatory\n")
    file.write("299 107.6160 0.99316 -0.11808 Bosscha Observatory, Lembang\n")
    file.write("300 133.544440.823370+0.565720Bisei Spaceguard Center-BATTeRS\n")
    file.write("301 288.8467 0.70279 +0.70926 Mont Megantic\n")
    file.write("302 288.88   0.990   +0.150   University of the Andes station\n")
    file.write("303 289.1296 0.98890 +0.15185 OAN de Llano del Hato, Merida\n")
    file.write("304 289.2980 0.87559 -0.48217 Las Campanas Observatory\n")
    file.write("305 109.5514 0.82066 +0.56963 Purple Mountain, Hainan Island station\n")
    file.write("306 290.6769 0.98477 +0.17381 Observatorio Taya Beixo, Barquisimeto\n")
    file.write("307 287.7166 0.72410 +0.68743 Shattuck Observatory, Hanover\n")
    file.write("309 289.595690.909943-0.414336Cerro Paranal\n")
    file.write("310 288.871640.739802+0.670574Minor Planet Center Test Code\n")
    file.write("312 112.334  0.9574  +0.2877  Tsingtao field station, Xisha Islands\n")
    file.write("318 115.691  0.85206 -0.52170 Quinns Rock\n")
    file.write(
        "319 116.1350 0.84883 -0.52702 Perth Observatory, Perth-Lowell Telescope\n"
    )
    file.write("320 116.4381 0.85859 -0.51102 Chiro Observatory\n")
    file.write("321 115.7571 0.85078 -0.52378 Craigie\n")
    file.write("322 116.1340 0.84882 -0.52703 Perth Observatory, Bickley-MCT\n")
    file.write("323 116.1350 0.84882 -0.52703 Perth Observatory, Bickley\n")
    file.write("324 116.3277 0.76598 +0.64072 Peking Observatory, Shaho Station\n")
    file.write("327 117.5750 0.76278 +0.64470 Peking Observatory, Xinglong Station\n")
    file.write("330 118.8209 0.84828 +0.52788 Purple Mountain Observatory, Nanking\n")
    file.write("333 249.5236 0.84936 +0.52642 Desert Eagle Observatory\n")
    file.write("334 120.3196 0.80925 +0.58552 Tsingtao\n")
    file.write("337 121.1843 0.85708 +0.51348 Sheshan, formerly Zo-Se\n")
    file.write("340 135.4853 0.82199 +0.56762 Toyonaka\n")
    file.write("341 137.9486 0.80669 +0.58923 Akashina\n")
    file.write("342 134.3189 0.83425 +0.54955 Shishikui\n")
    file.write("343 127.1258 0.78688 +0.61507 Younchun\n")
    file.write(
        "344 128.9767 0.80841 +0.58695 Bohyunsan Optical Astronomy Observatory\n"
    )
    file.write(
        "345 128.4575 0.80046 +0.59773 Sobaeksan Optical Astronomy Observatory\n"
    )
    file.write("346 127.3854 0.80474 +0.59166 KNUE Astronomical Observatory\n")
    file.write("347 139.9086 0.80417 +0.59244 Utsunomiya-Imaizumi\n")
    file.write("348 135.2669 0.81698 +0.57475 Ayabe\n")
    file.write("349 139.566220.810402+0.583916Ageo\n")
    file.write("350 139.2635 0.80504 +0.59132 Kurohone\n")
    file.write("351 135.8678 0.81939 +0.57135 Sakamoto\n")
    file.write("352 136.1778 0.82061 +0.56963 Konan\n")
    file.write("353 135.0648 0.82265 +0.56669 Nishi Kobe\n")
    file.write("354 140.0206 0.80109 +0.59674 Kawachi\n")
    file.write("355 139.2133 0.81618 +0.57590 Hadano\n")
    file.write("356 141.0867 0.78319 +0.61970 Kogota\n")
    file.write("357 140.0064 0.80807 +0.58712 Shimotsuma\n")
    file.write("358 140.1586 0.78856 +0.61296 Nanyo\n")
    file.write("359 135.1719 0.82782 +0.55912 Wakayama\n")
    file.write("360 132.9442 0.83314 +0.55138 Kuma Kogen\n")
    file.write("361 134.8933 0.82649 +0.56106 Sumoto\n")
    file.write("362 140.6550 0.73673 +0.67398 Ray Observatory\n")
    file.write("363 130.7703 0.83416 +0.54967 Yamada\n")
    file.write("364 130.5747 0.85213 +0.52164 YCPM Kagoshima Station\n")
    file.write("365 135.9579 0.82597 +0.56196 Uto Observatory\n")
    file.write("366 138.3003 0.81147 +0.58267 Miyasaka Observatory\n")
    file.write("367 133.1670 0.81504 +0.57747 Yatsuka\n")
    file.write("368 138.8117 0.81213 +0.58191 Ochiai\n")
    file.write("369 139.1500 0.8101  +0.5844  Chichibu\n")
    file.write("370 133.5273 0.83424 +0.54956 Kochi\n")
    file.write("371 133.5965 0.82433 +0.56431 Tokyo-Okayama\n")
    file.write("372 133.8276 0.83450 +0.54920 Geisei\n")
    file.write("373 135.3397 0.82866 +0.55797 Oishi\n")
    file.write("374 134.7196 0.81915 +0.57174 Minami-Oda Observatory\n")
    file.write("375 134.8708 0.8206  +0.5697  Uzurano\n")
    file.write("376 139.0392 0.81321 +0.58022 Uenohara\n")
    file.write("377 135.7933 0.82014 +0.57031 Kwasan Observatory, Kyoto\n")
    file.write("378 136.0142 0.82437 +0.56426 Murou\n")
    file.write("379 137.6279 0.82300 +0.56613 Hamamatsu-Yuto\n")
    file.write("380 137.0349 0.82190 +0.56772 Ishiki\n")
    file.write("381 137.625420.812172+0.581777Tokyo-Kiso\n")
    file.write("382 137.5553 0.80915 +0.58639 Tokyo-Norikura\n")
    file.write("383 137.8959 0.80218 +0.59526 Chirorin\n")
    file.write("384 138.1792 0.8219  +0.5678  Shimada\n")
    file.write("385 138.4680 0.82039 +0.56997 Nihondaira Observatory\n")
    file.write("386 138.3217 0.81121 +0.58309 Yatsugatake-Kobuchizawa\n")
    file.write("387 139.1944 0.81000 +0.58469 Tokyo-Dodaira\n")
    file.write("388 139.5421 0.81330 +0.57991 Tokyo-Mitaka\n")
    file.write("389 139.7447 0.81347 +0.57965 Tokyo (before 1938)\n")
    file.write("390 139.8725 0.80425 +0.59234 Utsunomiya\n")
    file.write("391 140.778430.786177+0.615960Sendai Observatory, Ayashi Station\n")
    file.write("392 141.3667 0.73355 +0.67741 JCPM Sapporo Station\n")
    file.write("393 140.1292 0.8090  +0.5858  JCPM Sakura Station\n")
    file.write("394 142.3208 0.70692 +0.70493 JCPM Hamatonbetsu Station\n")
    file.write("395 142.3583 0.7224  +0.6891  Tokyo-Asahikawa\n")
    file.write("396 142.4208 0.7236  +0.6879  Asahikawa\n")
    file.write("397 141.4761 0.73210 +0.67892 Sapporo Science Center\n")
    file.write("398 139.1080 0.80870 +0.58630 Nagatoro\n")
    file.write("399 144.5900 0.73158 +0.67950 Kushiro\n")
    file.write("400 143.7827 0.72344 +0.68811 Kitami\n")
    file.write("401 139.4208 0.8088  +0.5861  Oosato\n")
    file.write("402 136.3078 0.81800 +0.57335 Dynic Astronomical Observatory\n")
    file.write("403 137.0556 0.81593 +0.57625 Kani\n")
    file.write("404 140.9292 0.7909  +0.6099  Yamamoto\n")
    file.write("405 139.3292 0.8069  +0.5887  Kamihoriguchi\n")
    file.write("406 141.8233 0.72946 +0.68174 Bibai\n")
    file.write("407 140.3099 0.78426 +0.61837 Kahoku\n")
    file.write("408 138.1747 0.81121 +0.58328 Nyukasa\n")
    file.write("409 139.5211 0.81234 +0.58124 Kiyose and Mizuho\n")
    file.write("410 134.8910 0.81883 +0.57222 Sengamine\n")
    file.write("411 139.4170 0.80739 +0.58805 Oizumi\n")
    file.write("412 140.5991 0.80011 +0.59803 Iwaki\n")
    file.write("413 149.066080.855595-0.516262Siding Spring Observatory\n")
    file.write("414 149.0077 0.81694 -0.57499 Mount Stromlo\n")
    file.write("415 149.0636 0.81615 -0.57606 Kambah\n")
    file.write("416 149.1336 0.81701 -0.57485 Barton\n")
    file.write("417 137.1371 0.79611 +0.60317 Yanagida Astronomical Observatory\n")
    file.write("418 150.940340.857259-0.513294Tamworth\n")
    file.write("419 150.8329 0.83370 -0.55038 Windsor\n")
    file.write("420 151.2050 0.83126 -0.55404 Sydney\n")
    file.write("421 133.7650 0.83244 +0.55262 Mt. Kajigamori, Otoyo\n")
    file.write("422 151.0461 0.85503 -0.51709 Loomberah\n")
    file.write("423 151.124730.831807-0.553222North Ryde\n")
    file.write("424 149.0658 0.81758 -0.57405 Macquarie\n")
    file.write("425 152.9316 0.88796 -0.45843 Taylor Range Observatory, Brisbane\n")
    file.write("426 136.8217 0.85618 -0.51498 Woomera\n")
    file.write("427 138.7283 0.82667 -0.56084 Stockport\n")
    file.write("428 153.3970 0.88271 -0.46837 Reedy Creek\n")
    file.write("429 149.0400 0.81761 -0.57402 Hawker\n")
    file.write(
        "430 149.2123 0.85550 -0.51623 Rainbow Observatory, near Coonabarabran\n"
    )
    file.write("431 149.7578 0.83548 -0.54793 Mt. Tarana Observatory, Bathurst\n")
    file.write("432 153.082220.863790-0.502166Boambee\n")
    file.write("433 152.1078 0.84197 -0.53771 Bagnall Beach Observatory\n")
    file.write("434  10.9206 0.70765 +0.70419 S. Benedetto Po\n")
    file.write(
        "435  11.8936 0.70330 +0.70852 G. Colombo Astronomical Observatory, Padua\n"
    )
    file.write("436  11.3356 0.71658 +0.69528 Osservatorio di Livergnano\n")
    file.write("437 284.6971 0.76700 +0.63953 Haverford\n")
    file.write("438 287.3621 0.74059 +0.66978 Smith College Observatory, Northampton\n")
    file.write("439 253.2539 0.81156 +0.58288 ROTSE-III, Los Alamos\n")
    file.write("440 278.6842 0.73025 +0.68097 Elginfield Observatory\n")
    file.write("441 357.1697 0.55559 +0.82867 Swilken Brae, St. Andrews\n")
    file.write("442 357.4822 0.7477  +0.6619  Gualba Observatory\n")
    file.write("443 301.4656 0.82370 -0.56513 Obs. Astronomico Plomer, Buenos Aires\n")
    file.write("444 243.2794 0.83507 +0.54868 Star Cruiser Observatory\n")
    file.write("445 359.4200 0.7802  +0.6235  Observatorio d'Ontinyent\n")
    file.write("446 262.1666 0.87049 +0.49058 Kingsnake Observatory, Seguin\n")
    file.write("447 255.2056 0.77154 +0.63448 Centennial Observatory\n")
    file.write("448 253.2801 0.84543 +0.53268 Desert Moon Observatory, Las Cruces\n")
    file.write("449 279.6503 0.82617 +0.56156 Griffin Hunter Observatory, Bethune\n")
    file.write("450 279.3339 0.81857 +0.57254 Carla Jane Observatory, Charlotte\n")
    file.write("451 262.7569 0.79447 +0.60536 West Skies Observatory, Mulvane\n")
    file.write(
        "452 279.1063 0.8980  +0.4385  Big Cypress Observatory, Fort Lauderdale\n"
    )
    file.write("453 242.1331 0.82030 +0.57021 Edwards Raven Observatory\n")
    file.write(
        "454 283.376780.774542+0.630425Maryland Space Grant Consortium Observatory\n"
    )
    file.write("455 237.9636 0.78912 +0.61218 CBA Concord\n")
    file.write("456 358.8278 0.61348 +0.78709 Daventry Observatory\n")
    file.write("457  18.3403 0.66221 +0.74685 Partizanske\n")
    file.write("458 355.9806 0.75992 +0.64805 Guadarrama Observatory\n")
    file.write("459 288.1172 0.72607 +0.68538 Smith River Observatory, Danbury\n")
    file.write("460 265.9981 0.83010 +0.55579 Area 52 Observatory, Nashville\n")
    file.write(
        "461  19.8943 0.67153 +0.73869 University of Szeged, Piszkesteto Stn. (Konkoly)\n"
    )
    file.write("462 283.0842 0.77905 +0.62488 Mount Belleview Observatory\n")
    file.write("463 254.7375 0.76726 +0.63959 Sommers-Bausch Observatory, Boulder\n")
    file.write("464 288.5013 0.75109 +0.65799 Toby Point Observatory, Narragansett\n")
    file.write("465 174.7801 0.80166 -0.59578 Takapuna\n")
    file.write("466 174.8487 0.8002  -0.5977  Mount Molehill Observatory, Auckland\n")
    file.write("467 174.7766 0.80058 -0.59724 Auckland Observatory\n")
    file.write("468  13.3296 0.74652 +0.66349 Astronomical Observatory, Campo Catino\n")
    file.write("469   7.3820 0.67873 +0.73205 Courroux\n")
    file.write("470  13.327560.749268+0.660088Ceccano\n")
    file.write("471   8.2389 0.56364 +0.82325 Houstrup\n")
    file.write("472   6.3203 0.71225 +0.69998 Merlette\n")
    file.write("473  13.316610.694793+0.716822Remanzacco\n")
    file.write("474 170.464960.720773-0.691079Mount John Observatory, Lake Tekapo\n")
    file.write("475   7.6965 0.70747 +0.70443 Turin (before 1913)\n")
    file.write("476   7.140740.706597+0.705359Grange Observatory, Bussoleno\n")
    file.write("477   0.4856 0.62103 +0.78117 Galleywood\n")
    file.write("478   3.0896 0.72548 +0.68597 Lamalou-les-Bains\n")
    file.write("479   6.0505 0.73020 +0.68096 Sollies-Pont\n")
    file.write("480   0.7733 0.61466 +0.78616 Cockfield\n")
    file.write("481   7.930670.595365+0.800771Moorwarfen\n")
    file.write("482 357.1854 0.55560 +0.82866 St. Andrews\n")
    file.write(
        "483 173.8036 0.74734 -0.66254 Carter Observatory, Black Birch Station\n"
    )
    file.write("484 174.7594 0.75191 -0.65706 Happy Valley, Wellington\n")
    file.write("485 174.7654 0.75256 -0.65635 Carter Observatory, Wellington\n")
    file.write("486 175.47   0.765   -0.643   Palmerston North\n")
    file.write("487 355.4444 0.56858 +0.81989 Macnairston Observatory\n")
    file.write("488 358.3664 0.57486 +0.81553 Newcastle-upon-Tyne\n")
    file.write("489 359.87   0.612   +0.788   Hemingford Abbots\n")
    file.write("490 358.00   0.633   +0.772   Wimborne Minster\n")
    file.write("491 356.9000 0.76131 +0.64644 Centro Astronomico de Yebes\n")
    file.write("492 358.47   0.605   +0.795   Mickleover\n")
    file.write("493 357.4542 0.79753 +0.60182 Calar Alto\n")
    file.write("494 357.8361 0.61126 +0.78879 Stakenbridge\n")
    file.write("495 357.662470.597857+0.798936Altrincham\n")
    file.write("496 358.6860 0.6311  +0.7731  Bishopstoke\n")
    file.write("497 359.294490.622323+0.780160Loudwater\n")
    file.write("498 359.2581 0.61334 +0.78718 Earls Barton\n")
    file.write("499 359.790780.625578+0.777562Cheam\n")
    file.write("500   0.000000.000000 0.000000Geocentric\n")
    file.write("501   0.3475 0.63237 +0.77208 Herstmonceux\n")
    file.write("502   0.847930.618111+0.783475Colchester\n")
    file.write("503   0.0948 0.61400 +0.78667 Cambridge\n")
    file.write("504   4.3944 0.68553 +0.72570 Le Creusot\n")
    file.write("505   4.5639 0.6229  +0.7797  Simon Stevin\n")
    file.write("506   9.96   0.598   +0.797   Bendestorf\n")
    file.write("507   5.22   0.617   +0.783   Nyenheim\n")
    file.write("508   5.29   0.617   +0.783   Zeist\n")
    file.write("509   5.8725 0.73132 +0.67976 La Seyne sur Mer\n")
    file.write("510   8.0256 0.63185 +0.77257 Siegen\n")
    file.write("511   5.7157 0.72140 +0.69034 Haute Provence\n")
    file.write("512   4.4893 0.61477 +0.78606 Leiden (before 1860)\n")
    file.write("513   4.7855 0.69971 +0.71209 Lyons\n")
    file.write("514   8.438  0.6513  +0.7563  Mundenheim (1907-1913)\n")
    file.write("515   7.4956 0.64656 +0.76038 Volkssternwarte Dhaun, near Kirn\n")
    file.write("516   9.973210.595399+0.800741Hamburg (before 1909)\n")
    file.write("517   6.1358 0.69201 +0.71957 Geneva (from 1967)\n")
    file.write("518   9.9727 0.59545 +0.80071 Marine Observatory, Hamburg\n")
    file.write("519   8.2867 0.62598 +0.77729 Meschede\n")
    file.write("520   7.0966 0.63427 +0.77053 Bonn\n")
    file.write("521  10.887940.645624+0.761154Remeis Observatory, Bamberg\n")
    file.write("522   7.7677 0.66279 +0.74633 Strasbourg\n")
    file.write("523   8.6512 0.64251 +0.76374 Frankfurt\n")
    file.write("524   8.4605 0.6509  +0.7566  Mannheim\n")
    file.write("525   8.769170.633171+0.771473Marburg\n")
    file.write("526  10.1477 0.58426 +0.80886 Kiel\n")
    file.write("527   9.9431 0.5955  +0.8007  Altona\n")
    file.write("528   9.9426 0.62340 +0.77931 Gottingen\n")
    file.write("529  10.7229 0.50259 +0.86163 Christiania\n")
    file.write("530  10.6898 0.5911  +0.8039  Lubeck\n")
    file.write("531  12.4797 0.74545 +0.66434 Collegio Romano, Rome\n")
    file.write("532  11.6084 0.66853 +0.74130 Munich\n")
    file.write("533  11.8715 0.70335 +0.70847 Padua\n")
    file.write("534  12.3913 0.62606 +0.77719 Leipzig (since 1861)\n")
    file.write("535  13.3578 0.78782 +0.61386 Palermo\n")
    file.write("536  13.1062 0.61135 +0.78873 Berlin-Babelsberg\n")
    file.write("537  13.3642 0.6097  +0.7900  Urania Observatory, Berlin\n")
    file.write("538  13.8461 0.70998 +0.70187 Pola\n")
    file.write("539  14.1316 0.66968 +0.74024 Kremsmunster\n")
    file.write("540  14.2753 0.66470 +0.74477 Linz\n")
    file.write("541  14.3953 0.64306 +0.76331 Prague\n")
    file.write("542  13.0374 0.6091  +0.7904  Falkensee\n")
    file.write("543  12.3688 0.6260  +0.7772  Leipzig (before 1861)\n")
    file.write("544  13.351310.610644+0.789263Wilhelm Foerster Observatory, Berlin\n")
    file.write("545  16.3817 0.66767 +0.74200 Vienna (before 1879)\n")
    file.write("546  16.3549 0.66760 +0.74207 Oppolzer Observatory, Vienna\n")
    file.write("547  17.0363 0.62904 +0.77479 Breslau\n")
    file.write("548  13.3950 0.60999 +0.78976 Berlin (1835-1913)\n")
    file.write("549  17.6257 0.50341 +0.86116 Uppsala\n")
    file.write("550  11.4196 0.5943  +0.8015  Schwerin\n")
    file.write("551  18.1895 0.67201 +0.73808 Hurbanovo, formerly O'Gyalla\n")
    file.write("552  11.3418 0.71485 +0.69700 Osservatorio S. Vittore, Bologna\n")
    file.write("553  18.9938 0.64002 +0.76574 Chorzow\n")
    file.write("554   8.3959 0.63684 +0.76845 Burgsolms Observatory, Wetzlar\n")
    file.write("555  19.8263 0.64336 +0.76306 Cracow-Fort Skala\n")
    file.write("556  11.26   0.675   +0.734   Reintal, near Munich\n")
    file.write("557  14.779610.645250+0.761529Ondrejov\n")
    file.write("558  21.0303 0.61396 +0.78672 Warsaw\n")
    file.write("559  14.98   0.793   +0.607   Serra La Nave\n")
    file.write("560  10.931000.703262+0.708561Madonna di Dossobuono\n")
    file.write("561  19.8943 0.67153 +0.73869 Piszkesteto Stn. (Konkoly)\n")
    file.write("562  15.9236 0.66938 +0.74062 Figl Observatory, Vienna\n")
    file.write("563  13.60   0.671   +0.739   Seewalchen\n")
    file.write("564  11.19   0.671   +0.741   Herrsching\n")
    file.write("565  10.1344 0.70437 +0.70746 Bassano Bresciano\n")
    file.write("566 203.7424 0.93623 +0.35156 Haleakala-NEAT/GEODSS\n")
    file.write("567  12.7117 0.69783 +0.71387 Chions\n")
    file.write("568 204.5278 0.94171 +0.33725 Maunakea\n")
    file.write("569  24.9587 0.49891 +0.86375 Helsinki\n")
    file.write("570  25.2990 0.5794  +0.8123  Vilnius (since 1939)\n")
    file.write("571  10.63   0.704   +0.708   Cavriana\n")
    file.write("572   6.89   0.631   +0.772   Cologne\n")
    file.write("573   9.6612 0.6145  +0.7862  Eldagsen\n")
    file.write("574  10.2667 0.70463 +0.70721 Gottolengo\n")
    file.write("575   6.808  0.68219 +0.72894 La Chaux de Fonds\n")
    file.write("576   0.3760 0.63067 +0.77346 Burwash\n")
    file.write("577   7.50   0.678   +0.734   Metzerlen Observatory\n")
    file.write("578  27.99   0.898   -0.439   Linden Observatory\n")
    file.write("579   8.85   0.711   +0.701   Novi Ligure\n")
    file.write("580  15.4936 0.68242 +0.72862 Graz\n")
    file.write("581  22.80   0.830   -0.556   Sedgefield\n")
    file.write("582   1.2408 0.61682 +0.78447 Orwell Park\n")
    file.write("583  30.2717 0.69087 +0.72056 Odesa-Mayaky\n")
    file.write("584  30.2946 0.50213 +0.86189 Leningrad\n")
    file.write("585  30.524620.640067+0.765748Kyiv comet station\n")
    file.write("586   0.1423 0.73358 +0.67799 Pic du Midi\n")
    file.write("587   9.229180.697459+0.714479Sormano\n")
    file.write("588  11.25   0.715   +0.697   Eremo di Tizzano\n")
    file.write("589  12.643690.738223+0.672386Santa Lucia Stroncone\n")
    file.write("590   7.46   0.678   +0.734   Metzerlen\n")
    file.write("591   9.6258 0.60995 +0.78979 Resse Observatory\n")
    file.write("592   7.021140.628245+0.775437Solingen\n")
    file.write("593  11.17   0.739   +0.671   Monte Argentario\n")
    file.write("594  13.2033 0.74497 +0.66529 Monte Autore\n")
    file.write("595  13.525780.696925+0.714749Farra d'Isonzo\n")
    file.write("596  12.6183 0.74446 +0.66545 Colleverde di Guidonia\n")
    file.write("597   9.6631 0.61461 +0.78621 Springe\n")
    file.write("598  11.334090.717444+0.694448Loiano\n")
    file.write("599  13.557640.739311+0.671604Campo Imperatore-CINEOS\n")
    file.write("600  11.4708 0.71618 +0.69564 TLC Observatory, Bologna\n")
    file.write("601  13.7281 0.63009 +0.77394 Engelhardt Observatory, Dresden\n")
    file.write("602  16.3854 0.66764 +0.74203 Urania Observatory, Vienna\n")
    file.write("603  10.1300 0.58622 +0.80745 Bothkamp\n")
    file.write("604  13.475240.610235+0.789572Archenhold Sternwarte, Berlin-Treptow\n")
    file.write("605   7.1130 0.62142 +0.78086 Marl\n")
    file.write("606   9.9956 0.59353 +0.80212 Norderstedt\n")
    file.write("607   8.0000 0.6277  +0.7760  Hagen Observatory, Ronkhausen\n")
    file.write("608 203.7420 0.93623 +0.35156 Haleakala-AMOS\n")
    file.write("609  12.8533 0.73772 +0.67314 Osservatorio Polino\n")
    file.write("610  11.3431 0.71577 +0.69604 Pianoro\n")
    file.write("611   8.6531 0.64877 +0.75848 Starkenburg Sternwarte, Heppenheim\n")
    file.write("612   7.10   0.625   +0.778   Lenkerbeck\n")
    file.write("613   7.0709 0.62504 +0.77800 Heisingen\n")
    file.write("614   2.467  0.6621  +0.7469  Soisy-sur-Seine\n")
    file.write("615   6.9067 0.71233 +0.70014 St. Veran\n")
    file.write("616  16.583480.654655+0.753466Brno\n")
    file.write("617   2.5725 0.66496 +0.74437 Arbonne la Foret\n")
    file.write("618   5.0077 0.72750 +0.68382 Martigues\n")
    file.write("619   2.090130.749506+0.659828Sabadell\n")
    file.write("620   2.9517 0.77110 +0.63463 Observatorio Astronomico de Mallorca\n")
    file.write("621   7.485030.629461+0.774501Bergisch Gladbach\n")
    file.write("622   7.5680 0.68778 +0.72358 Oberwichtrach\n")
    file.write("623   5.5667 0.63577 +0.76932 Liege\n")
    file.write("624   9.6167 0.64723 +0.75977 Dertingen\n")
    file.write(
        "625 203.5683 0.93557 +0.35201 Kihei-AMOS Remote Maui Experimental Site\n"
    )
    file.write("626   4.9864 0.62847 +0.77524 Geel\n")
    file.write("627   5.2146 0.72002 +0.69168 Blauvac\n")
    file.write("628   6.843660.624789+0.778184Mulheim-Ruhr\n")
    file.write("629  20.1511 0.69273 +0.71880 Szeged Observatory\n")
    file.write("630   7.2367 0.67051 +0.73951 Osenbach\n")
    file.write("631  10.022930.595992+0.800307Hamburg-Georgswerder\n")
    file.write("632  11.1739 0.72380 +0.68773 San Polo A Mosciano\n")
    file.write("633   9.9339 0.71930 +0.69238 Romito\n")
    file.write("634   5.1456 0.70182 +0.71007 Crolles\n")
    file.write("635   2.9019 0.73605 +0.67467 Pergignan\n")
    file.write("636   6.9794 0.62524 +0.77783 Essen\n")
    file.write("637  10.0903 0.59326 +0.80232 Hamburg-Himmelsmoor\n")
    file.write("638   8.8933 0.61778 +0.78374 Detmold\n")
    file.write("639  13.7233 0.62933 +0.77456 Dresden\n")
    file.write("640  13.5996 0.6429  +0.7634  Senftenberger Sternwarte\n")
    file.write("641  20.0272 0.82468 -0.56374 Overberg\n")
    file.write("642 236.6850 0.6648  +0.7445  Oak Bay, Victoria\n")
    file.write("643 243.2794 0.83507 +0.54868 OCA-Anza Observatory\n")
    file.write("644 243.140220.836325+0.546877Palomar Mountain/NEAT\n")
    file.write("645 254.179420.841945+0.538563Apache Point-Sloan Digital Sky Survey\n")
    file.write("646 242.4369 0.82999 +0.55603 Santana Observatory, Rancho Cucamonga\n")
    file.write("647 245.9683 0.6337  +0.7712  Stone Finder Observatory, Calgary\n")
    file.write("648 249.398220.852115+0.522053Winer Observatory, Sonoita\n")
    file.write("649 265.3003 0.78207 +0.62117 Powell Observatory, Louisburg\n")
    file.write("650 242.9028 0.83510 +0.54836 Temecula\n")
    file.write("651 249.419160.852069+0.522123Grasslands Observatory, Tucson\n")
    file.write("652 245.9333 0.6291  +0.7749  Rock Finder Observatory, Calgary\n")
    file.write("653 237.8678 0.68091 +0.72996 Torus Observatory, Buckley\n")
    file.write(
        "654 242.318410.826471+0.561727Table Mountain Observatory, Wrightwood-PHMC\n"
    )
    file.write("655 236.383  0.6656  +0.7438  Sooke\n")
    file.write("656 236.3921 0.66580 +0.74367 Victoria\n")
    file.write("657 236.6903 0.66437 +0.74491 Climenhaga Observatory, Victoria\n")
    file.write("658 236.583000.663631+0.745601Dominion Astrophysical Observatory\n")
    file.write("659 237.0514 0.66257 +0.74650 Heron Cove Observatory, Orcas\n")
    file.write("660 237.7379 0.79038 +0.61059 Leuschner Observatory, Berkeley\n")
    file.write(
        "661 245.7117 0.63251 +0.77222 Rothney Astrophysical Observatory, Priddis\n"
    )
    file.write("662 238.3545 0.79619 +0.60335 Lick Observatory, Mount Hamilton\n")
    file.write("663 248.3136 0.83483 +0.54879 Red Mountain Observatory\n")
    file.write("664 239.2775 0.6840  +0.7273  Manastash Ridge Observatory\n")
    file.write("665 240.9903 0.82215 +0.56781 Wallis Observatory\n")
    file.write("666 241.1692 0.8270  +0.5604  Moorpark College Observatory\n")
    file.write("667 240.009210.684483+0.726626Wanapum Dam\n")
    file.write("668 240.82   0.821   +0.568   San Emigdio Peak\n")
    file.write("669 240.8238 0.82540 +0.56279 Ojai\n")
    file.write("670 240.9558 0.82775 +0.55922 Camarillo\n")
    file.write("671 242.001980.827184+0.560523Stony Ridge\n")
    file.write("672 241.9436 0.82794 +0.55942 Mount Wilson\n")
    file.write("673 242.317830.826474+0.561722Table Mountain Observatory, Wrightwood\n")
    file.write("674 242.336050.826464+0.561730Ford Observatory, Wrightwood\n")
    file.write("675 243.137460.836357+0.546831Palomar Mountain\n")
    file.write("676 242.3907 0.83553 +0.54762 San Clemente\n")
    file.write("677 242.8281 0.82746 +0.56012 Lake Arrowhead\n")
    file.write("678 248.2597 0.83352 +0.55083 Fountain Hills\n")
    file.write("679 244.5367 0.85792 +0.51292 San Pedro Martir\n")
    file.write("680 244.78   0.833   +0.554   Los Angeles\n")
    file.write("681 245.8858 0.62954 +0.77459 Calgary\n")
    file.write("682 247.6381 0.79932 +0.59932 Kanab\n")
    file.write("683 248.9182 0.84751 +0.52922 Goodricke-Pigott Observatory, Tucson\n")
    file.write("684 247.5100 0.82512 +0.56356 Prescott\n")
    file.write("685 247.84   0.816   +0.575   Williams\n")
    file.write("686 249.2092 0.84512 +0.53359 U. of Minn. Infrared Obs., Mt. Lemmon\n")
    file.write("687 248.3473 0.81848 +0.57318 Northern Arizona University, Flagstaff\n")
    file.write(
        "688 248.4645 0.81938 +0.57193 Lowell Observatory, Anderson Mesa Station\n"
    )
    file.write("689 248.2601 0.81851 +0.57319 U.S. Naval Observatory, Flagstaff\n")
    file.write("690 248.3367 0.81832 +0.57344 Lowell Observatory, Flagstaff\n")
    file.write(
        "691 248.399660.849466+0.526479Steward Observatory, Kitt Peak-Spacewatch\n"
    )
    file.write("692 249.0513 0.84679 +0.53036 Steward Observatory, Tucson\n")
    file.write("693 249.267450.845317+0.533211Catalina Station, Tucson\n")
    file.write("694 248.9943 0.84700 +0.53009 Tumamoc Hill, Tucson\n")
    file.write("695 248.405330.849504+0.526425Kitt Peak\n")
    file.write("696 249.1154 0.85205 +0.52249 Whipple Observatory, Mt. Hopkins\n")
    file.write("697 248.383810.849546+0.526308Kitt Peak, McGraw-Hill\n")
    file.write("698 249.267360.845316+0.533212Mt. Bigelow\n")
    file.write("699 248.463310.819380+0.571930Lowell Observatory-LONEOS\n")
    file.write("700 250.3817 0.80656 +0.58960 Chinle\n")
    file.write("701 249.797160.853823+0.519224Junk Bond Observatory, Sierra Vista\n")
    file.write(
        "702 252.8117 0.8305  +0.5561  Joint Obs. for cometary research, Socorro\n"
    )
    file.write("703 249.267360.845315+0.533213Catalina Sky Survey\n")
    file.write("704 253.340930.831869+0.553542Lincoln Laboratory ETS, New Mexico\n")
    file.write("705 254.179420.841945+0.538563Apache Point\n")
    file.write("706 253.9366 0.78294 +0.62043 Salida\n")
    file.write("707 254.56   0.774   +0.633   Chamberlin field station\n")
    file.write("708 255.0475 0.77092 +0.63520 Chamberlin Observatory, Denver\n")
    file.write("709 254.228820.840250+0.541096W & B Observatory, Cloudcroft\n")
    file.write("710 254.7336 0.77980 +0.62458 MPO Observatory, Florissant\n")
    file.write("711 255.9785 0.86114 +0.50731 McDonald Observatory, Fort Davis\n")
    file.write(
        "712 255.118670.778365+0.626250USAF Academy Observatory, Colorado Springs\n"
    )
    file.write("713 254.9897 0.76865 +0.63793 Thornton\n")
    file.write("714 246.8173 0.82444 +0.56439 Bagdad\n")
    file.write("715 253.2759 0.84546 +0.53264 Jornada Observatory, Las Cruces\n")
    file.write(
        "716 255.2489 0.77753 +0.62731 Palmer Divide Observatory, Colorado Springs\n"
    )
    file.write("717 256.0481 0.86160 +0.50636 Prude Ranch\n")
    file.write("718 247.7042 0.76004 +0.64802 Tooele\n")
    file.write("719 253.086080.829384+0.557204Etscorn Observatory\n")
    file.write("720 259.6261 0.90216 +0.43018 Universidad de Monterrey\n")
    file.write("721 259.7312 0.76271 +0.64476 Lime Creek\n")
    file.write("722 264.4192 0.87017 +0.49110 Missouri City\n")
    file.write("723 263.3300 0.82134 +0.56861 Cottonwood Observatory, Ada\n")
    file.write("724 260.8053 0.94388 +0.33026 National Observatory, Tacubaya\n")
    file.write("725 261.3453 0.86883 +0.49358 Fair Oaks Ranch\n")
    file.write("726 265.6933 0.69024 +0.72120 Brainerd\n")
    file.write("727 262.538720.813941+0.579096Zeno Observatory, Edmond\n")
    file.write("728 262.6084 0.88610 +0.46194 Corpus Christi\n")
    file.write(
        "729 262.878580.648804+0.758451Glenlea Astronomical Observatory, Winnipeg\n"
    )
    file.write(
        "730 262.841430.671544+0.738537University of North Dakota, Grand Forks\n"
    )
    file.write("731 272.6711 0.77290 +0.63244 Rose-Hulman Observatory, Terre Haute\n")
    file.write("732 263.2300 0.95591 +0.29359 Oaxaca\n")
    file.write("733 263.3546 0.83802 +0.54387 Allen, Texas\n")
    file.write("734 263.997580.779425+0.624489Farpoint Observatory, Eskridge\n")
    file.write("735 264.406400.872133+0.487634George Observatory, Needville\n")
    file.write("736 263.3357 0.87006 +0.49132 Houston\n")
    file.write("737 275.6633 0.8282  +0.5586  New Bullpen Observatory, Alpharetta\n")
    file.write(
        "738 267.6733 0.7788  +0.6252  Observatory of the State University of Missouri\n"
    )
    file.write("739 265.2440 0.77965 +0.62419 Sunflower Observatory, Olathe\n")
    file.write("740 265.3383 0.8511  +0.5233  SFA Observatory, Nacogdoches\n")
    file.write("741 266.8503 0.71493 +0.69692 Goodsell Observatory, Northfield\n")
    file.write("742 266.312160.748989+0.660428Drake University, Des Moines\n")
    file.write("743 267.761480.708545+0.703382University of Minnesota, Minneapolis\n")
    file.write("744 273.8378 0.76884 +0.63735 Doyan Rose Observatory, Indianapolis\n")
    file.write("745 267.1747 0.77569 +0.62906 Morrison Obervatory, Glasgow\n")
    file.write("746 275.2254 0.72551 +0.68597 Brooks Observatory, Mt. Pleasant\n")
    file.write("747 268.9292 0.86373 +0.50227 Highland Road Park Observatory\n")
    file.write("748 268.4680 0.75014 +0.65912 Van Allen Observatory, Iowa City\n")
    file.write("749 276.1642 0.82795 +0.55902 Oakwood\n")
    file.write("750 268.7282 0.71059 +0.70131 Hobbs Observatory, Fall Creek\n")
    file.write("751 269.2439 0.78038 +0.62324 Lake Saint Louis\n")
    file.write("752 275.4647 0.82278 +0.56659 Puckett Observatory, Mountain Town\n")
    file.write("753 270.590690.731622+0.679491Washburn Observatory, Madison\n")
    file.write("754 271.4432 0.73762 +0.67303 Yerkes Observatory, Williams Bay\n")
    file.write("755 274.6478 0.73353 +0.67743 Optec Observatory\n")
    file.write(
        "756 272.325670.743605+0.666407Dearborn Observatory, Evanston (bef. July 1939)\n"
    )
    file.write("757 280.0050 0.8096  +0.5851  High Point\n")
    file.write("758 279.2379 0.88044 +0.47257 BCC Observatory, Cocoa\n")
    file.write("759 273.1947 0.80946 +0.58530 Nashville\n")
    file.write("760 273.6048 0.77216 +0.63337 Goethe Link Observatory, Brooklyn\n")
    file.write("761 277.6456 0.88138 +0.47083 Zephyrhills\n")
    file.write("762 274.2008 0.70885 +0.70304 Four Winds Observatory, Lake Leelanau\n")
    file.write("763 280.4658 0.72157 +0.69009 King City\n")
    file.write("764 275.1439 0.83264 +0.55205 Puckett Observatory, Stone Mountain\n")
    file.write("765 275.5775 0.77669 +0.62784 Cincinnati\n")
    file.write(
        "766 275.5167 0.73600 +0.67477 Michigan State University Obs., East Lansing\n"
    )
    file.write("767 276.2697 0.74102 +0.66930 Ann Arbor\n")
    file.write(
        "768 272.324880.743585+0.666430Dearborn Observatory, Evanston (aft. Oct. 1939)\n"
    )
    file.write("769 276.9892 0.76716 +0.63936 McMillin Observatory, Columbus\n")
    file.write("770 274.0786 0.77573 +0.62900 Crescent Moon Observatory, Columbus\n")
    file.write("771 277.57   0.922   +0.389   Boyeros Observatory, Havana\n")
    file.write("772 284.0865 0.70517 +0.70669 Boltwood Observatory, Stittsville\n")
    file.write(
        "773 278.4318 0.74966 +0.65966 Warner and Swasey Observatory, Cleveland\n"
    )
    file.write(
        "774 278.9250 0.74905 +0.66039 Warner and Swasey Nassau Station, Chardon\n"
    )
    file.write("775 284.6168 0.76029 +0.64743 Sayre Observatory, South Bethlehem\n")
    file.write("776 284.4669 0.73472 +0.67619 Foggy Bottom, Hamilton\n")
    file.write("777 280.6017 0.72454 +0.68695 Toronto\n")
    file.write("778 279.9778 0.76172 +0.64582 Allegheny Observatory, Pittsburgh\n")
    file.write(
        "779 280.5779 0.72219 +0.68943 David Dunlap Observatory, Richmond Hill\n"
    )
    file.write(
        "780 281.4778 0.78868 +0.61280 Leander McCormick Observatory, Charlottesville\n"
    )
    file.write("781 281.5075 1.00045 -0.00405 Quito\n")
    file.write("782 281.65   0.999   +0.000   Quito, comet astrograph station\n")
    file.write("783 282.02   0.783   +0.622   Rixeyville\n")
    file.write("784 282.2146 0.74140 +0.66895 Stull Observatory, Alfred University\n")
    file.write("785 285.3542 0.76323 +0.64397 Fitz-Randolph Observatory, Princeton\n")
    file.write(
        "786 282.9345 0.77906 +0.62487 U.S. Naval Obs., Washington (since 1893)\n"
    )
    file.write(
        "787 282.9494 0.77934 +0.62451 U.S. Naval Obs., Washington (before 1893)\n"
    )
    file.write("788 284.3667 0.76953 +0.63650 Mount Cuba Observatory, Wilmington\n")
    file.write("789 284.5940 0.73188 +0.67922 Litchfield Observatory, Clinton\n")
    file.write("790 284.2835 0.70343 +0.70840 Dominion Observatory, Ottawa\n")
    file.write(
        "791 284.5236 0.76713 +0.63937 Flower and Cook Observatory, Philadelphia\n"
    )
    file.write(
        "792 288.299050.751746+0.657236University of Rhode Island, Quonochontaug\n"
    )
    file.write(
        "793 286.2515 0.7365  +0.6742  Dudley Observatory, Albany (before 1893)\n"
    )
    file.write(
        "794 286.1100 0.74789 +0.66161 Vassar College Observatory, Poughkeepsie\n"
    )
    file.write("795 286.038610.757969+0.650106Rutherford\n")
    file.write("796 286.45   0.755   +0.654   Stamford\n")
    file.write("797 287.0751 0.75218 +0.65676 Yale Observatory, New Haven\n")
    file.write("798 287.0154 0.75093 +0.65822 Yale Observatory, Bethany\n")
    file.write("799 288.8650 0.73896 +0.67150 Winchester\n")
    file.write("800 288.4511 0.96006 -0.28021 Harvard Observatory, Arequipa\n")
    file.write("801 288.442330.738364+0.672183Oak Ridge Observatory\n")
    file.write("802 288.871640.739802+0.670574Harvard Observatory, Cambridge\n")
    file.write("803 288.9167 0.74543 +0.66436 Taunton\n")
    file.write("804 289.3121 0.83421 -0.54976 Santiago-San Bernardo\n")
    file.write("805 288.9800 0.83997 -0.54145 Santiago-Cerro El Roble\n")
    file.write("806 289.4513 0.83584 -0.54738 Santiago-Cerro Calan\n")
    file.write("807 289.1941 0.86560 -0.49980 Cerro Tololo Observatory, La Serena\n")
    file.write("808 290.6708 0.85098 -0.52414 El Leoncito\n")
    file.write(
        "809 289.266260.873440-0.486052European Southern Observatory, La Silla\n"
    )
    file.write("810 288.5154 0.73712 +0.67352 Wallace Observatory, Westford\n")
    file.write("811 289.895650.752586+0.656289Maria Mitchell Observatory, Nantucket\n")
    file.write("812 288.4543 0.83992 -0.54093 Vina del Mar\n")
    file.write("813 289.3083 0.83533 -0.54805 Santiago-Quinta Normal (1862-1920)\n")
    file.write("814 288.419170.746007+0.663734North Scituate\n")
    file.write("815 289.3479 0.83539 -0.54799 Santiago-Santa Lucia (1849-1861)\n")
    file.write("816 285.7583 0.71645 +0.69542 Rand Observatory\n")
    file.write("817 288.6104 0.74018 +0.67017 Sudbury\n")
    file.write("818 286.4167 0.7040  +0.7079  Gemeaux Observatory, Laval\n")
    file.write("819 284.3850 0.69720 +0.71451 Val-des-Bois\n")
    file.write("820 295.375810.930491-0.365872Tarija\n")
    file.write("821 295.450410.852688-0.521032Cordoba-Bosque Alegre\n")
    file.write("822 295.801370.854203-0.518325Cordoba\n")
    file.write("823 288.1691 0.73715 +0.67354 Fitchburg\n")
    file.write("824 285.7528 0.71641 +0.69546 Lake Clear\n")
    file.write("825 288.2595 0.74033 +0.67003 Granville\n")
    file.write("826 288.2282 0.69312 +0.71843 Plessissville\n")
    file.write("827 287.5393 0.66190 +0.74710 Saint-Felicien\n")
    file.write("828 288.9758 0.74656 +0.66310 Assonet\n")
    file.write("829 290.6979 0.85102 -0.52411 Complejo Astronomico El Leoncito\n")
    file.write("830 288.5697 0.73491 +0.67590 Hudson\n")
    file.write(
        "831 277.4134 0.87191 +0.48804 Rosemary Hill Observatory, University of Florida\n"
    )
    file.write("832 283.1850 0.7653  +0.6416  Etters\n")
    file.write(
        "833 301.4633 0.82373 -0.56508 Obs. Astronomico de Mercedes, Buenos Aires\n"
    )
    file.write("834 301.5654 0.82398 -0.56473 Buenos Aires-AAAA\n")
    file.write("835 288.6428 0.73709 +0.67354 Drum Hill Station, Chelmsford\n")
    file.write("836 288.5011 0.74708 +0.66252 Furnace Brook Observatory, Cranston\n")
    file.write("837 279.7553 0.89228 +0.44996 Jupiter\n")
    file.write("838 275.8628 0.77000 +0.63596 Dayton\n")
    file.write("839 302.0678 0.82097 -0.56906 La Plata\n")
    file.write("840 276.2833 0.73235 +0.67870 Flint\n")
    file.write("841 279.442330.796229+0.603220Martin Observatory, Blacksburg\n")
    file.write("842 282.7678 0.76901 +0.63713 Gettysburg College Observatory\n")
    file.write("843 273.0648 0.82481 +0.56357 Emerald Lane Observatory, Decatur\n")
    file.write("844 303.809820.822499-0.566884Observatorio Astronomico Los Molinos\n")
    file.write("845 283.5058 0.73942 +0.67107 Ford Observatory, Ithaca\n")
    file.write(
        "846 269.655010.779842+0.623926Principia Astronomical Observatory, Elsah\n"
    )
    file.write("847 275.9750 0.7078  +0.7041  Lunar Cafe Observator, Flint\n")
    file.write("848 237.0219 0.72412 +0.68741 Tenagra Observatory, Cottage Grove\n")
    file.write("849 265.1694 0.77927 +0.62467 Everstar Observatory, Olathe\n")
    file.write("850 274.0802 0.81810 +0.57333 Cordell-Lorenz Observatory, Sewanee\n")
    file.write("851 296.419620.712830+0.698986Burke-Gaffney Observatory, Halifax\n")
    file.write("852 269.4050 0.7805  +0.6231  River Moss Observatory, St. Peters\n")
    file.write("853 249.1517 0.84365 +0.53544 Biosphere 2 Observatory\n")
    file.write("854 249.179950.846183+0.531351Sabino Canyon Observatory, Tucson\n")
    file.write("855 266.5383 0.7093  +0.7026  Wayside Observatory, Minnetonka\n")
    file.write("856 242.5540 0.8300  +0.5560  Riverside\n")
    file.write("857 249.3992 0.85213 +0.52204 Iowa Robotic Observatory, Sonoita\n")
    file.write("858 253.7800 0.8194  +0.5719  Tebbutt Observatory, Edgewood\n")
    file.write("859 316.3097 0.94132 -0.33707 Wykrota Observatory-CEAMIG\n")
    file.write("860 313.0347 0.92108 -0.38842 Valinhos\n")
    file.write("861 312.9204 0.92253 -0.38487 Barao Geraldo\n")
    file.write("862 138.5262 0.80861 +0.58658 Saku\n")
    file.write("863 137.18   0.807   +0.588   Furukawa\n")
    file.write("864 130.7533 0.84257 +0.53680 Kumamoto\n")
    file.write("865 285.8792 0.74765 +0.66189 Emmy Observatory, New Paltz\n")
    file.write("866 283.5100 0.7784  +0.6257  U.S. Naval Academy, Michelson\n")
    file.write("867 134.1222 0.81671 +0.57522 Saji Observatory\n")
    file.write("868 135.1359 0.83066 +0.55492 Hidaka Observatory\n")
    file.write("869 133.4298 0.83480 +0.54870 Tosa\n")
    file.write("870 313.174110.921798-0.386786Campinas\n")
    file.write("871 134.3925 0.82256 +0.56678 Akou\n")
    file.write("872 134.2411 0.82904 +0.55734 Tokushima\n")
    file.write("873 133.7717 0.82410 +0.56455 Kurashiki Observatory\n")
    file.write("874 314.417350.924359-0.380986Observatorio do Pico dos Dias, Itajuba\n")
    file.write("875 139.2353 0.80896 +0.58593 Yorii\n")
    file.write("876 139.2467 0.80762 +0.58774 Honjo\n")
    file.write("877 139.0828 0.81194 +0.58196 Okutama\n")
    file.write("878 136.9142 0.82019 +0.57019 Kagiya\n")
    file.write("879 137.3535 0.81970 +0.57099 Tokai\n")
    file.write("880 316.7771 0.92169 -0.38664 Rio de Janeiro\n")
    file.write("881 137.2571 0.81872 +0.57230 Toyota\n")
    file.write("882 137.3558 0.81842 +0.57281 JCPM Oi Station\n")
    file.write("883 138.4215 0.81986 +0.57065 Shizuoka\n")
    file.write("884 138.0792 0.8187  +0.5724  Kawane\n")
    file.write("885 138.4667 0.82049 +0.56975 JCPM Yakiimo Station\n")
    file.write("886 138.9367 0.81836 +0.57280 Mishima\n")
    file.write("887 139.3367 0.80745 +0.58798 Ojima\n")
    file.write("888 138.9952 0.81885 +0.57217 Gekko\n")
    file.write("889 140.1427 0.80322 +0.59372 Karasuyama\n")
    file.write("890 140.2500 0.8108  +0.5834  JCPM Tone Station\n")
    file.write("891 140.8633 0.78606 +0.61609 JCPM Kimachi Station\n")
    file.write("892 139.4753 0.80852 +0.58650 YGCO Hoshikawa and Nagano Stations\n")
    file.write("893 140.862220.786233+0.615870Sendai Municipal Observatory\n")
    file.write("894 138.4476 0.81113 +0.58321 Kiyosato\n")
    file.write("895 140.7203 0.78573 +0.61658 Hatamae\n")
    file.write("896 138.3678 0.81132 +0.58292 Yatsugatake South Base Observatory\n")
    file.write("897 139.4929 0.80797 +0.58725 YGCO Chiyoda Station\n")
    file.write("898 138.1883 0.82107 +0.56899 Fujieda\n")
    file.write("899 142.5500 0.7224  +0.6891  Toma\n")
    file.write("900 135.989940.819572+0.571083Moriyama\n")
    file.write("901 137.0877 0.81664 +0.57525 Tajimi\n")
    file.write("902 132.2208 0.82775 +0.55922 Ootake\n")
    file.write("903 135.1769 0.81738 +0.57418 Fukuchiyama and Kannabe\n")
    file.write("904 135.12   0.824   +0.565   Go-Chome and Kobe-Suma\n")
    file.write("905 135.9246 0.83368 +0.55040 Nachi-Katsuura Observatory\n")
    file.write("906 145.667  0.8113  -0.5837  Cobram\n")
    file.write("907 144.9758 0.79082 -0.61001 Melbourne\n")
    file.write("908 137.2467 0.80352 +0.59330 Toyama\n")
    file.write("909 237.8717 0.6711  +0.7389  Snohomish Hilltop Observatory\n")
    file.write("910   6.9267 0.72368 +0.68811 Caussols-ODAS\n")
    file.write(
        "911 282.9233 0.7429  +0.6672  Collins Observatory, Corning Community College\n"
    )
    file.write("912 288.2342 0.74769 +0.66186 Carbuncle Hill Observatory, Greene\n")
    file.write("913 303.8161 0.82093 -0.56912 Observatorio Kappa Crucis, Montevideo\n")
    file.write("914 288.0108 0.73809 +0.67254 Underwood Observatory, Hubbardston\n")
    file.write("915 261.8789 0.86861 +0.49393 River Oaks Observatory, New Braunfels\n")
    file.write("916 272.6836 0.77287 +0.63248 Oakley Observatory, Terre Haute\n")
    file.write(
        "917 237.5522 0.68140 +0.72948 Pacific Lutheran University Keck Observatory\n"
    )
    file.write("918 257.8694 0.72071 +0.69110 Badlands Observatory, Quinn\n")
    file.write("919 248.3183 0.8419  +0.5379  Desert Beaver Observatory\n")
    file.write("920 282.3353 0.73161 +0.67947 RIT Observatory, Rochester\n")
    file.write(
        "921 254.4725 0.83988 +0.54159 SW Institute for Space Research, Cloudcroft\n"
    )
    file.write("922 272.8333 0.82335 +0.56569 Timberland Observatory, Decatur\n")
    file.write("923 284.6300 0.76655 +0.64006 The Bradstreet Observatory, St. Davids\n")
    file.write(
        "924 287.6769 0.68988 +0.72150 Observatoire du Cegep de Trois-Rivieres\n"
    )
    file.write("925 249.8589 0.85450 +0.51811 Palominas Observatory\n")
    file.write("926 249.1209 0.85394 +0.51902 Tenagra II Observatory, Nogales\n")
    file.write("927 270.561940.735007+0.675850Madison-YRS\n")
    file.write("928 286.6761 0.75688 +0.65136 Moonedge Observatory, Northport\n")
    file.write("929 268.7758 0.86319 +0.50319 Port Allen\n")
    file.write("930 210.412240.953752-0.299638S. S. Observatory, Pamatai\n")
    file.write("931 210.3842 0.95330 -0.30100 Puna'auia\n")
    file.write("932 286.573940.749771+0.659497John J. McCarthy Obs., New Milford\n")
    file.write("933 249.7342 0.85383 +0.51924 Rockland Observatory, Sierra Vista\n")
    file.write("934 242.9572 0.83985 +0.54108 Poway Valley\n")
    file.write("935 282.3394 0.77977 +0.62400 Wyrick Observatory, Haymarket\n")
    file.write("936 263.3792 0.77614 +0.62852 Ibis Observatory, Manhattan\n")
    file.write("937 358.6900 0.58065 +0.81143 Bradbury Observatory, Stockton-on-Tees\n")
    file.write("938 351.6162 0.77243 +0.63299 Linhaceira\n")
    file.write("939 359.6033 0.76982 +0.63619 Observatorio Rodeno\n")
    file.write("940 358.9611 0.63199 +0.77238 Waterlooville\n")
    file.write("941 359.6139 0.76988 +0.63608 Observatorio Pla D'Arguines\n")
    file.write("942 359.3636 0.60413 +0.79423 Grantham\n")
    file.write("943 355.8664 0.63881 +0.76679 Peverell\n")
    file.write("944 354.083150.796657+0.602418Observatorio Geminis, Dos Hermanas\n")
    file.write("945 354.3986 0.72671 +0.68474 Observatorio Monte Deva\n")
    file.write("946   0.7931 0.75662 +0.65170 Ametlla de Mar\n")
    file.write("947   2.1244 0.65268 +0.75511 Saint-Sulpice\n")
    file.write("948   0.2189 0.61048 +0.78937 Pymoor\n")
    file.write("949 359.8169 0.67454 +0.73577 Durtal\n")
    file.write("950 342.1176 0.87764 +0.47847 La Palma\n")
    file.write("951 358.2983 0.62194 +0.78046 Highworth\n")
    file.write("952 359.7583 0.7787  +0.6253  Marxuquera\n")
    file.write("953   2.1339 0.74602 +0.66393 Montjoia\n")
    file.write("954 343.4906 0.88148 +0.47142 Teide Observatory\n")
    file.write("955 350.6739 0.78146 +0.62188 Sassoeiros\n")
    file.write("956 356.1908 0.76224 +0.64530 Observatorio Pozuelo\n")
    file.write("957 359.3506 0.71047 +0.70137 Merignac\n")
    file.write("958 358.969610.724206+0.687273Observatoire de Dax\n")
    file.write("959   1.4653 0.72596 +0.68548 Ramonville Saint Agne\n")
    file.write("960   0.6108 0.63016 +0.77387 Rolvenden\n")
    file.write(
        "961 356.8206 0.56112 +0.82498 City Observatory, Calton Hill, Edinburgh\n"
    )
    file.write("962 359.8188 0.77845 +0.62561 Gandia\n")
    file.write("963 359.7333 0.6084  +0.7909  Werrington\n")
    file.write("964 358.8433 0.62471 +0.77826 Southend Bradfield\n")
    file.write(
        "965 351.4008 0.79761 +0.60118 Observacao Astronomica no Algarve, Portimao\n"
    )
    file.write("966 357.204230.609591+0.790100Church Stretton\n")
    file.write("967 358.9778 0.61508 +0.78585 Greens Norton\n")
    file.write("968   0.4250 0.6158  +0.7853  Haverhill\n")
    file.write("969 359.8454 0.6235  +0.7792  London-Regents Park\n")
    file.write("970   0.4954 0.62045 +0.78162 Chelmsford\n")
    file.write("971 350.812490.781336+0.622040Lisbon\n")
    file.write("972 357.5833 0.54359 +0.83656 Dun Echt\n")
    file.write("973 359.6671 0.62271 +0.77983 Harrow\n")
    file.write("974   8.9220 0.71542 +0.69637 Genoa\n")
    file.write("975 359.6333 0.77292 +0.63239 Observatorio Astronomico de Valencia\n")
    file.write("976 358.4669 0.61258 +0.78778 Leamington Spa\n")
    file.write("977 351.5483 0.58660 +0.80717 Markree\n")
    file.write("978 357.245410.588685+0.805673Conder Brow\n")
    file.write("979 358.6697 0.62896 +0.77485 South Wonston\n")
    file.write("980 357.2200 0.58864 +0.80570 Lancaster\n")
    file.write("981 353.3522 0.58409 +0.80898 Armagh\n")
    file.write("982 353.6621 0.59771 +0.79904 Dunsink Observatory, Dublin\n")
    file.write("983 353.795250.805167+0.591067San Fernando\n")
    file.write("984 357.269750.631671+0.772658Eastfield\n")
    file.write("985 357.5317 0.60801 +0.79130 Telford\n")
    file.write("986 359.360530.625049+0.777992Ascot\n")
    file.write("987 355.3735 0.58658 +0.80721 Isle of Man Observatory, Foxdale\n")
    file.write("988 355.7060 0.56225 +0.82421 Glasgow\n")
    file.write("989 357.405820.591888+0.803341Wilfred Hall Observatory, Preston\n")
    file.write("990 356.3121 0.76260 +0.64487 Madrid\n")
    file.write("991 356.9278 0.59750 +0.79919 Liverpool (since 1867)\n")
    file.write("992 356.9995 0.5973  +0.7993  Liverpool (before 1867)\n")
    file.write("993 357.495560.629975+0.774031Woolston Observatory\n")
    file.write("994 359.3878 0.62827 +0.77540 Godalming\n")
    file.write("995 358.4177 0.57819 +0.81319 Durham\n")
    file.write("996 358.7483 0.62025 +0.78179 Oxford\n")
    file.write("997 359.15   0.619   +0.783   Hartwell\n")
    file.write("998 359.757530.622254+0.780206London-Mill Hill\n")
    file.write("999 359.4725 0.71033 +0.70153 Bordeaux-Floirac\n")
    file.write("A00   0.3770 0.62475 +0.77821 Gravesend\n")
    file.write("A01   0.7441 0.74414 +0.66596 Masia Cal Maciarol Modul 2\n")
    file.write("A02   0.7441 0.74414 +0.66596 Masia Cal Maciarol Modul 8\n")
    file.write("A03   1.4000 0.7541  +0.6546  Torredembarra\n")
    file.write("A04   1.7181 0.72206 +0.68956 Saint-Caprais\n")
    file.write("A05   1.8175 0.72721 +0.68417 Belesta\n")
    file.write("A06   2.4417 0.74922 +0.66012 Mataro\n")
    file.write("A07   2.7444 0.66070 +0.74815 Gretz-Armainvilliers\n")
    file.write("A08   2.8847 0.72735 +0.68406 Malibert\n")
    file.write("A09   1.1803 0.65037 +0.75711 Quincampoix\n")
    file.write("A10   1.9281 0.75278 +0.65613 Observatorio Astronomico de Corbera\n")
    file.write("A11   2.4718 0.63222 +0.77219 Wormhout\n")
    file.write("A12   8.747680.703404+0.708434Stazione Astronomica di Sozzago\n")
    file.write("A13   7.1394 0.68632 +0.72501 Observatoire Naef, Ependes\n")
    file.write("A14   5.1864 0.72028 +0.69143 Les Engarouines Observatory\n")
    file.write("A15   6.7972 0.61903 +0.78275 Josef Bresser Sternwarte, Borken\n")
    file.write("A16   7.1922 0.68622 +0.72511 Tentlingen\n")
    file.write("A17   8.681520.650125+0.757317Guidestar Observatory, Weinheim\n")
    file.write("A18   7.1761 0.62342 +0.77928 Herne\n")
    file.write("A19   7.0744 0.63164 +0.77267 Koln\n")
    file.write("A20   7.518870.605274+0.793357Sogel\n")
    file.write("A21   8.0581 0.63667 +0.76862 Irmtraut\n")
    file.write("A22   8.6531 0.64877 +0.75848 Starkenburg Sternwarte-SOHAS\n")
    file.write("A23   8.6677 0.65027 +0.75719 Weinheim\n")
    file.write("A24   8.9481 0.69995 +0.71185 New Millennium Observatory, Mozzate\n")
    file.write("A25   9.1925 0.70104 +0.71077 Nova Milanese\n")
    file.write("A26   8.657360.646597+0.760303Darmstadt\n")
    file.write("A27  10.3236 0.61823 +0.78341 Eridanus Observatory, Langelsheim\n")
    file.write("A28  10.3342 0.67398 +0.73642 Kempten\n")
    file.write("A29  10.6733 0.72369 +0.68782 Santa Maria a Monte\n")
    file.write("A30  11.223080.700397+0.711555Crespadoro\n")
    file.write("A31  11.4186 0.70024 +0.71155 Corcaroli Observatory\n")
    file.write("A32  10.5517 0.58423 +0.80887 Panker\n")
    file.write("A33  11.0157 0.63231 +0.77217 Volkssternwarte Kirchheim\n")
    file.write("A34  10.7911 0.64944 +0.75793 Grosshabersdorf\n")
    file.write("A35  12.8978 0.63511 +0.76995 Hormersdorf Observatory\n")
    file.write("A36   9.7911 0.69856 +0.71340 Ganda di Aviatico\n")
    file.write("A37  13.6634 0.61128 +0.78877 Mueggelheim\n")
    file.write(
        "A38  13.3747 0.74706 +0.66266 Campocatino Automated Telescope, Collepardo\n"
    )
    file.write("A39  12.4186 0.63084 +0.77336 Altenburg\n")
    file.write("A40  14.4978 0.81104 +0.58306 Pieta\n")
    file.write("A41  14.5911 0.69290 +0.71871 Rezman Observatory, Kamnik\n")
    file.write("A42   9.5019 0.61280 +0.78760 Gehrden\n")
    file.write(
        "A43  13.0897 0.61201 +0.78821 Inastars Observatory, Potsdam (before 2006)\n"
    )
    file.write("A44  13.6972 0.66609 +0.74346 Altschwendt\n")
    file.write("A45   9.3620 0.62525 +0.77786 Karrenkneul\n")
    file.write("A46  16.5825 0.65349 +0.75447 Lelekovice\n")
    file.write("A47  16.6031 0.75962 +0.64829 Matera\n")
    file.write("A48  10.8885 0.70401 +0.70782 Povegliano Veronese\n")
    file.write("A49  17.6372 0.50372 +0.86098 Uppsala-Angstrom\n")
    file.write("A50  28.9973 0.64407 +0.76245 Andrushivka Astronomical Observatory\n")
    file.write("A51  18.6667 0.5837  +0.8093  Danzig\n")
    file.write("A52  18.7553 0.67756 +0.73304 Etyek\n")
    file.write("A53  10.6883 0.70294 +0.70889 Peschiera del Garda\n")
    file.write("A54  16.6217 0.60828 +0.79108 Ostrorog\n")
    file.write(
        "A55  13.1181 0.73871 +0.67204 Osservatorio Astronomico Vallemare di Borbona\n"
    )
    file.write("A56  10.3197 0.71406 +0.69784 Parma\n")
    file.write(
        "A57  11.1031 0.72364 +0.68791 Osservatorio Astron. Margherita Hack, Firenze\n"
    )
    file.write("A58   2.4694 0.66135 +0.74758 Observatoire de Chalandray-Canotiers\n")
    file.write("A59  12.9071 0.64123 +0.76490 Karlovy Vary Observatory\n")
    file.write("A60  20.8106 0.84556 -0.53260 YSTAR-NEOPAT Station, Sutherland\n")
    file.write("A61   8.8581 0.70949 +0.70238 Tortona\n")
    file.write("A62   9.2301 0.66233 +0.74678 Aichtal\n")
    file.write("A63   4.7567 0.69879 +0.71298 Cosmosoz Obs., Tassin la Demi Lune\n")
    file.write("A64   6.1151 0.69034 +0.72132 Couvaloup de St-Cergue\n")
    file.write("A65   2.4083 0.71939 +0.69239 Le Couvent de Lentin\n")
    file.write(
        "A66  10.3161 0.72613 +0.68526 Stazione Osservativa Astronomica, Livorno\n"
    )
    file.write("A67   7.6785 0.71665 +0.69522 Chiusa di Pesio\n")
    file.write("A68   9.6533 0.57755 +0.81362 Swedenborg Obs., Bockholmwik\n")
    file.write("A69  11.3300 0.7287  +0.6826  Osservatorio Palazzo Bindi Sergardi\n")
    file.write("A70  25.2033 0.42654 +0.90144 Lumijoki\n")
    file.write("A71  15.4533 0.66486 +0.74459 Stixendorf\n")
    file.write("A72  13.6222 0.62904 +0.77481 Radebeul Observatory\n")
    file.write("A73  16.2895 0.66788 +0.74183 Penzing Astrometric Obs., Vienna\n")
    file.write("A74   8.762400.641951+0.764216Bergen-Enkheim Observatory\n")
    file.write("A75   2.1861 0.75124 +0.65783 Fort Pius Observatory, Barcelona\n")
    file.write("A76  20.8356 0.66948 +0.74037 Andromeda Observatory, Miskolc\n")
    file.write("A77   5.646930.720583+0.691196Observatoire Chante-Perdrix, Dauban\n")
    file.write("A78  11.715090.730944+0.680264Stia\n")
    file.write("A79  23.843400.743686+0.666622Zvezdno Obshtestvo Observatory, Plana\n")
    file.write("A80  14.1222 0.61408 +0.78662 Lindenberg Observatory\n")
    file.write("A81  12.4033 0.74578 +0.66397 Balzaretto Observatory, Rome\n")
    file.write("A82  13.8744 0.70037 +0.71148 Osservatorio Astronomico di Trieste\n")
    file.write("A83  29.9969 0.45945 +0.88525 Jakokoski Observatory\n")
    file.write("A84  30.3333 0.80175 +0.59632 TUBITAK National Observatory\n")
    file.write(
        "A85  30.8065 0.68881 +0.72252 Odesa  Astronomical Observatory, Kryzhanovka\n"
    )
    file.write("A86   4.3547 0.70170 +0.71021 Albigneux\n")
    file.write("A87   8.7662 0.64935 +0.75798 Rimbach\n")
    file.write("A88   8.901330.714961+0.696835Bolzaneto\n")
    file.write("A89  10.3308 0.67421 +0.73621 Sterni Observatory, Kempten\n")
    file.write("A90   2.1431 0.75120 +0.65788 Sant Gervasi Observatory, Barcelona\n")
    file.write("A91  26.5997 0.46678 +0.88143 Hankasalmi Observatory\n")
    file.write("A92  26.0927 0.71506 +0.69673 Urseanu Observatory, Bucharest\n")
    file.write("A93  10.4189 0.72222 +0.68935 Lucca\n")
    file.write("A94  13.4577 0.69641 +0.71526 Cormons\n")
    file.write("A95  28.3892 0.46584 +0.88193 Taurus Hill Observatory, Varkaus\n")
    file.write("A96  16.2867 0.66656 +0.74303 Klosterneuburg\n")
    file.write("A97  16.4219 0.66646 +0.74308 Stammersdorf\n")
    file.write("A98  30.2092 0.58214 +0.81040 Observatory Mazzarot-1, Baran'\n")
    file.write("A99  10.8589 0.69978 +0.71223 Osservatorio del Monte Baldo\n")
    file.write("B00   2.5767 0.66289 +0.74622 Savigny-le-Temple\n")
    file.write("B01   8.4464 0.64117 +0.76499 Taunus Observatory, Frankfurt\n")
    file.write("B02  20.6566 0.63224 +0.77224 Kielce\n")
    file.write("B03  16.2698 0.66759 +0.74211 Alter Satzberg, Vienna\n")
    file.write("B04   7.478510.698677+0.713400OAVdA, Saint-Barthelemy\n")
    file.write("B05  37.8831 0.57134 +0.81800 Ka-Dar Observatory, Barybino\n")
    file.write("B06   2.533720.747520+0.662058Montseny Astronomical Observatory\n")
    file.write("B07   9.0033 0.69383 +0.71778 Camorino\n")
    file.write("B08  11.3807 0.71498 +0.69683 San Lazzaro di Savena\n")
    file.write("B09  10.6708 0.72550 +0.68593 Capannoli\n")
    file.write(
        "B10   5.5150 0.71564 +0.69631 Observatoire des Baronnies Provencales, Moydans\n"
    )
    file.write("B11  10.6286 0.69881 +0.71318 Osservatorio Cima Rest, Magasa\n")
    file.write("B12   4.4906 0.61329 +0.78721 Koschny Observatory, Noordwijkerhout\n")
    file.write("B13   8.9311 0.69950 +0.71231 Osservatorio di Tradate\n")
    file.write("B14   9.0758 0.71061 +0.70138 Ca del Monte\n")
    file.write(
        "B15  13.0129 0.61111 +0.78890 Inastars Observatory, Potsdam (since 2006)\n"
    )
    file.write(
        "B16  36.9547 0.56382 +0.82317 1st Moscow Gymnasium Observatory, Lipki\n"
    )
    file.write("B17  33.162800.705588+0.706256AZT-8 Yevpatoriya\n")
    file.write("B18  42.5008 0.72958 +0.68232 Terskol\n")
    file.write("B19   2.4414 0.74963 +0.65966 Observatorio Iluro, Mataro\n")
    file.write("B20   2.2636 0.75026 +0.65897 Observatorio Carmelita, Tiana\n")
    file.write("B21  13.4744 0.66335 +0.74589 Gaisberg Observatory, Schaerding\n")
    file.write("B22   0.7441 0.74412 +0.66598 Observatorio d'Ager\n")
    file.write("B23  10.9710 0.70124 +0.71069 Fiamene\n")
    file.write("B24   2.5983 0.66317 +0.74598 Cesson\n")
    file.write("B25  15.0557 0.79386 +0.60614 Catania\n")
    file.write(
        "B26   5.6667 0.72204 +0.68966 Observatoire des Terres Blanches, Reillanne\n"
    )
    file.write("B27  14.1544 0.66425 +0.74516 Picard Observatory, St. Veit\n")
    file.write("B28  13.1836 0.69466 +0.71696 Mandi Observatory, Pagnacco\n")
    file.write("B29   0.6701 0.75801 +0.65008 L'Ampolla Observatory, Tarragona\n")
    file.write("B30  16.5689 0.60872 +0.79074 Szamotuly-Galowo\n")
    file.write(
        "B31  20.8108 0.84560 -0.53254 Southern African Large Telescope, Sutherland\n"
    )
    file.write("B32  12.9486 0.63467 +0.77030 Gelenau\n")
    file.write("B33  10.7783 0.72588 +0.68555 Libbiano Observatory, Peccioli\n")
    file.write("B34  33.7258 0.81748 +0.57405 Green Island Observatory, Gecitkale\n")
    file.write("B35  35.0317 0.84991 +0.52524 Bareket Observatory, Macabim\n")
    file.write("B36  13.7125 0.66684 +0.74278 Redshed Observatory, Kallham\n")
    file.write(
        "B37   2.259340.748338+0.661147Obs. de L' Ametlla del Valles, Barcelona\n"
    )
    file.write("B38  11.857460.724995+0.686523Santa Mama\n")
    file.write("B39   8.9072 0.69950 +0.71231 Tradate\n")
    file.write("B40  15.0706 0.79331 +0.60690 Skylive Observatory, Catania\n")
    file.write("B41  17.6925 0.65449 +0.75362 Zlin Observatory\n")
    file.write("B42  30.3275 0.57401 +0.81614 Vitebsk\n")
    file.write("B43   7.3089 0.63404 +0.77073 Hennef\n")
    file.write("B44   5.5906 0.71772 +0.69419 Eygalayes\n")
    file.write("B45  19.9356 0.64169 +0.76447 Narama\n")
    file.write("B46  12.054390.714373+0.697420Sintini Observatory, Alfonsine\n")
    file.write("B47  24.7503 0.49826 +0.86413 Metsala Observatory, Espoo\n")
    file.write("B48   6.5981 0.61901 +0.78275 Bocholt\n")
    file.write("B49   2.112500.749498+0.659844Paus Observatory, Sabadell\n")
    file.write("B50   8.2767 0.65808 +0.75045 Corner Observatory, Durmersheim\n")
    file.write("B51   7.066690.725612+0.685830Vallauris\n")
    file.write("B52   2.997250.741344+0.668883Observatorio El Far\n")
    file.write("B53  12.3536 0.74572 +0.66404 Casal Lumbroso, Rome\n")
    file.write("B54   0.7439 0.74413 +0.66597 Ager\n")
    file.write("B55  12.876000.689553+0.721975Comeglians\n")
    file.write("B56   2.449350.749614+0.659663Observatorio Sant Pere, Mataro\n")
    file.write(
        "B57   2.224390.749316+0.660019Laietania Observatory, Parets del Valles\n"
    )
    file.write("B58  19.025290.676156+0.734318Polaris Observatory, Budapest\n")
    file.write("B59   6.878810.619231+0.782586Borken\n")
    file.write("B60   7.175310.612824+0.787576Deep Sky Observatorium, Bad Bentheim\n")
    file.write("B61   2.043500.750575+0.658604Valldoreix Obs.,Sant Cugat del Valles\n")
    file.write("B62   9.685310.609275+0.790314Brelingen\n")
    file.write("B63  20.107990.642589+0.763698Solaris Observatory, Luczanowice\n")
    file.write("B64  24.887790.491587+0.867927Slope Rock Observatory, Hyvinkaa\n")
    file.write("B65  24.3878 0.49864 +0.86391 Komakallio Observatory, Kirkkonummi\n")
    file.write("B66   9.006930.710595+0.701332Osservatorio di Casasco\n")
    file.write("B67   9.224190.685858+0.725582Sternwarte Mirasteilas, Falera\n")
    file.write("B68  13.539500.693458+0.718372Mount Matajur Observatory\n")
    file.write(
        "B69   9.017190.662152+0.746956Owls and Ravens Observatory, Holzgerlingen\n"
    )
    file.write("B70   2.4937 0.74787 +0.66165 Sant Celoni\n")
    file.write("B71   1.5213 0.75363 +0.65510 Observatorio El Vendrell\n")
    file.write("B72   7.6811 0.63470 +0.77022 Soerth\n")
    file.write(
        "B73   8.985030.662074+0.747029Mauren Valley Observatory, Holzgerlingen\n"
    )
    file.write("B74   1.105360.747550+0.662053Santa Maria de Montmagastrell\n")
    file.write(
        "B75   8.805190.701074+0.710741Stazione Astronomica Betelgeuse, Magnago\n"
    )
    file.write("B76  13.8944 0.63019 +0.77390 Sternwarte Schonfeld, Dresden\n")
    file.write("B77   7.950830.677934+0.732833Schafmatt Observatory, Aarau\n")
    file.write("B78  14.128110.670885+0.739158Astrophoton Observatory, Audorf\n")
    file.write("B79  11.209900.700480+0.711457Marana Observatory\n")
    file.write("B80  12.741260.742254+0.667919Osservatorio Astronomico Campomaggiore\n")
    file.write("B81   2.8990 0.76967 +0.63634 Caimari\n")
    file.write("B82   9.9716 0.64613 +0.76072 Maidbronn\n")
    file.write("B83   5.797690.706034+0.705851Gieres\n")
    file.write("B84   3.537750.622812+0.779749Cyclops Observatory, Oostkapelle\n")
    file.write("B85   6.510110.604962+0.793587Beilen Observatory\n")
    file.write("B86   7.455610.625931+0.777324Sternwarte Hagen\n")
    file.write("B87   2.7701 0.74295 +0.66715 Banyoles\n")
    file.write("B88   8.296810.710570+0.701309Bigmuskie Observatory, Mombercelli\n")
    file.write("B89   2.2619 0.75018 +0.65907 Observatori Astronomic de Tiana\n")
    file.write("B90  13.296860.693994+0.717600Malina River Observatory, Povoletto\n")
    file.write("B91   7.255440.672149+0.737995Bollwiller\n")
    file.write("B92   0.275390.681073+0.729781Chinon\n")
    file.write("B93   6.478560.607102+0.791962Hoogeveen\n")
    file.write("B94  34.2817 0.47422 +0.87748 Petrozavodsk\n")
    file.write("B95   8.154500.602437+0.795492Achternholt\n")
    file.write("B96   4.310310.628378+0.775301Brixiis Observatory, Kruibeke\n")
    file.write("B97   6.1118 0.61688 +0.78442 Sterrenwacht Andromeda, Meppel\n")
    file.write("B98  11.313000.728746+0.682563Siena\n")
    file.write("B99   0.7443 0.74413 +0.66598 Santa Coloma de Gramenet\n")
    file.write("C00  30.5150 0.55583 +0.82853 Velikie Luki\n")
    file.write("C01  13.922930.630265+0.773855Lohrmann-Observatorium, Triebenberg\n")
    file.write("C02   2.5305 0.74740 +0.66218 Observatorio Royal Park\n")
    file.write("C03  24.961140.492892+0.867190Clayhole Observatory, Jokela\n")
    file.write("C04  37.6331 0.65998 +0.74878 Kramatorsk\n")
    file.write("C05  12.1153 0.68023 +0.73088 Konigsleiten\n")
    file.write("C06  92.9744 0.56032 +0.82553 Krasnoyarsk\n")
    file.write("C07   0.7442 0.74413 +0.66597 Anysllum Observatory, Ager\n")
    file.write("C08  17.3761 0.50302 +0.86138 Fiby\n")
    file.write("C09   3.803970.722660+0.688932Rouet\n")
    file.write("C10   3.426220.661039+0.747874Maisoncelles\n")
    file.write("C11  14.0901 0.64091 +0.76509 City Observatory, Slany\n")
    file.write("C12   2.1107 0.74967 +0.65964 Berta Observatory, Sabadell\n")
    file.write("C13   9.100310.698332+0.713430Como\n")
    file.write("C14  15.967000.668463+0.741344Sky Vistas Observatory, Eichgraben\n")
    file.write("C15 132.1656 0.72418 +0.68737 ISON-Ussuriysk Observatory\n")
    file.write("C16  11.572610.673687+0.736691Isarwinkel Observatory, Bad Tolz\n")
    file.write("C17   0.743810.744124+0.665978Observatorio Joan Roget, Ager\n")
    file.write("C18   3.604000.634888+0.770037Frasnes-Lez-Anvaing\n")
    file.write("C19   5.4231 0.71591 +0.69599 ROSA Observatory, Vaucluse\n")
    file.write(
        "C20  42.661910.723859+0.688104Kislovodsk Mtn. Astronomical Stn., Pulkovo Obs.\n"
    )
    file.write("C21   0.743830.744124+0.665978Observatorio Via Lactea, Ager\n")
    file.write("C22  12.9599 0.63858 +0.76717 Oberwiesenthal\n")
    file.write("C23   5.154390.628694+0.775052Olmen\n")
    file.write("C24   9.1331 0.70036 +0.71145 Seveso\n")
    file.write(
        "C25  13.558060.739310+0.671605Pulkovo Observatory Station, Campo Imperatore\n"
    )
    file.write("C26   4.499280.614813+0.786032Levendaal Observatory, Leiden\n")
    file.write("C27   1.353020.748763+0.660753Pallerols\n")
    file.write("C28   7.483000.624224+0.778652Wellinghofen\n")
    file.write(
        "C29   1.078890.737202+0.673777Observatori Astronomic de Les Planes de Son\n"
    )
    file.write(
        "C30  35.3425 0.47988 +0.87440 Petrozavodsk University Obs., Sheltozero Stn.\n"
    )
    file.write(
        "C31   6.9825 0.62777 +0.77581 Sternwarte Neanderhoehe Hochdahl e.V., Erkrath\n"
    )
    file.write(
        "C32  41.4258 0.72496 +0.68694 Ka-Dar Observatory, TAU Station, Nizhny Arkhyz\n"
    )
    file.write("C33   2.8989 0.76967 +0.63634 Observatorio CEAM, Caimari\n")
    file.write("C34  19.0108 0.69361 +0.71796 Baja Astronomical Observatory\n")
    file.write("C35   2.0349 0.74927 +0.66012 Terrassa\n")
    file.write("C36  30.3086 0.58230 +0.81028 Starry Wanderer Observatory, Baran'\n")
    file.write("C37   1.018300.614242+0.786484Stowupland\n")
    file.write("C38   7.649110.703322+0.708581Varuna Observatory, Cuorgne\n")
    file.write("C39   5.7992 0.61929 +0.78253 Nijmegen\n")
    file.write(
        "C40  39.0308 0.70806 +0.70380 Kuban State University Astrophysical Observatory\n"
    )
    file.write("C41  42.661260.723857+0.688105MASTER-II Observatory, Kislovodsk\n")
    file.write("C42  87.1778 0.72711 +0.68469 Xingming Observatory, Mt. Nanshan\n")
    file.write("C43  14.2792 0.62451 +0.77842 Hoyerswerda\n")
    file.write("C44   9.022390.696268+0.715567A. Volta Observatory, Lanzo d'Intelvi\n")
    file.write("C45  12.406390.744413+0.665514La Giustiniana\n")
    file.write("C46  69.122190.576620+0.814296Horizon Observatory, Petropavlovsk\n")
    file.write("C47  15.2356 0.66017 +0.74871 Nonndorf\n")
    file.write("C48 100.9214 0.62235 +0.78051 Sayan Solar Observatory, Irkutsk\n")
    file.write("C49                           STEREO-A\n")
    file.write("C50                           STEREO-B\n")
    file.write("C51                           WISE\n")
    file.write("C52                           Swift\n")
    file.write("C53                           NEOSSat\n")
    file.write("C54                           New Horizons\n")
    file.write("C55                           Kepler\n")
    file.write("C56                           LISA-Pathfinder\n")
    file.write("C57                           TESS\n")
    file.write("C59                           Yangwang-1\n")
    file.write(
        "C60   7.069260.634261+0.770545Argelander Institute for Astronomy Obs., Bonn\n"
    )
    file.write("C61   2.582020.658892+0.749723Chelles\n")
    file.write("C62  11.3467 0.68967 +0.72175 Eurac Observatory, Bolzano\n")
    file.write(
        "C63   9.9797 0.69363 +0.71819 Giuseppe Piazzi Observatory, Ponte in Valtellina\n"
    )
    file.write("C64  15.284390.671380+0.738819Puchenstuben\n")
    file.write("C65   0.729650.743841+0.666482Observatori Astronomic del Montsec\n")
    file.write("C66   2.8050 0.77084 +0.63493 Observatorio El Cielo de Consell\n")
    file.write("C67  12.2199 0.59747 +0.79922 Gnevsdorf\n")
    file.write(
        "C68  23.893390.789058+0.612302Ellinogermaniki Agogi Observatory, Pallini\n"
    )
    file.write("C69  13.3611 0.65835 +0.75036 Bayerwald Sternwarte, Neuhuette\n")
    file.write("C70   4.497750.614779+0.786055Uiterstegracht Station, Leiden\n")
    file.write("C71   1.4892 0.74780 +0.66186 Sant Marti Sesgueioles\n")
    file.write("C72  12.8717 0.74621 +0.66358 Palestrina\n")
    file.write("C73  28.0325 0.70312 +0.70870 Galati Observatory\n")
    file.write(
        "C74   0.7449 0.74412 +0.66598 Observatorio El Teatrillo de Lyra, Ager\n"
    )
    file.write("C75  13.2225 0.69384 +0.71776 Whitestar Observatory, Borgobello\n")
    file.write("C76   0.744310.744127+0.665974Observatorio Estels, Ager\n")
    file.write("C77   7.4535 0.71589 +0.69600 Bernezzo Observatory\n")
    file.write("C78  34.812420.849698+0.525519Martin S. Kraar Observatory, Rehovot\n")
    file.write("C79   2.7855 0.74801 +0.66147 Roser Observatory, Blanes\n")
    file.write(
        "C80  39.7651 0.67959 +0.73115 Don Astronomical Observatory, Rostov-on-Don\n"
    )
    file.write("C81  10.840980.693023+0.718872Dolomites Astronomical Observatory\n")
    file.write(
        "C82  14.357630.760171+0.647611Osservatorio Astronomico Nastro Verde, Sorrento\n"
    )
    file.write("C83  91.8425 0.55930 +0.82626 Badalozhnyj Observatory\n")
    file.write("C84   2.243720.750690+0.658447Badalona\n")
    file.write("C85   1.2408 0.77939 +0.62448 Observatorio Cala d'Hort, Ibiza\n")
    file.write("C86   2.7813 0.74801 +0.66147 Blanes\n")
    file.write("C87   8.7689 0.64913 +0.75817 Rimbach\n")
    file.write("C88  11.183310.729763+0.681487Montarrenti Observatory, Siena\n")
    file.write("C89  21.555580.730958+0.680397Astronomical Station Vidojevica\n")
    file.write("C90   1.051810.754546+0.654066Vinyols\n")
    file.write("C91  11.226210.717604+0.694214Montevenere Observatory, Monzuno\n")
    file.write("C92  13.609950.727425+0.683915Valdicerro Observatory, Loreto\n")
    file.write("C93  13.4064 0.74042 +0.67004 Bellavista Observatory, L'Aquila\n")
    file.write("C94 103.0670 0.61962 +0.78241 MASTER-II Observatory, Tunka\n")
    file.write(
        "C95   5.712390.721401+0.690345SATINO Remote Observatory, Haute Provence\n"
    )
    file.write("C96  13.8786 0.73544 +0.67537 OACL Observatory, Mosciano Sant Angelo\n")
    file.write("C97  57.976330.916656+0.398354Al-Fulaij Observatory, Oman\n")
    file.write("C98  11.1764 0.72335 +0.68818 Osservatorio Casellina, Scandicci\n")
    file.write("C99   2.896310.746295+0.663419Observatori Can Roig, Llagostera\n")
    file.write("D00  42.6536 0.72388 +0.68809 ASC-Kislovodsk Observatory\n")
    file.write(
        "D01  23.930610.495920+0.865471Andean Northern Observatory, Nummi-Pusula\n"
    )
    file.write("D02   2.051890.751414+0.657647Observatori Petit Sant Feliu\n")
    file.write("D03  10.5889 0.71522 +0.69670 Rantiga Osservatorio, Tincana\n")
    file.write("D04  38.8569 0.70960 +0.70225 Krasnodar\n")
    file.write("D05  42.500050.729580+0.682314ISON-Terskol Observatory\n")
    file.write(
        "D06  12.770170.747232+0.662472Associazione Tuscolana di Astronomia, Domatore\n"
    )
    file.write("D07   6.2094 0.62867 +0.77508 Wegberg\n")
    file.write("D08   8.9191 0.69024 +0.72136 Ghezz Observatory, Leontica\n")
    file.write("D09   5.6794 0.63139 +0.77287 Observatory Gromme, Maasmechelen\n")
    file.write("D10   8.901810.661976+0.747123Gaertringen\n")
    file.write("D11   5.627970.723085+0.688551Bastidan Observatory\n")
    file.write("D12  11.338060.690580+0.720900Filzi School Observatory, Laives\n")
    file.write("D13  11.563690.738665+0.671859Cat's Eye Observatory\n")
    file.write("D14 113.3231 0.92000 +0.39061 Nanchuan Observatory, Guangzhou\n")
    file.write(
        "D15  11.317810.630848+0.773359Sternwarte F.Schiller-Gymnasium, Weimar\n"
    )
    file.write("D16 113.964220.925155+0.378330Po Leung Kuk Observatory, Tuen Mun\n")
    file.write("D17 114.2200 0.9245  +0.3799  Hong Kong\n")
    file.write("D18 114.3580 0.86219 +0.50490 Mt. Guizi Observatory\n")
    file.write(
        "D19 114.323000.924955+0.378843Hong Kong Space Museum Sai Kung iObservatory\n"
    )
    file.write("D20 115.713110.854733-0.517343Zadko Observatory, Wallingup Plain\n")
    file.write("D21 115.8150 0.8492  -0.5263  Shenton Park\n")
    file.write("D22 115.816670.849044-0.526558UWA Observatory, Crawley\n")
    file.write("D23   0.518530.749367+0.659977OAIA, Alcarras\n")
    file.write("D24 117.089690.844095-0.534439LightBuckets Observatory, Pingelly\n")
    file.write(
        "D25 117.089780.844104-0.534424Tzec Maun Observatory, Pingelly (before 2010)\n"
    )
    file.write("D26   1.921310.722868+0.688750Peyrole Observatory, Peyrole\n")
    file.write("D27   3.803610.725021+0.686446Observatoire de Fontcaude, Juvignac\n")
    file.write(
        "D28   2.182860.748708+0.660744Escaldarium Observatory,Caldes de Montbui\n"
    )
    file.write(
        "D29 118.4639 0.84204 +0.53767 Purple Mountain Observatory, XuYi Station\n"
    )
    file.write(
        "D32 119.599750.862770+0.504193JiangNanTianChi Observatory, Mt. Getianling\n"
    )
    file.write("D33 120.6982 0.92730 +0.37308 Kenting Observatory, Checheng\n")
    file.write("D34 120.7839 0.92796 +0.37148 Kenting Observatory, Hengchun\n")
    file.write("D35 120.8736 0.91818 +0.39597 Lulin Observatory\n")
    file.write("D36 120.8897 0.91801 +0.39625 Tataka, Mt. Yu-Shan National Park\n")
    file.write("D37 120.873250.918176+0.395972Lulin Widefield Telescope, Mt. Lulin\n")
    file.write("D38   8.437640.709383+0.702495Tecnosky Astropark, Felizzano\n")
    file.write(
        "D39 122.049610.793971+0.605943Shandong University Observatory, Weihai\n"
    )
    file.write("D44 124.139280.911427+0.410157Ishigakijima Astronomical Observatory\n")
    file.write("D53 127.4820 0.63981 +0.76600 ISON-Blagoveschensk Observatory\n")
    file.write("D54 127.4830 0.63981 +0.76601 MASTER-II Observatory, Blagoveshchensk\n")
    file.write(
        "D55 127.9747 0.79571 +0.60370 Kangwon Science High School Observatory, Ksho\n"
    )
    file.write(
        "D57 128.887440.817572+0.573996Gimhae Astronomical Observatory, Uhbang-dong\n"
    )
    file.write("D58 129.025000.818419+0.572736KSA SEM Observatory, Danggam-dong\n")
    file.write("D61 134.9131 0.82671 +0.56075 Suntopia Marina, Sumoto\n")
    file.write("D62 130.4494 0.83676 +0.54575 Miyaki-Argenteus\n")
    file.write("D67  37.624720.586136+0.807530Tula Rooftop Observatory, Tula\n")
    file.write("D70 133.4686 0.83505 +0.54834 Tosa\n")
    file.write("D74 134.6819 0.83041 +0.55530 Nakagawa\n")
    file.write("D78 136.132810.822378+0.567077Iga-Ueno\n")
    file.write("D79 138.630920.821212-0.568722YSVP Observatory, Vale Park\n")
    file.write("D80 138.9728 0.80392 +0.59297 Gumma Astronomical Observatory\n")
    file.write("D81 138.2239 0.80310 +0.59394 Nagano\n")
    file.write("D82 137.6317 0.83058 -0.55504 Wallaroo\n")
    file.write("D83 138.4681 0.80501 +0.59161 Miwa\n")
    file.write("D84 138.5086 0.8192  -0.5716  Hallet Cove\n")
    file.write("D85 138.6597 0.82186 -0.56782 Ingle Farm\n")
    file.write("D86 138.6407 0.83075 -0.55490 Penwortham\n")
    file.write("D87 138.5500 0.82079 -0.56931 Brooklyn Park\n")
    file.write("D88 139.3142 0.81635 +0.57562 Hiratsuka\n")
    file.write("D89 140.3383 0.7871  +0.6149  Yamagata\n")
    file.write("D90 140.3420 0.82728 -0.55991 RAS Observatory, Moorook\n")
    file.write("D91 140.8250 0.79261 +0.60775 Adati\n")
    file.write("D92 140.946380.782920+0.620047Osaki\n")
    file.write("D93 140.755160.786291+0.615826Sendai Astronomical Observatory\n")
    file.write("D94 139.9962 0.80351 +0.59335 Takanezawa, Tochigi\n")
    file.write("D95 141.0680 0.78035 +0.62325 Kurihara\n")
    file.write("D96 140.342160.827287-0.559905Tzec Maun Observatory, Moorook\n")
    file.write("D97 140.5700 0.82752 -0.55956 Berri\n")
    file.write("E00 144.2089 0.79902 -0.59937 Castlemaine\n")
    file.write("E01 144.541420.798618-0.599924Barfold\n")
    file.write("E03 145.3822 0.78756 -0.61419 RAS Observatory, Officer\n")
    file.write("E04 145.7403 0.96545 +0.25977 Pacific Sky Observatory, Saipan\n")
    file.write("E05 145.697210.957625-0.287092Earl Hill Observatory, Trinity Beach\n")
    file.write("E07 148.998890.820544-0.569830Murrumbateman\n")
    file.write("E08 149.334310.855971-0.515472Wobblesock Observatory, Coonabarabran\n")
    file.write(
        "E09 149.0814 0.85551 -0.51630 Oakley Southern Sky Observatory, Coonabarabran\n"
    )
    file.write("E10 149.070850.855632-0.516198Siding Spring-Faulkes Telescope South\n")
    file.write("E11 149.6627 0.84469 -0.53362 Frog Rock Observatory, Mudgee\n")
    file.write("E12 149.0642 0.85563 -0.51621 Siding Spring Survey\n")
    file.write("E13 149.0969 0.81622 -0.57597 Wanniassa\n")
    file.write("E14 149.1100 0.81852 -0.57274 Hunters Hill Observatory, Ngunnawal\n")
    file.write("E15 149.6061 0.82016 -0.57041 Magellan Observatory, near Goulburn\n")
    file.write("E16 149.366240.831684-0.553656Grove Creek Observatory, Trunkey\n")
    file.write("E17 150.3417 0.8329  -0.5519  Leura\n")
    file.write("E18 151.027140.829819-0.556191BDI Observatory, Regents Park\n")
    file.write("E19 151.0958 0.83042 -0.55528 Kingsgrove\n")
    file.write("E20 151.103200.832146-0.552728Marsfield\n")
    file.write("E21 151.5667 0.8838  -0.4665  Norma Rose Observatory, Leyburn\n")
    file.write(
        "E22 151.855000.885337-0.463616Univ. of Southern Queensland Obs., Mt. Kent\n"
    )
    file.write("E23 151.071190.833596-0.550574Arcadia\n")
    file.write("E24 150.7769 0.83176 -0.55329 Tangra Observatory, St. Clair\n")
    file.write("E25 153.1170 0.88713 -0.45997 Rochedale (APTA)\n")
    file.write("E26 153.3971 0.88414 -0.46566 RAS Observatory, Biggera Waters\n")
    file.write("E27 153.2667 0.8871  -0.4600  Thornlands\n")
    file.write("E28 150.641050.833196-0.551210Kuriwa Observatory, Hawkesbury Heights\n")
    file.write("E81 173.2617 0.75267 -0.65622 Nelson\n")
    file.write("E83 173.957030.749648-0.659621Wither Observatory, Witherlea\n")
    file.write("E85 174.894000.800696-0.597064Farm Cove\n")
    file.write("E87 175.6540 0.76249 -0.64485 Turitea\n")
    file.write("E89 176.2040 0.78759 -0.61421 Geyserland Observatory, Pukehangi\n")
    file.write("E94 177.883310.782217-0.620920Possum Observatory, Gisborne\n")
    file.write("F51 203.744090.936241+0.351543Pan-STARRS 1, Haleakala\n")
    file.write("F52 203.744090.936239+0.351545Pan-STARRS 2, Haleakala\n")
    file.write("F59 201.941000.932037+0.361160Ironwood Remote Observatory, Hawaii\n")
    file.write("F60 201.952830.929942+0.366558Ironwood Observatory, Hawaii\n")
    file.write("F65 203.742500.936239+0.351538Haleakala-Faulkes Telescope North\n")
    file.write("F84 210.3842 0.95330 -0.30100 Hibiscus Observatory, Punaauia\n")
    file.write("F85 210.3842 0.95330 -0.30100 Tiki Observatory, Punaauia\n")
    file.write("F86 210.383810.953304-0.301004Moana Observatory, Punaauia\n")
    file.write("G00  15.126000.665508+0.744080AZM Martinsberg, Oed\n")
    file.write("G01   8.165280.600977+0.796597Universitaetssternwarte Oldenburg\n")
    file.write("G02  18.765390.653307+0.754650KYSUCE Observatory, Kysucke Nove Mesto\n")
    file.write("G03  18.260610.678620+0.732104Capricornus Observatory, Csokako\n")
    file.write(
        "G04   7.141330.627502+0.776082Schuelerlabor Astronomie St. 7, Wuppertal\n"
    )
    file.write("G05 354.533630.787181+0.614802Piconcillo, Sierra Morena\n")
    file.write("G06   4.671500.619980+0.781996Dordrecht, Sterrenburg\n")
    file.write("G07   3.063860.719394+0.692378Millau Observatory\n")
    file.write("G08   1.996940.748752+0.660794Observatorio Les Pedritxes, Matadepera\n")
    file.write("G09   0.610560.621784+0.780574SWF Observatory, South Woodham Ferrers\n")
    file.write("G10 354.450550.792574+0.607765Clavier Observatory, Lora Del Rio\n")
    file.write("G11   7.183790.630712+0.773465Breitenweg Observatory, Herkenrath\n")
    file.write("G12   8.3306 0.62140 +0.78090 Sternwarte EG, Lippstadt\n")
    file.write("G13   9.771690.451874+0.889103Astronomihagen, Fannrem\n")
    file.write("G14   7.005200.725247+0.686239Novaloop Observatory, Mougins\n")
    file.write("G15   9.1183 0.71116 +0.70080 Magroforte Observatory, Alessandria\n")
    file.write("G16  13.348690.787948+0.613701OmegaLab Observatory, Palermo\n")
    file.write("G17  11.202610.723508+0.688023BAS Observatory, Scandicci\n")
    file.write("G18  11.280560.712881+0.698947ALMO Observatory, Padulle\n")
    file.write("G19  12.7460 0.63252 +0.77202 Immanuel Kant Observatory,Limbach\n")
    file.write("G20   6.059890.727743+0.683615Brignoles Observatory\n")
    file.write("G21  13.737890.796024+0.603377Osservatorio Castrofilippo\n")
    file.write("G22   9.214390.655435+0.752770Experimenta Observatory, Heilbronn\n")
    file.write("G23  19.092340.675698+0.734739Vulpecula Observatory, Budapest\n")
    file.write("G24   9.093500.662443+0.746701Dettenhausen\n")
    file.write("G25 288.1050 0.70317 +0.70867 Sherbrooke\n")
    file.write("G26 109.8236 0.82499 +0.56338 Fushan Observatory, Mt Shaohua\n")
    file.write("G27   0.729350.743842+0.666483Fabra Observatory, Montsec\n")
    file.write("G28   1.008500.609900+0.789830Wyncroft Observatory, Attleborough\n")
    file.write("G29 358.9124 0.77285 +0.63263 Requena\n")
    file.write("G30 284.907190.704518+0.707320Casselman\n")
    file.write("G31  13.7253 0.69946 +0.71233 CCAT Trieste\n")
    file.write(
        "G32 291.820400.921639-0.387713Elena Remote Observatory, San Pedro de Atacama\n"
    )
    file.write("G33   7.608790.623411+0.779293Wickede\n")
    file.write("G34  13.7015 0.63254 +0.77203 Oberfrauendorf\n")
    file.write("G35 249.157890.849476+0.526134Elephant Head Obsevatory, Sahuarita\n")
    file.write("G36 357.452500.797538+0.601812Calar Alto-CASADO\n")
    file.write("G37 248.577490.822887+0.566916Lowell Discovery Telescope\n")
    file.write(
        "G38 356.768420.759967+0.647951Observatorio La Senda, Cabanillas del Campo\n"
    )
    file.write("G39 291.820390.921640-0.387711ROAD, San Pedro de Atacama\n")
    file.write("G40 343.491740.881470+0.471441Slooh.com Canary Islands Observatory\n")
    file.write("G41 264.738160.867040+0.496575Insperity Observatory, Humble\n")
    file.write(
        "G42 259.0230 0.90391 +0.42687 Observatorio Astronomico UAdeC, Saltillo\n"
    )
    file.write(
        "G43 293.6879 0.83817 -0.54382 Observatorio Buenaventura Suarez, San Luis\n"
    )
    file.write("G44 313.3061 0.92118 -0.38816 Observatorio Longa Vista, Sao Paulo\n")
    file.write(
        "G45 253.635640.832748+0.552480Space Surveillance Telescope, Atom Site\n"
    )
    file.write("G46 244.661530.818022+0.573711Pinto Valley Observatory\n")
    file.write("G47 253.806540.819827+0.571261HillTopTop Observatory, Edgewood\n")
    file.write(
        "G48 251.101480.849514+0.526196Harlingten Research Observatory, Rancho Hildalgo\n"
    )
    file.write("G49 266.5943 0.70889 +0.70302 Minnetonka\n")
    file.write("G50 253.3300 0.84629 +0.53134 Organ Mesa Observatory, Las Cruces\n")
    file.write("G51 239.957780.823164+0.565990Byrne Observatory, Sedgwick Reserve\n")
    file.write("G52 237.496040.785917+0.616275Stone Edge Observatory, El Verano\n")
    file.write("G53 240.587270.799043+0.599625Alder Springs Observatory, Auberry\n")
    file.write("G54 243.0630 0.83295 +0.55166 Hemet\n")
    file.write("G55 241.095330.816361+0.575651Bakersfield\n")
    file.write("G56 237.9294 0.78983 +0.61128 Walnut Creek\n")
    file.write("G57 236.8564 0.70171 +0.71009 Dilbert Observatory, Forest Grove\n")
    file.write(
        "G58 237.8180 0.79100 +0.60988 Chabot Space and Science Center, Oakland\n"
    )
    file.write("G59 237.4530 0.67475 +0.73559 Maiden Lane Obs., Bainbridge Island\n")
    file.write("G60 240.338880.825544+0.562496Carroll Observatory, Montecito\n")
    file.write("G61 238.1524 0.79270 +0.60760 Pleasanton\n")
    file.write(
        "G62 238.5469 0.72214 +0.68971 Sunriver Nature Center Observatory, Sunriver\n"
    )
    file.write("G63 238.6858 0.70152 +0.71031 Mill Creek Observatory, The Dalles\n")
    file.write("G64 239.2911 0.77535 +0.62979 Blue Canyon Observatory\n")
    file.write(
        "G65 238.3612 0.79616 +0.60338 Vulcan North, Lick Observatory, Mount Hamilton\n"
    )
    file.write("G66 238.9169 0.78135 +0.62206 Lake Forest Observatory, Forest Hills\n")
    file.write("G67 239.3650 0.78134 +0.62225 Rancho Del Sol, Camino\n")
    file.write("G68 240.2250 0.78044 +0.62355 Sierra Stars Observatory, Markleeville\n")
    file.write(
        "G69 241.0158 0.82829 +0.55850 Via Capote Sky Observatory, Thousand Oaks\n"
    )
    file.write("G70 241.4547 0.82543 +0.56273 Francisquito Observatory, Los Angeles\n")
    file.write("G71 241.6047 0.83216 +0.55276 Rancho Palos Verdes\n")
    file.write("G72 241.824080.829301+0.556970University Hills\n")
    file.write("G73 241.9400 0.82804 +0.55925 Mount Wilson-TIE\n")
    file.write("G74 242.885380.837429+0.544849Boulder Knolls Observatory, Escondido\n")
    file.write(
        "G75 243.2783 0.8351  +0.5487  Starry Knight Observatory, Coto de Caza\n"
    )
    file.write("G76 242.4178 0.83388 +0.55015 Altimira Observatory, Coto de Caza\n")
    file.write("G77 243.7183 0.8274  +0.5603  Baldwin Lake\n")
    file.write("G78 244.3127 0.84158 +0.53832 Desert Wanderer Observatory, El Centro\n")
    file.write(
        "G79 243.6165 0.82718 +0.56030 Goat Mountain Astronomical Research Station\n"
    )
    file.write("G80 240.5873 0.79904 +0.59962 Sierra Remote Observatories, Auberry\n")
    file.write("G81 242.913000.834904+0.548639Temecula\n")
    file.write("G82 248.400570.849482+0.526455SARA Observatory, Kitt Peak\n")
    file.write("G83 250.110390.842740+0.537440Mt. Graham-LBT\n")
    file.write("G84 249.210840.845112+0.533610Mount Lemmon SkyCenter\n")
    file.write("G85 247.565180.799502+0.599067Vermillion Cliffs Observatory, Kanab\n")
    file.write("G86 249.0697 0.84645 +0.53090 Tucson-Winterhaven\n")
    file.write(
        "G87 248.1894 0.74666 +0.66331 Calvin M. Hooper Memorial Observatory, Hyde Park\n"
    )
    file.write("G88 247.8881 0.83064 +0.55514 LAMP Observatory, New River\n")
    file.write("G89 248.3069 0.81933 +0.57197 Kachina Observatory, Flagstaff\n")
    file.write("G90 248.9658 0.84301 +0.53639 Three Buttes Observatory, Tucson\n")
    file.write(
        "G91 249.1219 0.85208 +0.52234 Whipple Observatory, Mt. Hopkins--2MASS\n"
    )
    file.write("G92 249.2814 0.84920 +0.52660 Jarnac Observatory, Vail\n")
    file.write("G93 249.3726 0.85215 +0.52201 Sonoita Research Observatory, Sonoita\n")
    file.write("G94 249.9267 0.84971 +0.52594 Sonoran Skies Observatory, St. David\n")
    file.write("G95 249.7622 0.85404 +0.51888 Hereford Arizona Observatory, Hereford\n")
    file.write("G96 249.211280.845111+0.533614Mt. Lemmon Survey\n")
    file.write(
        "G97 250.8694 0.84965 +0.52600 Astronomical League Alpha Observatory, Portal\n"
    )
    file.write("G98 251.343540.815037+0.578012Calvin-Rehoboth Observatory, Rehoboth\n")
    file.write("G99 251.8104 0.84192 +0.53835 NF Observatory, Silver City\n")
    file.write("H00 251.6987 0.84247 +0.53746 Tyrone\n")
    file.write("H01 252.810670.830474+0.556096Magdalena Ridge Observatory, Socorro\n")
    file.write("H02 253.3706 0.81146 +0.58309 Sulphur Flats Observatory, La Cueva\n")
    file.write("H03 253.3553 0.81753 +0.57440 Sandia View Observatory, Rio Rancho\n")
    file.write("H04 254.0260 0.81388 +0.57964 Santa Fe\n")
    file.write("H05 256.0707 0.77126 +0.63477 Edmund Kline Observatory, Deer Trail\n")
    file.write("H06 254.471300.840712+0.540310iTelescope Observatory, Mayhill\n")
    file.write("H07 254.471340.840711+0.5403107300 Observatory, Cloudcroft\n")
    file.write("H08 254.470810.840705+0.540319BlackBird Observatory, Cloudcroft\n")
    file.write("H09 255.5886 0.77070 +0.63549 Antelope Hills Observatory, Bennett\n")
    file.write("H10 254.471410.840711+0.540309Tzec Maun Observatory, Mayhill\n")
    file.write("H11 250.9840 0.85029 +0.52492 LightBuckets Observatory, Rodeo\n")
    file.write("H12 254.470780.840712+0.540307TechDome, Mayhill\n")
    file.write("H13 248.252120.840489+0.540134Lenomiya Observatory, Casa Grande\n")
    file.write("H14 249.212330.846402+0.530995Morning Star Observatory, Tucson\n")
    file.write("H15 254.471560.840711+0.540308ISON-NM Observatory, Mayhill\n")
    file.write("H16 253.2890 0.77152 +0.63472 HUT Observatory, Eagle\n")
    file.write("H17 254.383330.783783+0.619652Angel Peaks Observatory\n")
    file.write("H18 249.287980.849231+0.526572Vail View Observatory, Vail\n")
    file.write("H19 263.862590.828144+0.558685Lone Star Observatory, Caney\n")
    file.write(
        "H20 271.816820.772950+0.632393Eastern Illinois University Obs., Charleston\n"
    )
    file.write(
        "H21 272.031730.772885+0.632471Astronomical Research Observatory, Westfield\n"
    )
    file.write("H22 272.7371 0.77438 +0.63062 Terre Haute\n")
    file.write("H23 273.498580.862319+0.504671Pear Tree Observatory, Valparaiso\n")
    file.write("H24 274.598810.733648+0.677310J. C. Veen Observatory, Lowell\n")
    file.write("H25 266.870820.714467+0.697388Harvest Moon Observatory, Northfield\n")
    file.write(
        "H26 270.789220.735075+0.675789Doc Greiner Research Observatory, Janesvillle\n"
    )
    file.write("H27 266.231340.780074+0.623645Moonglow Observatory, Warrensburg\n")
    file.write("H28 263.231500.836912+0.545569Preston Hills Observatory, Celina\n")
    file.write("H29 262.5494 0.81372 +0.57940 Ivywood Observatory, Edmond\n")
    file.write(
        "H30 262.5558 0.81808 +0.57328 University of Oklahoma Observatory, Norman\n"
    )
    file.write("H31 263.3300 0.87011 +0.49123 Star Ridge Observatory, Weimar\n")
    file.write(
        "H32 263.6334 0.86174 +0.50567 Texas A&M Physics Observatory, College Station\n"
    )
    file.write("H33 264.1217 0.80990 +0.58466 Bixhoma Observatory, Bixby\n")
    file.write("H34 264.8258 0.84600 +0.53143 Chapel Hill\n")
    file.write("H35 264.9517 0.77423 +0.63085 Leavenworth\n")
    file.write("H36 264.293450.780428+0.623229Sandlot Observatory, Scranton\n")
    file.write(
        "H37 265.2003 0.72947 +0.68182 Grems Timmons Observatories, Graettinger\n"
    )
    file.write("H38 265.9864 0.75079 +0.65840 Timberline Observatory, Urbandale\n")
    file.write("H39 266.6828 0.70944 +0.70247 S.O.S. Observatory, Minneapolis\n")
    file.write("H40 266.7306 0.82519 +0.56302 Nubbin Ridge Observatory\n")
    file.write("H41 267.0742 0.81870 +0.57238 Petit Jean Mountain\n")
    file.write("H42 267.5078 0.73568 +0.67512 Wartburg College Observatory, Waverly\n")
    file.write("H43 267.4998 0.81918 +0.57163 Conway\n")
    file.write("H44 267.7982 0.81880 +0.57220 Cascade Mountain\n")
    file.write(
        "H45 267.0831 0.81890 +0.57210 Arkansas Sky Obs., Petit Jean Mountain South\n"
    )
    file.write("H46 265.7297 0.77818 +0.62602 Ricky Observatory, Blue Springs\n")
    file.write("H47 269.1439 0.84639 +0.53079 Vicksburg\n")
    file.write("H48 265.0139 0.79424 +0.60565 PSU Greenbush Observatory, Pittsburg\n")
    file.write(
        "H49 266.8636 0.81712 +0.57457 ATU Astronomical Observatory, Russellville\n"
    )
    file.write(
        "H50 267.541390.819253+0.571536University of Central Arkansas Obs., Conway\n"
    )
    file.write("H51 270.4003 0.73117 +0.68011 Greiner Research Observatory, Verona\n")
    file.write("H52 270.673540.739151+0.671335Hawkeye Observatory, Durand\n")
    file.write("H53 271.228420.789618+0.611581Thompsonville\n")
    file.write("H54 271.6514 0.71305 +0.69883 Cedar Drive Observatory, Pulaski\n")
    file.write(
        "H55 271.8558 0.77283 +0.63254 Astronomical Research Observatory, Charleston\n"
    )
    file.write("H56 272.167640.742693+0.667433Northbrook Meadow Observatory\n")
    file.write(
        "H57 275.972460.758850+0.649150Ohio State University Observatory, Lima\n"
    )
    file.write("H58 273.3353 0.82349 +0.56548 NASA/MSFC ALaMO, Redstone Arsenal\n")
    file.write("H59 273.3651 0.76362 +0.64356 Prairie Grass Observatory, Camp Cullom\n")
    file.write("H60 273.865420.767435+0.639034Heartland Observatory, Carmel\n")
    file.write("H61 281.416890.721533+0.690080Newcastle\n")
    file.write("H62 274.4117 0.73335 +0.67763 Calvin College Observatory\n")
    file.write("H63 274.9276 0.75227 +0.65672 DeKalb Observatory, Auburn\n")
    file.write(
        "H64 275.4364 0.77796 +0.62623 Thomas More College Observatory, Crestview Hills\n"
    )
    file.write("H65 275.4364 0.77995 +0.62381 Waltonfields Observatory, Walton\n")
    file.write("H66 276.1460 0.76956 +0.63651 Yellow Springs\n")
    file.write("H67 276.162410.740813+0.669522Stonegate Observatory, Ann Arbor\n")
    file.write("H68 276.348240.854246+0.518152Red Barn Observatory, Ty Ty\n")
    file.write("H69 276.944630.764320+0.642741Perkins Observatory, Delaware\n")
    file.write("H70 277.4458 0.81412 +0.57897 Asheville\n")
    file.write("H71 276.482820.852885+0.520378Chula\n")
    file.write("H72 278.2258 0.89584 +0.44289 Evelyn L. Egan Observatory, Fort Myers\n")
    file.write(
        "H73 278.6351 0.74850 +0.66097 Lakeland Astronomical Observatory, Kirtland\n"
    )
    file.write("H74 278.8747 0.87602 +0.48066 Bar J Observatory, New Smyrna Beach\n")
    file.write(
        "H75 278.918560.749551+0.659816Indian Hill North Observatory, Huntsburg\n"
    )
    file.write("H76 279.4133 0.90197 +0.43036 Oakridge Observatory, Miami\n")
    file.write("H77 279.7653 0.89877 +0.43695 Buehler Observatory\n")
    file.write(
        "H78 282.708961.000183+0.021030University of Narino Observatory, Pasto\n"
    )
    file.write("H79 280.492700.723258+0.688308York University Observatory, Toronto\n")
    file.write("H80 285.335670.763194+0.644015Halsted Observatory, Princeton\n")
    file.write("H81 283.615390.738959+0.671615Hartung-Boothroyd Observatory, Ithaca\n")
    file.write("H82 281.7839 0.77836 +0.62576 CBA-NOVAC Observatory, Front Royal\n")
    file.write("H83 282.6641 0.77926 +0.62463 Timberlake Observatory, Oakton\n")
    file.write("H84 282.4961 0.73259 +0.67843 Northview Observatory, Mendon\n")
    file.write("H85 283.0029 0.77784 +0.62638 Silver Spring\n")
    file.write("H86 283.1576 0.77693 +0.62749 CBA-East Observatory, Laurel\n")
    file.write("H87 282.4361 0.79309 +0.60708 Fenwick Observatory, Richmond\n")
    file.write("H88 283.7577 0.77295 +0.63235 Hope Observatory, Belcamp\n")
    file.write("H89 284.2975 0.70235 +0.70945 Galaxy Blues Observatory, Gatineau\n")
    file.write("H90 284.4731 0.70267 +0.70914 Ottawa\n")
    file.write("H91 285.048390.712263+0.699590Reynolds Observatory, Potsdam\n")
    file.write("H92 285.6211 0.76785 +0.63849 Arcturus Observatory\n")
    file.write("H93 285.5758 0.75934 +0.64853 Berkeley Heights\n")
    file.write("H94 285.5439 0.75781 +0.65032 Cedar Knolls\n")
    file.write("H95 285.821200.758745+0.649211NJIT Observatory, Newark\n")
    file.write("H96 286.6142 0.69143 +0.72005 Observatoire des Pleiades, Mandeville\n")
    file.write("H97 287.201320.746487+0.663233Talcott Mountain Science Center, Avon\n")
    file.write("H98 287.2655 0.74987 +0.65938 Dark Rosanne Obs., Middlefield\n")
    file.write("H99 288.8036 0.74040 +0.66992 Sunhill Observatory, Newton\n")
    file.write("I00 288.2294 0.74794 +0.66157 Carbuncle Hill Observatory, Coventry\n")
    file.write("I01 288.862530.740677+0.669630Clay Center Observatory, Brookline\n")
    file.write(
        "I02 289.1949 0.86558 -0.49976 Cerro Tololo Observatory, La Serena--2MASS\n"
    )
    file.write(
        "I03 289.266260.873440-0.486052European Southern Obs., La Silla--ASTROVIRTEL\n"
    )
    file.write("I04 289.3152 0.86693 -0.49697 Mamalluca Observatory\n")
    file.write("I05 289.2980 0.87559 -0.48217 Las Campanas Observatory-TIE\n")
    file.write(
        "I06 289.8061 0.74801 +0.66147 Werner Schmidt Obs., Dennis-Yarmouth Regional HS\n"
    )
    file.write("I07 288.0971 0.74279 +0.66735 Conlin Hill Observatory, Oxford\n")
    file.write("I08 290.6932 0.85116 -0.52394 Alianza S4, Cerro Burek\n")
    file.write("I09 289.803770.910166-0.413875Cerro Armazones\n")
    file.write("I10 291.8200 0.92165 -0.38770 CAO, San Pedro de Atacama (until 2012)\n")
    file.write("I11 289.263450.865020-0.500901Gemini South Observatory, Cerro Pachon\n")
    file.write("I12 288.870530.736679+0.673998Phillips Academy Observatory, Andover\n")
    file.write("I13 282.930060.779116+0.624793Burleith Observatory, Washington D.C.\n")
    file.write("I14 288.589310.740298+0.670040Tigh Speuran Observatory, Framingham\n")
    file.write("I15 288.700760.747034+0.662558Wishing Star Observatory, Barrington\n")
    file.write("I16 291.820330.921638-0.387715IAA-AI Atacama, San Pedro de Atacama\n")
    file.write(
        "I17 284.322060.748993+0.660451Thomas G. Cupillari Observatory, Fleetville\n"
    )
    file.write("I18 281.3067 0.79038 +0.61070 Fan Mountain Observatory, Covesville\n")
    file.write("I19 295.407110.854834-0.517422Observatorio El Gato Gris, Tanti\n")
    file.write(
        "I20 295.681610.838551-0.543122Observatorio Astronomico Salvador, Rio Cuarto\n"
    )
    file.write("I21 295.8281 0.85465 -0.51760 El Condor Observatory, Cordoba\n")
    file.write(
        "I22 296.173990.712120+0.699724Abbey Ridge Observatory, Stillwater Lake\n"
    )
    file.write("I23 292.266490.714173+0.697623Frosty Cold Observatory, Mash Harbor\n")
    file.write(
        "I24 282.2306 0.78534 +0.61702 Lake of the Woods Observatory, Locust Grove\n"
    )
    file.write("I25 295.443810.850887-0.523945ECCCO Observatory, Bosque Alegre\n")
    file.write("I26 295.8214 0.85417 -0.51839 Observatorio Kappa Crucis, Cordoba\n")
    file.write("I27 284.0006 0.70401 +0.70783 Barred Owl Observatory, Carp\n")
    file.write("I28 289.0889 0.74643 +0.66324 Starhoo Observatory, Lakeville\n")
    file.write("I29 288.633040.738432+0.672081Middlesex School Observatory, Concord\n")
    file.write("I30 299.3417 0.83966 -0.54131 Observatorio Geminis Austral\n")
    file.write(
        "I31 299.3649 0.83995 -0.54086 Observatorio Astronomico del Colegio Cristo Rey\n"
    )
    file.write("I32 299.3464 0.83969 -0.54125 Observatorio Beta Orionis, Rosario\n")
    file.write("I33 289.2608 0.86504 -0.50086 SOAR, Cerro Pachon\n")
    file.write("I34 284.1297 0.76548 +0.64134 Morgantown\n")
    file.write("I35 301.5572 0.82198 -0.56762 Sidoli\n")
    file.write("I36 301.282710.819978-0.570483Observatorio Los Campitos, Canuelas\n")
    file.write("I37 301.352750.825603-0.562360Astrodomi Observatory, Santa Rita\n")
    file.write("I38 302.021410.854400-0.517885Observatorio Los Algarrobos, Salto\n")
    file.write("I39 301.426610.823342-0.565652Observatorio Cruz del Sur, San Justo\n")
    file.write("I40 289.260610.873472-0.485986La Silla--TRAPPIST\n")
    file.write("I41 243.140220.836325+0.546877Palomar Mountain--ZTF\n")
    file.write("I42 288.9081 0.74895 +0.66041 Westport Observatory\n")
    file.write(
        "I43 261.902370.846901+0.530084Tarleton State University Obs., Stephenville\n"
    )
    file.write(
        "I44 273.5176 0.86201 +0.50521 Northwest Florida State College, Niceville\n"
    )
    file.write(
        "I45 301.4281 0.82326 -0.56577 W Crusis Astronomical Observatory, San Justo\n"
    )
    file.write("I46 281.6108 0.76192 +0.64558 The Cottage Observatory, Altoona\n")
    file.write("I47 290.5503 0.81526 -0.57753 Pierre Auger Observatory, Malargue\n")
    file.write("I48 295.6757 0.80340 -0.59348 Observatorio El Catalejo, Santa Rosa\n")
    file.write("I49 253.986170.813183+0.580617Sunflower Observatory, Santa Fe\n")
    file.write("I50 254.471420.840712+0.540309P2 Observatory, Mayhill\n")
    file.write("I51 283.0547 0.78133 +0.62203 Clinton\n")
    file.write(
        "I52 249.211080.845113+0.533611Steward Observatory, Mt. Lemmon Station\n"
    )
    file.write("I53 356.3783 0.79822 +0.60052 Armilla\n")
    file.write("I54 353.030810.779853+0.623912Observatorio Las Vaguadas, Badajoz\n")
    file.write("I55 359.642140.772769+0.632566Valencia\n")
    file.write(
        "I56 357.710660.801182+0.596429Observatorio Astronomico John Beckman, Almeria\n"
    )
    file.write("I57 359.3256 0.78579 +0.61646 Elche\n")
    file.write("I58 359.5374 0.77206 +0.63345 Betera\n")
    file.write(
        "I59 356.1558 0.72754 +0.68377 Observatorio Fuente de los matos, Muriedas\n"
    )
    file.write("I60 357.1781 0.67397 +0.73630 Guernanderf\n")
    file.write("I61 352.1494 0.74047 +0.66989 Ourense\n")
    file.write("I62 356.426390.767072+0.639561Observatorio Helios Ontigola\n")
    file.write("I63 358.8330 0.62944 +0.77446 Cygnus Observatory, New Airesford\n")
    file.write("I64 359.293860.623532+0.779182Maidenhead\n")
    file.write("I65 355.0796 0.80245 +0.59491 Yunquera\n")
    file.write("I66 312.0000 0.96235 -0.27153 Taurus Australis Observatory, Brasilia\n")
    file.write("I67 359.087530.626440+0.776870Hartley Wintney\n")
    file.write("I68 312.4981 0.96931 -0.24573 Pousada dos Anoes Observatory\n")
    file.write("I69 352.0069 0.85232 +0.52140 AGM Observatory, Marrakech\n")
    file.write("I70 359.941580.604128+0.794217Gedney House Observatory, Kirton\n")
    file.write("I71 353.6698 0.77330 +0.63205 Observatorio Los Milanos, Caceres\n")
    file.write("I72 355.9849 0.75923 +0.64893 Observatorio Carpe-Noctem, Madrid\n")
    file.write("I73 359.587110.670611+0.739353Salvia Observatory, Saulges\n")
    file.write("I74 358.187390.629588+0.774337Baxter Garden Observatory, Salisbury\n")
    file.write("I75 359.9650 0.76735 +0.63910 Observatorio Los Caracoles, Castello\n")
    file.write("I76 355.936810.761573+0.646107Observatorio Tesla, Valdemorillo\n")
    file.write("I77 316.0025 0.94119 -0.33714 CEAMIG-REA Observatory, Belo Horizonte\n")
    file.write("I78 355.5721 0.80240 +0.59481 Observatorio Principia, Malaga\n")
    file.write("I79 357.6733 0.78743 +0.61474 AstroCamp, Nerpio\n")
    file.write("I80 358.133280.590762+0.804183Rose Cottage Observatory, Keighley\n")
    file.write("I81 356.201110.533510+0.842967Tarbatness Observatory, Portmahomack\n")
    file.write("I82 343.5797 0.88105 +0.47156 Guimar\n")
    file.write("I83 353.1900 0.59630 +0.80008 Cherryvalley Observatory, Rathmolyon\n")
    file.write("I84 353.0212 0.77967 +0.62415 Cerro del Viento, Badajoz\n")
    file.write("I85 357.9848 0.80086 +0.59686 Las Negras\n")
    file.write("I86 356.2739 0.76211 +0.64543 Observatorio UCM, Madrid\n")
    file.write("I87 352.9593 0.60121 +0.79643 Astroshot Observatory, Monasterevin\n")
    file.write("I88 356.0823 0.79287 +0.60753 Fuensanta de Martos\n")
    file.write("I89 357.6739 0.78744 +0.61474 iTelescope Observatory, Nerpio\n")
    file.write("I90 351.597600.618315+0.783298Blackrock Castle Observatory\n")
    file.write("I91 357.692500.801192+0.596407Retamar\n")
    file.write(
        "I92 353.952890.795987+0.603315Astreo Observatory, Mairena del Aljarafe\n"
    )
    file.write("I93 359.797000.713711+0.698096St Pardon de Conques\n")
    file.write(
        "I94 356.1367 0.76162 +0.64603 Observatorio Rho Ophiocus, Las Rozas de Madrid\n"
    )
    file.write("I95 356.813940.771993+0.633666Observatorio de la Hita\n")
    file.write(
        "I96 356.503840.758233+0.649960Hyperion Observatory, Urbanizacion Caraquiz\n"
    )
    file.write(
        "I97 359.501780.621889+0.780493Penn Heights Observatory, Rickmansworth\n"
    )
    file.write("I98 356.413390.757256+0.651181El Berrueco\n")
    file.write("I99 356.460430.763221+0.644121Observatorio Blanquita, Vaciamadrid\n")
    file.write("J00 359.5056 0.76880 +0.63744 Segorbe\n")
    file.write("J01 354.284500.739938+0.670609Observatorio Cielo Profundo, Leon\n")
    file.write("J02 359.5550 0.78391 +0.61884 Busot\n")
    file.write("J03 355.132500.638787+0.766833Gothers Observatory, St. Dennis\n")
    file.write("J04 343.488170.881463+0.471461ESA Optical Ground Station, Tenerife\n")
    file.write("J05 355.296390.749617+0.659822Bootes Observatory, Boecillo\n")
    file.write(
        "J06 358.812470.604374+0.794039Trent Astronomical Observatory, Clifton\n"
    )
    file.write(
        "J07 353.895430.767881+0.638546Observatorio SPAG Monfrague, Palazuelo-Empalme\n"
    )
    file.write("J08 359.6549 0.77127 +0.63439 Observatorio Zonalunar, Puzol\n")
    file.write("J09 353.7917 0.59450 +0.80141 Balbriggan\n")
    file.write("J10 359.598390.784437+0.618151Alicante\n")
    file.write("J11 351.317690.746984+0.662617Matosinhos\n")
    file.write("J12 356.510610.758248+0.649949Caraquiz\n")
    file.write("J13 342.1208 0.87763 +0.47851 La Palma-Liverpool Telescope\n")
    file.write("J14 345.992810.880303+0.472891La Corte\n")
    file.write("J15 352.830610.755420+0.653125Muxagata\n")
    file.write("J16 354.203560.584292+0.808826An Carraig Observatory, Loughinisland\n")
    file.write("J17 357.203130.609723+0.790018Ragdon\n")
    file.write("J18 356.906000.609920+0.789845Dingle Observatory, Montgomery\n")
    file.write("J19 359.830360.764671+0.642359El Maestrat\n")
    file.write("J20 356.219260.762019+0.645541Aravaca\n")
    file.write("J21 356.080030.759065+0.649062El Boalo\n")
    file.write("J22 342.132350.878415+0.476543Tacande Observatory, La Palma\n")
    file.write("J23 358.493610.671765+0.738300Centre Astronomique de La Couyere\n")
    file.write("J24 343.557190.881661+0.470499Observatorio Altamira\n")
    file.write("J25 354.488830.728241+0.683076Penamayor Observatory, Nava\n")
    file.write("J26 356.981190.612507+0.787898The Spaceguard Centre, Knighton\n")
    file.write("J27 355.968990.760373+0.647528El Guijo Observatory\n")
    file.write("J28 356.213810.791408+0.609366Jaen\n")
    file.write("J29 346.342130.875695+0.481318Observatorio Nira, Tias\n")
    file.write("J30 356.293000.761925+0.645666Observatorio Ventilla, Madrid\n")
    file.write("J31 355.774110.802445+0.594759La Axarquia\n")
    file.write("J32 352.977690.796769+0.602268Aljaraque\n")
    file.write(
        "J33 359.906000.620040+0.781953University of Hertfordshire Obs., Bayfordbury\n"
    )
    file.write("J34 355.227110.748695+0.660858La Fecha\n")
    file.write("J35 356.029110.792167+0.608432Tucci Observatory, Martos\n")
    file.write("J36 356.945190.765179+0.641659Observatorio DiezALaOnce, Illana\n")
    file.write("J37 353.064690.796893+0.602104Huelva\n")
    file.write("J38 353.609240.726887+0.684518Observatorio La Vara, Valdes\n")
    file.write("J39 344.5636 0.88429 +0.46547 Ingenio\n")
    file.write("J40 355.558470.802546+0.594601Malaga\n")
    file.write("J41 353.8189 0.59779 +0.79897 Raheny\n")
    file.write("J42 359.6989 0.77138 +0.63425 Puzol\n")
    file.write("J43 352.133540.856441+0.515339Oukaimeden Observatory, Marrakech\n")
    file.write("J44 357.6552 0.73506 +0.67596 Observatorio Iturrieta, Alava\n")
    file.write(
        "J45 344.467350.883626+0.466916Observatorio Montana Cabreja, Vega de San Mateo\n"
    )
    file.write("J46 346.3594 0.87569 +0.48131 Observatorio Montana Blanca, Tias\n")
    file.write("J47 346.4440 0.87501 +0.48260 Observatorio Nazaret\n")
    file.write("J48 343.6960 0.87977 +0.47393 Observatory Mackay, La Laguna\n")
    file.write("J49 359.4482 0.78695 +0.61496 Santa Pola\n")
    file.write("J50 342.1176 0.87764 +0.47847 La Palma-NEON\n")
    file.write("J51 343.728980.879789+0.473809Observatorio Atlante, Tenerife\n")
    file.write("J52 358.6608 0.74198 +0.66826 Observatorio Pinsoro\n")
    file.write("J53 354.892780.791142+0.609607Posadas\n")
    file.write("J54 343.4906 0.88149 +0.47142 Bradford Robotic Telescope\n")
    file.write("J55 344.3144 0.88549 +0.46313 Los Altos de Arguineguin Observatory\n")
    file.write("J56 344.4536 0.88416 +0.46624 Observatorio La Avejerilla\n")
    file.write(
        "J57 358.890890.767817+0.638833Centro Astronomico Alto Turia, Valencia\n"
    )
    file.write(
        "J58 356.6644 0.62304 +0.77959 Brynllefrith Observatory, Llantwit Fardre\n"
    )
    file.write("J59 356.202560.726956+0.684386Observatorio Linceo, Santander\n")
    file.write("J60 354.3406 0.74773 +0.66201 Tocororo Observatory, Arquillinos\n")
    file.write("J61 353.4264 0.59719 +0.79942 Brownstown Observatory, Kilcloon\n")
    file.write("J62 351.6345 0.59017 +0.80459 Kingsland Observatory, Boyle\n")
    file.write("J63 359.4831 0.78548 +0.61683 San Gabriel\n")
    file.write("J64 359.3459 0.78871 +0.61271 La Mata\n")
    file.write("J65 353.4497 0.59830 +0.79860 Celbridge\n")
    file.write("J66 357.7833 0.61071 +0.78922 Kinver\n")
    file.write("J67 359.4667 0.77114 +0.63457 Observatorio La Puebla de Vallbona\n")
    file.write("J68 357.7055 0.61813 +0.78345 Tweenhills Observatory, Hartpury\n")
    file.write("J69 358.980340.631443+0.772863North Observatory, Clanfield\n")
    file.write(
        "J70 358.8404 0.78968 +0.61149 Obs. Astronomico Vega del Thader, El Palmar\n"
    )
    file.write("J71 357.8947 0.59350 +0.80217 Willow Bank Observatory\n")
    file.write("J72 358.9664 0.79065 +0.61028 Valle del Sol\n")
    file.write("J73 359.0833 0.6187  +0.7830  Quainton\n")
    file.write("J74 357.0961 0.72950 +0.68169 Bilbao\n")
    file.write("J75 357.434710.789388+0.612222OAM Observatory, La Sagra\n")
    file.write("J76 358.797180.790771+0.610163La Murta\n")
    file.write(
        "J77 357.5947 0.63154 +0.77276 Golden Hill Observatory, Stourton Caundle\n"
    )
    file.write("J78 358.8244 0.78887 +0.61253 Murcia\n")
    file.write("J79 358.380660.795516+0.603908Observatorio Calarreona, Aguilas\n")
    file.write("J80 359.1083 0.70862 +0.70323 Sainte Helene\n")
    file.write("J81 358.134890.735984+0.674878Guirguillano\n")
    file.write("J82 357.3067 0.5935  +0.8021  Leyland\n")
    file.write("J83 357.3883 0.59274 +0.80270 Olive Farm Observatory, Hoghton\n")
    file.write("J84 358.9803 0.63144 +0.77285 South Observatory, Clanfield\n")
    file.write("J85 357.4833 0.5666  +0.8213  Makerstoun\n")
    file.write("J86 356.6153 0.79930 +0.59968 Sierra Nevada Observatory\n")
    file.write("J87 355.5067 0.76047 +0.64753 La Canada\n")
    file.write("J88 358.5592 0.63165 +0.77266 Strawberry Field Obs., Southampton\n")
    file.write("J89 356.2861 0.76045 +0.64739 Tres Cantos Observatory\n")
    file.write("J90 358.5317 0.62251 +0.78000 West Challow\n")
    file.write("J91 357.0483 0.7411  +0.6692  Alt emporda Observatory, Figueres\n")
    file.write("J92 359.3487 0.62214 +0.78031 Beaconsfield\n")
    file.write("J93 357.7426 0.61927 +0.78255 Mount Tuffley Observatory, Gloucester\n")
    file.write("J94 357.7886 0.61909 +0.78270 Abbeydale\n")
    file.write("J95 358.553010.624152+0.778715Great Shefford\n")
    file.write("J96 356.056690.735326+0.675690Observatorio de Cantabria\n")
    file.write("J97 359.5333 0.7754  +0.6293  Alginet\n")
    file.write("J98 359.5344 0.77275 +0.63259 Observatorio Manises\n")
    file.write("J99 359.578080.772589+0.632790Burjassot\n")
    file.write("K00   8.948360.642630+0.763639Hanau\n")
    file.write("K01   0.620910.618636+0.783060Astrognosis Observatory, Bradwell\n")
    file.write("K02   0.667610.622858+0.779718Eastwood Observatory, Leigh on Sea\n")
    file.write("K03   0.744110.744133+0.665979Observatori AAS Montsec\n")
    file.write("K04   0.744160.744130+0.665983Lo Fossil Observatory, Ager\n")
    file.write("K05   1.023110.610689+0.789233Eden Observatory, Banham\n")
    file.write("K06   1.999500.749658+0.659703Observatorio Montagut, Can Sola\n")
    file.write("K07   2.4614 0.65973 +0.74902 Observatoire de Gravelle, St. Maurice\n")
    file.write("K08   1.8800 0.75142 +0.65773 Observatorio Lledoner, Vallirana\n")
    file.write("K09   2.2400 0.74889 +0.66051 Llica d'Amunt\n")
    file.write("K10   5.4214 0.71851 +0.69332 Micro Palomar, Reilhanette\n")
    file.write("K11   2.880790.697458+0.714390Observatoire de Pommier\n")
    file.write("K12   2.7267 0.77121 +0.63447 Obsevatorio Astronomico de Marratxi\n")
    file.write("K13   2.9124 0.77015 +0.63575 Albireo Observatory, Inca\n")
    file.write("K14   2.9131 0.77090 +0.63485 Observatorio de Sencelles\n")
    file.write("K15   3.755220.725152+0.686311Murviel-les-Montpellier\n")
    file.write("K16   5.421060.718540+0.693283Reilhanette\n")
    file.write("K17   7.026790.692802+0.718806Observatoire des Valentines, Bex\n")
    file.write("K18   7.5242 0.67588 +0.73460 Hesingue\n")
    file.write("K19   5.647310.720582+0.691187PASTIS Observatory, Banon\n")
    file.write("K20   4.680150.642261+0.763954Danastro Observatory, Romeree\n")
    file.write("K21   4.9292 0.72101 +0.69061 Saint-Saturnin-les-Avignon\n")
    file.write("K22   5.076110.724222+0.687283Les Barres Observatory, Lamanon\n")
    file.write("K23   9.4023 0.70168 +0.71014 Gorgonzola\n")
    file.write("K24   6.860690.651487+0.756168Schmelz\n")
    file.write(
        "K25   5.7136 0.72157 +0.69014 Haute Provence Sud, Saint-Michel-l'Observatoire\n"
    )
    file.write("K26   6.2201 0.64965 +0.75775 Contern\n")
    file.write(
        "K27   6.2094 0.68296 +0.72816 St-Martin Observatory, Amathay Vesigneux\n"
    )
    file.write("K28   6.8947 0.63326 +0.77137 Sternwarte Eckdorf\n")
    file.write("K29   7.783470.696415+0.715918Stellarium Gornergrat\n")
    file.write("K30   7.148390.682674+0.728365Luscherz\n")
    file.write("K31   7.003610.713656+0.698546Osservatorio Astronomico di Bellino\n")
    file.write("K32   7.529640.716152+0.695733Maritime Alps Observatory, Cuneo\n")
    file.write("K33   7.497610.715775+0.696117San Defendente\n")
    file.write("K34   7.7005 0.70697 +0.70492 Turin\n")
    file.write("K35   8.163690.639883+0.765937Huenfelden\n")
    file.write("K36   8.248870.645167+0.761522Ebersheim\n")
    file.write("K37   8.3148 0.70738 +0.70449 Cereseto\n")
    file.write("K38   8.918240.697505+0.714297M57 Observatory, Saltrio\n")
    file.write("K39   8.955560.714080+0.697844Serra Observatory\n")
    file.write("K40   9.0135 0.66228 +0.74685 Altdorf\n")
    file.write(
        "K41   8.7930 0.71113 +0.70075 Vegaquattro Astronomical Obs., Novi Ligure\n"
    )
    file.write("K42   8.3332 0.65685 +0.75151 Knielingen\n")
    file.write("K43   9.8389 0.69215 +0.71970 OVM Observatory, Chiesa in Valmalencom\n")
    file.write("K44   9.973310.615161+0.785779Marienburg Sternwarte, Hildesheim\n")
    file.write(
        "K45  10.498140.733299+0.677639Oss. Astronomico di Punta Falcone, Piombino\n"
    )
    file.write("K46  10.9114 0.64561 +0.76115 Bamberg\n")
    file.write("K47  10.688220.724257+0.687222BSCR Observatory, Santa Maria a Monte\n")
    file.write(
        "K48  10.838810.705714+0.706127Keyhole Observatory, San Giorgio di Mantova\n"
    )
    file.write("K49  11.185810.724381+0.687146Carpione Observatory, Spedaletto\n")
    file.write("K50  11.133000.646903+0.760116Sternwarte Feuerstein, Ebermannstadt\n")
    file.write(
        "K51  11.6579 0.69563 +0.71626 Osservatorio del Celado, Castello Tesino\n"
    )
    file.write(
        "K52   7.6478 0.70548 +0.70642 Gwen Observatory, San Francesco al Campo\n"
    )
    file.write("K53  12.045640.744479+0.665409Marina di Cerveteri\n")
    file.write(
        "K54  11.336780.728803+0.682494Astronomical Observatory University of Siena\n"
    )
    file.write("K55   7.765000.645586+0.761172Wallhausen\n")
    file.write("K56  12.704970.732993+0.678008Osservatorio di Foligno\n")
    file.write("K57  13.0444 0.69854 +0.71317 Fiore Observatory\n")
    file.write("K58   7.4497 0.62655 +0.77685 Gevelsberg\n")
    file.write("K59  13.277440.620411+0.781663Elsterland Observatory, Jessnigk\n")
    file.write("K60  13.510690.568623+0.819848Lindby\n")
    file.write("K61  13.6026 0.64741 +0.75967 Rokycany Observatory\n")
    file.write("K62  13.846750.635514+0.769557Teplice Observatory\n")
    file.write(
        "K63  10.4620 0.71953 +0.69218 G. Pascoli Observatory, Castelvecchio Pascoli\n"
    )
    file.write("K64  11.743970.644963+0.761748Waizenreuth\n")
    file.write("K65  12.2339 0.71879 +0.69290 Cesena\n")
    file.write("K66  12.628610.750491+0.658684Osservatorio Astronomico di Anzio\n")
    file.write("K67  13.3610 0.65835 +0.75036 Bayerwald Sternwarte, Spiegelau\n")
    file.write("K68  14.905120.759709+0.648110Osservatorio Elianto, Pontecagnano\n")
    file.write("K69  10.9941 0.62938 +0.77452 Riethnordhausen\n")
    file.write("K70  15.9736 0.78375 +0.61901 Rosarno\n")
    file.write("K71  12.2159 0.65748 +0.75101 Neutraubling\n")
    file.write("K72  16.3396 0.77485 +0.63021 Celico\n")
    file.write("K73  16.4158 0.75789 +0.65029 Gravina in Puglia\n")
    file.write(
        "K74  10.2364 0.64667 +0.76025 Muensterschwarzach Observatory, Schwarzach\n"
    )
    file.write(
        "K75  11.7289 0.68897 +0.72269 Astro Dolomites, Santa Cristina Valgardena\n"
    )
    file.write("K76   7.628980.713488+0.698410BSA Osservatorio, Savigliano\n")
    file.write("K77  11.2903 0.64680 +0.76019 EHB01 Observatory, Engelhardsberg\n")
    file.write("K78   9.853560.718987+0.692718iota Scorpii Observatory, La Spezia\n")
    file.write("K79  11.057890.631175+0.773097Erfurt\n")
    file.write("K80  16.637330.610859+0.789111Platanus Observatory, Lusowko\n")
    file.write("K81  13.785110.748666+0.660819P.M.P.H.R. Deep Sky Observatory, Atina\n")
    file.write("K82  17.5894 0.75937 +0.64854 Alphard Observatory, Ostuni\n")
    file.write(
        "K83  11.043170.723487+0.688080Beppe Forti Astronomical Observatory, Montelupo\n"
    )
    file.write("K84  10.758610.718340+0.693581Felliscopio Observatory, Fellicarolo\n")
    file.write("K85   6.031610.634354+0.770499Kelmis\n")
    file.write("K86  10.181890.701516+0.710308Brescia\n")
    file.write("K87  10.170110.646647+0.760288Dettelbach Vineyard Observatory\n")
    file.write("K88  19.8936 0.67154 +0.73869 GINOP-KHK, Piszkesteto\n")
    file.write("K89  11.563390.738665+0.671860Digital Stargate Observatory, Manciano\n")
    file.write("K90  20.545770.714093+0.697776Sopot Astronomical Observatory\n")
    file.write("K91  20.810190.845561-0.532618Sutherland-LCO A\n")
    file.write("K92  20.810040.845561-0.532618Sutherland-LCO B\n")
    file.write("K93  20.810110.845560-0.532620Sutherland-LCO C\n")
    file.write("K94  20.810970.845561-0.532606Sutherland\n")
    file.write("K95  20.811060.845555-0.532613MASTER-SAAO Observatory, Sutherland\n")
    file.write("K96  16.751190.774870+0.630302Savelli Observatory\n")
    file.write("K97   7.180260.664361+0.745050Freconrupt\n")
    file.write("K98  17.072170.608205+0.7911426ROADS Observatory 1, Wojnowko\n")
    file.write("K99  22.453500.663064+0.746102Derenivka Observatory\n")
    file.write("L00  12.5375 0.74535 +0.66446 East Rome Observatory, Rome\n")
    file.write("L01  13.749300.704742+0.707169Visnjan Observatory, Tican\n")
    file.write("L02  20.816580.771051+0.634781NOAK Observatory, Stavraki\n")
    file.write("L03  14.730810.671765+0.738393SGT Observatory, Gaflenz\n")
    file.write("L04  23.596400.685544+0.725675ROASTERR-1 Observatory, Cluj-Napoca\n")
    file.write("L05  10.0699 0.70093 +0.71089 Dridri Observatory, Franciacorta\n")
    file.write(
        "L06   9.254030.696280+0.715445Sormano 2 Observatory, Bellagio Via Lattea\n"
    )
    file.write(
        "L07  14.564060.760166+0.647727Osservatorio Salvatore di Giacomo, Agerola\n"
    )
    file.write("L08  24.394470.497926+0.864325Metsahovi Optical Telescope, Metsahovi\n")
    file.write("L09  20.809870.845559-0.532619Sutherland-LCO Aqawan A #1\n")
    file.write("L10  22.6186 0.78943 +0.61203 Kryoneri Observatory\n")
    file.write("L11  17.2092 0.50421 +0.86070 Sandvreten Observatory\n")
    file.write("L12   2.677890.629068+0.774754Koksijde\n")
    file.write("L13  25.621930.700409+0.711479Stardust Observatory, Brasov\n")
    file.write(
        "L14   4.922470.698669+0.713095Planetarium de Vaulx-en-Velin Observatory\n"
    )
    file.write("L15  25.978390.708234+0.703665St. George Observatory, Ploiesti\n")
    file.write(
        "L16  26.045610.705820+0.706098Stardreams Observatory, Valenii de Munte\n"
    )
    file.write("L17   2.7114 0.74071 +0.66964 Observatori Astronomic Albanya\n")
    file.write("L18  26.718280.659348+0.749399QOS Observatory, Zalistsi\n")
    file.write("L19  11.152580.716257+0.695653Osservatorio Felsina AAB, Montepastore\n")
    file.write("L20  18.320690.722441+0.689239AG_Sarajevo Observatory, Sarajevo\n")
    file.write("L21  27.421280.720179+0.691479Ostrov Observatory, Constanta\n")
    file.write("L22  27.669530.692963+0.718573Barlad Observatory\n")
    file.write("L23  27.8319 0.70211 +0.70968 Schela Observatory\n")
    file.write("L24  27.9289 0.89882 -0.43743 Gauteng\n")
    file.write("L25  14.437390.598174+0.798700Smolecin\n")
    file.write(
        "L26  11.810190.743368+0.666653Sanderphil Urban Observatory, Civitavecchia\n"
    )
    file.write("L27   5.647040.720583+0.69119729PREMOTE Observatory, Dauban\n")
    file.write("L28  15.463390.758034+0.650341ISON-Castelgrande Observatory\n")
    file.write("L29  18.0169 0.91802 -0.39574 Drebach-South Observatory, Windhoek\n")
    file.write("L30   7.514690.624126+0.778737Lohbach Observatory, Benninghofen\n")
    file.write("L31  12.856150.632524+0.772019RaSo Observatory, Chemnitz\n")
    file.write(
        "L32  20.810440.845576-0.532593Korea Microlensing Telescope Network-SAAO\n"
    )
    file.write("L33  29.9546 0.67379 +0.73646 Ananiv\n")
    file.write("L34  14.020610.789742+0.611548Galhassin Robotic Telescope, Isnello\n")
    file.write("L35  30.5086 0.64055 +0.76537 DreamSky Observatory, Lisnyky\n")
    file.write("L36  14.780080.645319+0.761467Ondrejov--BlueEye600 Telescope\n")
    file.write(
        "L37 353.738830.803937+0.592739Observatorio Alnitak, El Puerto de Santa Maria\n"
    )
    file.write("L38   9.699970.615648+0.785407Gartensternwarte Schafsweide, Sehlde\n")
    file.write("L39  11.040310.723062+0.688490Osservatorio Spica, Signa\n")
    file.write("L40   6.956810.654011+0.754011Sternwarte Saarbruecken Rastpfuhl\n")
    file.write("L41  12.301810.720683+0.691022Ponte Uso\n")
    file.write("L42  11.5633 0.73670 +0.67400 Observatory-Astrocamp Manciano\n")
    file.write("L43   0.744390.744131+0.665982Ager, Leida\n")
    file.write("L44   6.221110.688185+0.723360AstroVal, Le Chenit\n")
    file.write("L45  15.062430.793975+0.605979ObsCT, Catania\n")
    file.write("L46 356.119390.762017+0.645574Observatorio Majadahonda\n")
    file.write("L47  12.507110.725542+0.685961Osservatorio Astronomico, Piobbico\n")
    file.write("L48  23.568730.674816+0.735566CNVL Observatory, Baia Mare\n")
    file.write("L49  13.007300.671444+0.738747VEGA-Sternwarte, Dorfleiten\n")
    file.write("L50  34.0114 0.71157 +0.70039 GenShtab Observatory, Nauchnyi\n")
    file.write("L51  34.0164 0.71169 +0.70028 MARGO, Nauchnyi\n")
    file.write("L52  34.016940.711679+0.700287MASTER-Tavrida\n")
    file.write("L53   9.033810.699589+0.712226Lomazzo Observatory, Como\n")
    file.write("L54  22.888780.700705+0.711157Berthelot Observatory, Hunedoara\n")
    file.write("L55  35.087500.666222+0.743283Sura Gardens, Dnipro\n")
    file.write("L56   8.058580.638960+0.766697Sternwarte Limburg, Limburg\n")
    file.write("L57  26.904190.688762+0.722601Bacau Observatory, Bacau\n")
    file.write("L58  30.571080.691710+0.719771Heavenly Owl observatory\n")
    file.write("L59   1.226060.651546+0.756108Compustar Observatory, Rouen\n")
    file.write("L60  30.697220.644961+0.761695Popovich Observatory, Ivanivka\n")
    file.write("L61  20.810280.845575-0.532593MONET South, Sutherland\n")
    file.write("L62  12.528890.719467+0.692209Hypatia Observatory, Rimini\n")
    file.write("L63  11.009140.723671+0.687849HOB Observatory, Capraia Fiorentina\n")
    file.write(
        "L64   9.363140.701822+0.710005Martesana Observatory, Cassina de Pecchi\n"
    )
    file.write("L65   8.828310.602059+0.795784Bredenkamp Observatory, Bremen\n")
    file.write("L66  20.811220.845577-0.532615MeerLICHT-1, Sutherland\n")
    file.write("L67  37.798890.561057+0.825033Cherkizovo Observatory, Moscow Oblast\n")
    file.write("L68  25.536830.830048-0.555874PESCOPE, Port Elizabeth\n")
    file.write("L69  28.2142 0.90084 -0.43323 LaCaille Observatory, Pretoria\n")
    file.write("L70  15.923330.698145+0.713600Zvjezdarnica Graberje, Zagreb\n")
    file.write("L71  38.5839 0.71089 +0.70101 Vedrus Observatory, Azovskaya\n")
    file.write("L72  38.6928 0.55979 +0.82589 Melezhy Astrophoto Observatory\n")
    file.write("L73  11.261830.724459+0.687083Beato Ermanno Observatory, Impruneta\n")
    file.write("L74  14.211090.757212+0.651048AstroColauri, Naples\n")
    file.write("L75  26.463940.527292+0.846853Tartu Observatory of Tartu University\n")
    file.write("L76  39.651610.683530+0.727483Nomad Observatory, Kochevanchik\n")
    file.write("L77  39.820250.678927+0.731765RDSS, Kovalevka\n")
    file.write("L78  14.7800 0.75943 +0.64844 San Marco Observatory, Salerno\n")
    file.write("L79  18.220390.696477+0.715222BOSZA Observatory, Szalanta\n")
    file.write("L80  18.0175 0.91802 -0.39574 SpringBok Observatory, Tivoli\n")
    file.write("L81  16.361690.919631-0.392204Skygems Namibia Remote Observatory\n")
    file.write("L82 352.679500.775227+0.629726Crow Observatory, Portalegre\n")
    file.write("L83 356.222310.791355+0.609451UJA Observatory, Jaen\n")
    file.write("L84  41.279890.695443+0.716182Kairos Observatory, Letnik\n")
    file.write("L85  15.863250.766873+0.639830BiAnto Observatory, Lauria\n")
    file.write("L86   9.2631 0.71140 +0.70062 Giordano Bruno Observatory, Brallo\n")
    file.write("L87  16.361890.919631-0.392204Moonbase South Observatory, Hakos\n")
    file.write(
        "L88  16.5422 0.77721 +0.62746 Stazione Astronomica Le Pleiadi, Pantane\n"
    )
    file.write("L89  11.144390.722146+0.689445PAO, Prato\n")
    file.write("L90  15.979490.784120+0.618560ABObservatory, Rosarno\n")
    file.write("L91  13.8078 0.74776 +0.66189 Antares MTM Observatory, S. Donato\n")
    file.write("L92  16.002110.781423+0.621967San Costantino\n")
    file.write("L93   1.772210.752844+0.65601 Garraf Observatory, Sant Pere de Ribes\n")
    file.write("L94 354.145610.728187+0.683146Observatorio MOMA, Oviedo\n")
    file.write("L95 358.951590.793164+0.607000Observatorio Astronomico de Cartagena\n")
    file.write("L96  44.2745 0.76340 +0.64416 ISON-Byurakan Observatory\n")
    file.write("L97 357.991610.624666+0.778298Castle Fields Observatory, Calne\n")
    file.write(
        "L98 357.434250.789394+0.612232La Sagra Observatory, Puebla de Don Fadrique\n"
    )
    file.write("L99  30.602810.635913+0.769201Novosilky\n")
    file.write("M02   0.863860.754439+0.654271Astropriorat Observatory\n")
    file.write("M03   2.258220.750568+0.658591Badalona Boreal\n")
    file.write("M04   1.4256 0.74764 +0.66207 Pujalt Observatory, Barcelona\n")
    file.write("M05   1.331610.729979+0.681267Observatoire de la Nine, Canens\n")
    file.write("M06   0.743810.744130+0.665983PeLe's Observatory, Ager\n")
    file.write("M07  10.294470.594202+0.801641Siek\n")
    file.write("M08   4.0381 0.62786 +0.77573 CHON, Stekene\n")
    file.write("M09   5.600940.630164+0.773882Observatory Gromme - Oudsbergen\n")
    file.write("M10   6.854110.724305+0.687343CPF Observatory, St Vallier de Thiey\n")
    file.write("M11   5.647180.720589+0.691192Novaastro Observatory, Banon\n")
    file.write("M13   7.742500.662866+0.746267Lucie Berger Observatory, Strasbourg\n")
    file.write("M14   8.789390.699981+0.711832Schiaparelli Gallarate Station\n")
    file.write("M15   9.1506 0.70039 +0.71142 Virgo Oservatory, Seveso\n")
    file.write("M16   9.773190.719401+0.692358Osservatorio Il Coreggiolo\n")
    file.write("M17   9.809220.719163+0.692525SN1572 Tycho Observatory, La Spezia\n")
    file.write("M18  11.839390.639618+0.766239Koeditz\n")
    file.write("M19  13.883270.709976+0.701881Osservatorio Explorer, Pula\n")
    file.write("M20  13.011690.690044+0.721515Polse di Cougnes Observatory, Zuglio\n")
    file.write(
        "M21  16.361440.919630-0.392206Schiaparelli Southern Observatory, Hakos\n"
    )
    file.write("M22  20.810590.845564-0.532612ATLAS South Africa, Sutherland\n")
    file.write("M23  16.603500.679955+0.730852ELTE Gothard Observatory, Szombathely\n")
    file.write("M24  16.200500.787195+0.614649La Macchina del Tempo, Ardore Marina\n")
    file.write("M25  23.8283 0.47849 +0.87517 Einarin Observatory, Tampere\n")
    file.write("M26  11.134940.723236+0.688304Zen Observatory, Scandicci\n")
    file.write("M27  10.7175 0.72743 +0.68399 Elijah Observatory, Lajatico\n")
    file.write(
        "M28  20.810640.845568-0.532607Lesedi Telescope-SAAO Observatory, Sutherland\n"
    )
    file.write("M29  12.248640.718724+0.692984O.M.Ni.A. Observatory, Cesena\n")
    file.write("M30  25.620000.700380+0.711516Zeta Aquarii Observatory, Brasov\n")
    file.write("M31  26.212810.490130+0.868745Ursa Havaintokeskus,  Artjarvi\n")
    file.write("M32  22.709190.665464+0.743964Sunny Transcarpathian, Mukachevo\n")
    file.write("M33  34.763340.861632+0.506111OWL-Net, Mitzpe Ramon\n")
    file.write("M34  17.273630.665591+0.743936AGO70, Astronomical Observatory, Modra\n")
    file.write("M35  26.616690.688654+0.722734PS Observatory, Parjol\n")
    file.write("M36  13.796470.699732+0.712090Opicina, Trieste\n")
    file.write("M37  13.912430.696956+0.714892Astronomsko drustvo Nanos, Ajdovscina\n")
    file.write("M38  21.767190.671089+0.738923Harsona Observatory, Nyiregyhaza\n")
    file.write("M39  22.958880.760013+0.647750AUTH Observatory, Thessaloniki\n")
    file.write("M40  31.827080.867372+0.496143OSTS-NRIAG, Kottamia\n")
    file.write("M41  39.258270.930706+0.364567Jeddah\n")
    file.write("M42  54.6708 0.90990 +0.41343 Emirates Observatory, Al Rahba\n")
    file.write("M43  54.684780.912805+0.407034Al Sadeem Observatory, Abu Dhabi\n")
    file.write("M44  54.920310.912502+0.407722Al-Khatim Observatory, Abu Dhabi\n")
    file.write(
        "M45  25.7689 0.69761 +0.71420 Starhopper Observatory, Sfantu Gheorghe\n"
    )
    file.write("M46  55.450330.905280+0.423399Althuraya Astronomy Center, Dubai\n")
    file.write("M47  55.462050.904763+0.424484Sharjah Observatory, Sharjah\n")
    file.write(
        "M48  15.092220.794277+0.605535GAC - Via L. Sturzo Observatory, Catania\n"
    )
    file.write("M49  16.361720.919630-0.392206IAS Remote Observatory, Hakos\n")
    file.write("M50  11.563750.738663+0.671862Virtual Telescope Project, Manciano\n")
    file.write("M51   9.226970.655500+0.752709Robert Mayer Sternwarte, Heilbronn\n")
    file.write("M52   8.578500.758941+0.649052Sassari\n")
    file.write("M53  10.282190.585977+0.807623CAS Observatory, Preetz\n")
    file.write("M54   7.077810.725140+0.686335Observatoire Albireo de Biot\n")
    file.write("M55  19.987000.656685+0.751814Luckystar Observatory, Vazec\n")
    file.write("M56   9.174830.700833+0.710985Varedo\n")
    file.write("M57  14.020200.790651+0.610701Wide-field Mufara Telescope, Isnello\n")
    file.write("M58  16.361330.919630-0.392207VdS Remote Observatory, Hakos\n")
    file.write("M59   7.228830.680334+0.730616Rondchamp Observatory, Reconvilier\n")
    file.write("M60  11.325540.717411+0.694492Virgil Observatory, Loiano\n")
    file.write("M61   6.585810.624893+0.778108Observatory Moers Kapellen\n")
    file.write("M62   7.134170.679741+0.731214Lajoux Observatory\n")
    file.write("M63  18.369690.768886+0.637286RPF Observatory, Gagliano del Capo\n")
    file.write("M90  65.4286 0.54672 +0.83452 Chervishevo\n")
    file.write("N27  73.7253 0.57847 +0.81298 Omsk-Yogik Observatory\n")
    file.write("N30  74.3694 0.85369 +0.51909 Zeds Astronomical Observatory, Lahore\n")
    file.write("N31  74.444220.853321+0.519690Eden Astronomical Observatory, Lahore\n")
    file.write("N42  76.971810.732126+0.679511Tien-Shan Astronomical Observatory\n")
    file.write(
        "N43  77.1167 0.16712 -0.98328 Plateau Observatory for Dome A, Kunlun Station\n"
    )
    file.write("N44  77.139310.785023+0.617693Shache Station, Langan Village\n")
    file.write(
        "N50  78.963830.842176+0.538692Himalayan Chandra Telescope, IAO, Hanle\n"
    )
    file.write("N51  78.964610.842178+0.538687GROWTH India Telescope, IAO, Hanle\n")
    file.write("N55  80.026230.846497+0.532089Beimian Tianwentai, Ali, Tibet\n")
    file.write("N56  80.026750.846503+0.532073Jiama'erdeng Tianwentai, Ali, Tibet\n")
    file.write("N82  85.954940.641844+0.764450Multa Observatory\n")
    file.write("N83  86.235040.749549+0.659927LW-1, NAOC-Korla\n")
    file.write("N86  87.178520.727070+0.684719Xingming Observatory-KATS, Nanshan\n")
    file.write("N87  87.175030.727076+0.684720Nanshan Station, Xinjiang Observatory\n")
    file.write("N88  87.173220.727098+0.684697Xingming Observatory #3, Nanshan\n")
    file.write("N89  87.179060.727107+0.684682Xingming Observatory #2, Nanshan\n")
    file.write(
        "O02  90.526140.866434+0.498958Galaxy Tibet YBJ Observatory,Yangbajing\n"
    )
    file.write("O17  93.886690.783127+0.620730Purple Mountain Observatory, Lenghu-1\n")
    file.write("O18  93.895220.782966+0.621021WFST, Lenghu\n")
    file.write("O37  98.485530.948521+0.316891TRT-NEO, Chiangmai\n")
    file.write("O43  99.781110.994005+0.109127Observatori Negara, Langkawi\n")
    file.write("O44 100.0310 0.89435 +0.44698 Lijiang Station, Yunnan Observatories\n")
    file.write("O45 100.032610.894444+0.446808Yunnan-HK Observatory, Gaomeigu\n")
    file.write("O46 100.226640.875738+0.482415Daocheng Glacier Observatory\n")
    file.write("O47 101.134150.902535+0.429998Yunling Observatory, Yunnan\n")
    file.write(
        "O48 101.181540.903223+0.428442Purple Mountain Observatory, Yaoan (0.8-m)\n"
    )
    file.write(
        "O49 101.181110.903206+0.428474Purple Mountain Observatory, Yaoan Station\n"
    )
    file.write("O50 101.439420.998617+0.052565Hin Hua Observatory, Klang\n")
    file.write("O51 101.278690.975556+0.218996Akin Observatory, Rayong\n")
    file.write("O68 105.330900.793121+0.607347LW-2, NAOC-Zhongwei\n")
    file.write("O72 106.334760.672017+0.738399OWL-Net, Songino\n")
    file.write("O75 107.051800.672284+0.738151ISON-Hureltogoot Observatory\n")
    file.write("O85 109.213000.826583+0.561181LiShan Observatory, Lintong\n")
    file.write(
        "P07 114.089870.928304-0.370597Space Surveillance Telescope, HEH Station\n"
    )
    file.write("P18 116.610830.757010+0.651328Birch Forest Observatory, LaBaGouMen\n")
    file.write("P21 117.281460.850540-0.5242466R-AUS1, Youndegin\n")
    file.write("P22 117.575880.762782+0.644702LW-3, NAOC-Xinglong\n")
    file.write(
        "P25 118.312740.910976+0.411089Kinmen Educational Remote Observatory, Jincheng\n"
    )
    file.write("P30 119.597080.862775+0.504181Jiangnantianchi Observatory, Anji\n")
    file.write("P31 119.597360.862772+0.504189Starlight Observatory, Tianhuangping\n")
    file.write("P34 120.320310.855040+0.516826Lvye Observatory, Suzhou\n")
    file.write("P35 120.556990.913398+0.405722Cuteip Remote Observatory, Changhua\n")
    file.write("P36 120.626690.855207+0.516553ULTRA Observatory,Suzhou\n")
    file.write(
        "P37 120.639720.912980+0.406672HuiWen High School Observatory, Taichung City\n"
    )
    file.write("P40 121.539580.905916+0.422185Chinese Culture University, Taipei\n")
    file.write("P48 123.324030.258064-0.963413ASTEP, Concordia Station\n")
    file.write("P61 126.330470.722664+0.688958Jilin Observatory\n")
    file.write("P63 126.847500.817778+0.573621GSA Observatory, Gwangju\n")
    file.write("P64 127.004890.796371+0.602805GSHS Observatory, Suwon\n")
    file.write("P65 127.375680.805889+0.590124OWL-Net, Daedeok\n")
    file.write(
        "P66 127.446750.824763+0.563603Deokheung Optical Astronomy Observatory\n"
    )
    file.write(
        "P67 127.7415 0.79040 +0.61057 Kangwon National University Observatory\n"
    )
    file.write(
        "P71 128.761080.815026+0.577520Miryang Arirang Astronomical Observatory\n"
    )
    file.write("P72 128.975950.808423+0.586939OWL-Net, Mt. Bohyun\n")
    file.write("P73 129.0820 0.81744 +0.57412 BSH Byulsem Observatory, Busan\n")
    file.write("P87 132.094190.830358+0.555374Hirao Observatory, Yamaguchi\n")
    file.write(
        "P93 133.544330.823371+0.565729Space Tracking and Communications Center, JAXA\n"
    )
    file.write("Q02 135.493440.825315+0.562809Sakai Observatory, Osaka\n")
    file.write("Q06 136.495470.816116+0.575990Tarui Observatory, Tarui\n")
    file.write("Q10 137.329440.821623+0.568142Toyokawa Observatory\n")
    file.write("Q11 137.520690.820236+0.570158Shinshiro\n")
    file.write("Q12 137.825360.805147+0.591292Nagano Observatory\n")
    file.write("Q19 139.4390 0.81430 +0.57852 Machida\n")
    file.write("Q21 139.853350.804747+0.591654Southern Utsunomiya\n")
    file.write("Q23 140.3864 0.79654 +0.60264 Sukagawa\n")
    file.write("Q24 140.523500.810991+0.583108Katori\n")
    file.write(
        "Q33 142.482780.715989+0.695814Nayoro Observatory, Hokkaido University\n"
    )
    file.write("Q38 143.5506 0.81654 -0.57538 Swan Hill\n")
    file.write(
        "Q54 147.287720.739290-0.671278Harlingten Telescope, Greenhill Observatory\n"
    )
    file.write("Q55 149.061420.855643-0.516191SkyMapper, Siding Spring\n")
    file.write("Q56 148.976420.821480-0.568478Heaven's Mirror Observatory, Yass\n")
    file.write(
        "Q57 149.061730.855649-0.516175Korea Microlensing Telescope Network-SSO\n"
    )
    file.write("Q58 149.070850.855632-0.516199Siding Spring-LCO Clamshell #1\n")
    file.write("Q59 149.070810.855626-0.516197Siding Spring-LCO Clamshell #2\n")
    file.write("Q60 149.069000.855626-0.516198ISON-SSO Observatory, Siding Spring\n")
    file.write("Q61 149.0619 0.85564 -0.51618 PROMPT, Siding Spring\n")
    file.write("Q62 149.064420.855629-0.516206iTelescope Observatory, Siding Spring\n")
    file.write("Q63 149.070640.855632-0.516202Siding Spring-LCO A\n")
    file.write("Q64 149.070780.855632-0.516202Siding Spring-LCO B\n")
    file.write("Q65 149.193130.855519-0.516201Warrumbungle Observatory\n")
    file.write("Q66 149.064250.855627-0.516205Siding Spring-Janess-G, JAXA\n")
    file.write("Q67 149.492330.835816-0.547369JBL Observatory, Bathurst\n")
    file.write("Q68 150.337420.832917-0.551813Blue Mountains Observatory, Leura\n")
    file.write("Q69 150.449330.832777-0.551945Hazelbrook\n")
    file.write("Q70 150.500440.919153-0.392623Glenlee Observatory, Glenlee\n")
    file.write("Q78 152.947890.886807-0.460619Woogaroo Observatory, Forest Lake\n")
    file.write("Q79 152.8481 0.88871 -0.45696 Samford Valley Observatory\n")
    file.write("Q80 153.2160 0.88762 -0.45904 Birkdale\n")
    file.write("Q81 153.096220.893194-0.448181Caloundra West\n")
    file.write("R56 170.483890.720473-0.691324Scott Street Observatory, Lake Tekapo\n")
    file.write("R57 170.472780.720489-0.691309Aorangi Iti Observatory, Lake Tekapo\n")
    file.write("R58 170.490390.697579-0.714138Beverly-Begg Observatory, Dunedin\n")
    file.write("R65 172.349810.726556-0.684830R. F. Joyce Observatory, Christchurch\n")
    file.write("R66 172.587610.726587-0.684777Mooray Observatory, Christchurch\n")
    file.write("T03 203.742470.936240+0.351538Haleakala-LCO Clamshell #3\n")
    file.write("T04 203.742490.936241+0.351538Haleakala-LCO OGG B #2\n")
    file.write("T05 203.742990.936235+0.351547ATLAS-HKO, Haleakala\n")
    file.write("T07 204.423870.943290+0.332467ATLAS-MLO Auxiliary Camera, Mauna Loa\n")
    file.write("T08 204.423950.943290+0.332467ATLAS-MLO, Mauna Loa\n")
    file.write("T09 204.523980.941706+0.337237Subaru Telescope, Maunakea\n")
    file.write("T10 204.522410.941706+0.337212Submillimeter Array, Maunakea (SMA)\n")
    file.write(
        "T11 204.530360.941731+0.337198United Kingdom Infrared Telescope, Maunakea\n"
    )
    file.write(
        "T12 204.530570.941729+0.337199University of Hawaii 88-inch telescope, Maunakea\n"
    )
    file.write(
        "T13 204.527710.941691+0.337263NASA Infrared Telescope Facility, Maunakea\n"
    )
    file.write(
        "T14 204.531130.941714+0.337236Canada-France-Hawaii Telescope, Maunakea\n"
    )
    file.write("T15 204.530940.941727+0.337214Gemini North Observatory, Maunakea\n")
    file.write(
        "T16 204.525700.941703+0.337250W. M. Keck Observatory, Keck 1, Maunakea\n"
    )
    file.write(
        "T17 204.525800.941700+0.337256W. M. Keck Observatory, Keck 2, Maunakea\n"
    )
    file.write("T35 210.390200.953686-0.299837Astronomical Society of Tahiti\n")
    file.write("U52 237.451110.749240+0.660270Shasta Valley Observatory, Grenada\n")
    file.write("U53 237.1603 0.70274 +0.70909 Murray Hill Observatory, Beaverton\n")
    file.write("U54 237.312860.782952+0.620081Hume Observatory, Santa Rosa\n")
    file.write("U55 237.414560.653977+0.753984Golden Ears Observatory, Maple Ridge\n")
    file.write("U56 237.869170.795044+0.604511Palo Alto\n")
    file.write("U57 237.841280.795776+0.603616Black Mountain Observatory, Los Altos\n")
    file.write("U63 239.194560.681217+0.729770Burnt Tree Hill Observatory, Cle Elum\n")
    file.write("U64 239.461510.683272+0.727821CWU-Lind Observatory, Ellensburg\n")
    file.write("U65 239.459830.683247+0.727841CWU Observatory, Ellensburg\n")
    file.write("U67 240.203580.776325+0.628595Jack C. Davis Observatory, Carson City\n")
    file.write(
        "U68 240.587010.799040+0.599620JPL SynTrack Robotic Telescope, Auberry\n"
    )
    file.write("U69 240.5870 0.79904 +0.59962 iTelescope SRO Observatory, Auberry\n")
    file.write("U70 240.5869 0.79904 +0.59962 RASC Observatory, Alder Springs\n")
    file.write("U71 241.3633 0.82520 +0.56305 AHS Observatory, Castaic\n")
    file.write("U72 241.460000.828150+0.558687Tarzana\n")
    file.write("U73 241.6172 0.83164 +0.55346 Redondo Beach\n")
    file.write(
        "U74 240.587200.799040+0.599619JPL SynTrack Robotic Telescope 2, Auberry\n"
    )
    file.write("U75 242.183660.833735+0.550383Newport Beach\n")
    file.write("U76 242.1279 0.82855 +0.55810 Maury Lewin Observatory, Glendora\n")
    file.write("U77 242.9181 0.84002 +0.54076 Rani Observatory, San Diego\n")
    file.write("U78 242.8449 0.82758 +0.55989 Cedar Glen Observatory\n")
    file.write("U79 242.791870.838837+0.542598Cosmos Research Center, Encinitas\n")
    file.write("U80 243.6151 0.82737 +0.56004 CS3-DanHenge Observatory, Landers\n")
    file.write("U81 243.615140.827367+0.560037CS3-Trojan Station, Landers\n")
    file.write("U82 243.615190.827368+0.560036CS3-Palmer Divide Station, Landers\n")
    file.write("U83 243.573110.841238+0.53938 Mount Laguna Observatory\n")
    file.write(
        "U93 246.287610.791740+0.609209Skygems Dreamscope Utah, Beryl Junction\n"
    )
    file.write("U94 246.302500.792006+0.608864iTelescope Observatory, Beryl Junction\n")
    file.write(
        "U96 246.686000.579007+0.812698Athabasca University Geophysical Observatory\n"
    )
    file.write(
        "U97 248.332920.818306+0.573452JPL SynTrack Robotic Telescope 3, Flagstaff\n"
    )
    file.write("U98 249.743000.849529+0.526090NAC Observatory, Benson\n")
    file.write("V00 248.399810.849456+0.526492Kitt Peak-Bok\n")
    file.write("V01 248.239110.762243+0.645493Mountainville Observatory, Alpine\n")
    file.write("V02 248.057940.835743+0.547377Command Module, Tempe\n")
    file.write("V03 248.3314 0.79889 +0.59979 Big Water\n")
    file.write("V04 248.463310.819378+0.571927FRoST, Anderson Mesa\n")
    file.write(
        "V05 248.631950.836631+0.546101Rusty Mountain Observatory, Gold Canyon\n"
    )
    file.write("V06 249.267450.845317+0.533211Catalina Sky Survey-Kuiper\n")
    file.write(
        "V07 249.1219 0.85208 +0.52234 Whipple Observatory, Mount Hopkins-PAIRITEL\n"
    )
    file.write("V08 249.339000.848249+0.528126Mountain Creek Ranch, Vail\n")
    file.write("V09 249.742020.849537+0.526080Moka Observatory, Benson\n")
    file.write("V10 248.327720.818623+0.572977Sierra Sinagua Observatory, Flagstaff\n")
    file.write("V11 249.211190.847025+0.530011Saguaro Observatory, Tucson\n")
    file.write("V12 249.398190.852110+0.522050Elgin\n")
    file.write("V13 248.782780.762335+0.645641Little Moose Observatory, Timber Lakes\n")
    file.write(
        "V14 248.783360.762292+0.645691Moose Springs Observatory, Timber Lakes\n"
    )
    file.write("V15 249.210690.845110+0.533602OWL-Net, Mt. Lemmon\n")
    file.write("V16 251.102880.849510+0.526194Dark Sky New Mexico, Animas\n")
    file.write("V17 248.983190.845476+0.532429Leo Observatory, Tucson\n")
    file.write("V18 249.6181 0.85776 +0.51308 MASTER-OAGH Observatory, Sonora\n")
    file.write("V19 251.790860.841371+0.539217Whiskey Creek Observatory\n")
    file.write("V20 251.778220.827004+0.560943Killer Rocks Observatory, Pie Town\n")
    file.write("V21 251.102310.849511+0.526188Cewanee Observatory at DSNM\n")
    file.write("V22 251.815500.827009+0.560941Insight Remote Observatory, Pie Town\n")
    file.write("V23 252.764060.828722+0.558332FOAH Observatory, Magdalena\n")
    file.write(
        "V24 250.484030.850261+0.525020Sonoran Desert Skies Observatory, Pearce\n"
    )
    file.write(
        "V25 253.301940.846331+0.531305Tortugas Mountain Observatory, Las Cruces\n"
    )
    file.write("V26 253.390200.911283+0.410639UAS-ISON Observatory, Cosala\n")
    file.write("V27 253.718190.811354+0.583180North Mesa Observatory, Los Alamos\n")
    file.write("V28 254.346470.817018+0.575271Deep Sky West Observatory, Rowe\n")
    file.write("V29 254.266600.840062+0.541466Tzec Maun Cloudcroft Facility\n")
    file.write("V30 254.471050.840710+0.540313Heaven on Earth Observatory, Mayhill\n")
    file.write("V31 254.4750 0.84061 +0.54046 Hazardous Observatory, Mayhill\n")
    file.write("V32 254.471310.840709+0.540308Canvas View New Mexico Skies, Mayhill\n")
    file.write("V33 254.720390.806382+0.590114Finlaystone Observatory, Angel Fire\n")
    file.write("V34 255.369920.778401+0.626222Black Forest\n")
    file.write(
        "V35 255.918810.861839+0.506046Deep Sky Observatory Collaborative, Pier 5\n"
    )
    file.write("V36 255.617420.843042+0.536333The Ranch Observatory, Lakewood\n")
    file.write("V37 255.984830.861053+0.507428McDonald Observatory-LCO ELP\n")
    file.write(
        "V38 255.984930.861051+0.507431McDonald Observatory-LCO ELP Aqawan A #1\n"
    )
    file.write("V39 255.984520.861051+0.507430McDonald Observatory-LCO ELP B\n")
    file.write(
        "V40 255.918730.861839+0.506046Divine Creation Observatory, Fort Davis\n"
    )
    file.write("V41 256.725780.719992+0.691890Rapid City\n")
    file.write("V42 254.474720.840614+0.540448Dimension Point, Mayhill\n")
    file.write("V54 259.692190.936737+0.349756Observatoire LAURIER, El Marques\n")
    file.write("V58 260.734970.868735+0.493762Medina Dome, Medina\n")
    file.write("V59 261.0734 0.86642 +0.49781 Millwood Observatory, Comfort\n")
    file.write("V60 261.094730.862140+0.505126Putman Mountain Observatory\n")
    file.write("V61 261.057100.858216+0.511725Shed of Science South, Pontotoc\n")
    file.write("V62 261.056610.858216+0.511726Live Oak Observatory, Pontotoc\n")
    file.write("V63 261.057280.858219+0.511721Tara Observatory, Cherokee\n")
    file.write("V70 263.335720.870056+0.491332Starry Night Observatory, Columbus\n")
    file.write("V72 263.890110.752696+0.656235JDP Observatory, Omaha\n")
    file.write("V74 264.156890.869320+0.492598Katy Observatory, Katy\n")
    file.write("V78 265.107800.700141+0.711688Spirit Marsh Observatory. Sauk Centre\n")
    file.write("V81 265.7604 0.80902 +0.58590 Fayetteville\n")
    file.write("V83 266.257280.781733+0.621590Rolling Hills Observatory, Warrensburg\n")
    file.write("V86 266.8927 0.78221 +0.62099 Rattle Snake Observatory, Sedalia\n")
    file.write("V88 267.428110.820618+0.569618River Ridge Observatory, Conway\n")
    file.write("V93 268.616110.759765+0.648058Pin Oak Observatory, Fort Madison\n")
    file.write(
        "V94 268.661690.759876+0.647933Cherokeeridge Observatory, Fort Madison\n"
    )
    file.write("W04 271.009440.761606+0.645927Mark Evans Observatory, Bloomington\n")
    file.write("W08 271.883310.747086+0.662545Jimginny Observatory, Naperville\n")
    file.write("W09 272.147530.752886+0.655985Willowed Plains Observatory, Manteno\n")
    file.write(
        "W11 272.6247 0.75272 +0.65618 Northwest Indiana Robotic Telescope, Lowell\n"
    )
    file.write("W14 273.245110.821914+0.567774Harvest\n")
    file.write("W15 273.190830.810875+0.583314Wayne Observatory, Franklin\n")
    file.write("W16 273.768690.822976+0.566292Pleasant Groves Observatory\n")
    file.write("W17 273.771220.765700+0.641103Arrowhead, Sheridan\n")
    file.write("W18 274.249620.767039+0.639505Red Fox Observatory, Pendleton\n")
    file.write("W19 274.372830.740783+0.669559Kalamazoo\n")
    file.write("W22 275.004470.844595+0.533635WestRock Observatory, Columbus\n")
    file.write("W23 275.380190.772786+0.632594Hevonen Farm Observatory, Oxford\n")
    file.write("W24 275.238170.722574+0.689025Shamrock Banks Observatory, Clare\n")
    file.write("W25 275.635060.776417+0.628165RMS Observatory, Cincinnati\n")
    file.write("W28 276.3883 0.83011 +0.55581 Ex Nihilo Observatory, Winder\n")
    file.write("W29 276.9939 0.76659 +0.64004 Adena Brook Observatory, Columbus\n")
    file.write(
        "W30 276.771170.838735+0.542749Georgia College Observatory, Milledgeville\n"
    )
    file.write("W31 277.237360.834226+0.549613Deerlick Observatory, Crawfordville\n")
    file.write("W32 277.237500.834222+0.549619Crawfordville Observatory\n")
    file.write("W33 277.834510.819315+0.571499Transit Dreams Observatory, Campobello\n")
    file.write("W34 277.8453 0.81784 +0.57360 Squirrel Valley Observatory, Columbus\n")
    file.write("W35 278.039100.856610+0.514230Buffalo Creek Observatory, Nahunta\n")
    file.write("W38 278.585310.807479+0.588163Dark Sky Observatory, Boone\n")
    file.write("W42 279.465690.885511+0.463056Mind's Eye Observatory, Vero Beach\n")
    file.write("W46 280.411920.818614+0.572448Foxfire Village\n")
    file.write("W48 280.887000.811693+0.582156BKH Observatory, Chapel Hill\n")
    file.write("W49 281.067570.778794+0.625380CBA-MM Observatory, Mountain Meadows\n")
    file.write("W50 281.254040.813127+0.580167Apex\n")
    file.write(
        "W52 283.514190.778335+0.625736US Naval Academy Hopper Hall Observatory\n"
    )
    file.write("W53 282.315240.771140+0.634559Hagerstown\n")
    file.write(
        "W54 282.289440.785431+0.616890Mark Slade Remote Observatory, Wilderness\n"
    )
    file.write("W55 282.583890.773703+0.631447Natelli Observatory, Frederick\n")
    file.write("W56 282.525830.773143+0.632153Pineapple Observatory, Frederick\n")
    file.write("W57 289.260940.873480-0.486002ESA TBT La Silla Observatory\n")
    file.write("W58 283.149640.777667+0.626574ALPHA Observatory, South Laurel\n")
    file.write("W59 284.107580.757005+0.651302The Dark Side Observatory, Weatherly\n")
    file.write("W60 286.366260.995574+0.097155AstroExplor Observatory, Tinjaca\n")
    file.write("W61 283.744920.713380+0.698447Leeside Observatory, Elgin\n")
    file.write(
        "W62 284.137610.758729+0.649276Comet Hunter Observatory2, New Ringgold\n"
    )
    file.write("W63 284.309580.996767+0.082976Observatorio Astronomico UTP, Pereira\n")
    file.write("W64 285.270040.768364+0.637863Red Lion Observatory, Southampton Twsp\n")
    file.write("W65 284.791690.697761+0.713966Observatoire GOZ, Montpellier\n")
    file.write("W66 285.053810.756278+0.652109SVH Observatory, Blairstown\n")
    file.write(
        "W67 285.102110.759453+0.648444Paul Robinson Observatory, Voorhees State Park\n"
    )
    file.write("W68 289.235020.862845-0.504269ATLAS Chile, Rio Hurtado\n")
    file.write("W69 285.985000.759912+0.647855OLPH Observatory, Brooklyn\n")
    file.write("W70 285.913860.698475+0.713264Loose Goose Observatory, Saint-Jerome\n")
    file.write("W71 285.992970.717404+0.694456Rand II Observatory, Lake Placid\n")
    file.write("W72 286.8211 0.75302 +0.65580 Trumbull Observatory, Trumbull\n")
    file.write(
        "W73 289.321560.957949-0.287797Observatorio Astronomico de Moquegua, Carumas\n"
    )
    file.write("W74 289.262450.873451-0.486040Danish Telescope, La Silla\n")
    file.write("W75 289.609440.910001-0.414150SPECULOOS-South Observatory, Paranal\n")
    file.write("W76 289.236950.862826-0.504288CHILESCOPE Observatory, Rio Hurtado\n")
    file.write("W77 287.4010 0.75196 +0.65702 Skyledge Observatory, Killingworth\n")
    file.write("W78 288.883250.739859+0.670509Clay Telescope, Harvard University\n")
    file.write("W79 289.195350.865587-0.499763Cerro Tololo-LCO Aqawan B #1\n")
    file.write("W80 288.7678 0.74138 +0.66885 Westwood\n")
    file.write(
        "W81 288.999670.724557+0.686948Nebula Knoll Observatoy, East Wakefield\n"
    )
    file.write("W82 288.878040.736419+0.674274Mendel Observatory, Merrimack College\n")
    file.write("W83 288.697470.740821+0.669461Whitin Observatory, Wellesley\n")
    file.write("W84 289.193580.865572-0.499793Cerro Tololo-DECam\n")
    file.write("W85 289.195190.865591-0.499760Cerro Tololo-LCO A\n")
    file.write("W86 289.195330.865592-0.499759Cerro Tololo-LCO B\n")
    file.write("W87 289.195320.865591-0.499761Cerro Tololo-LCO C\n")
    file.write("W88 289.465700.837136-0.545574Slooh.com Chile Observatory, La Dehesa\n")
    file.write("W89 289.195330.865589-0.499764Cerro Tololo-LCO Aqawan A #1\n")
    file.write(
        "W90 289.058140.732740+0.678229Phillips Exeter Academy Grainger Observatory\n"
    )
    file.write("W91 289.602570.910007-0.414148VHS-VISTA, Cerro Paranal\n")
    file.write("W92 290.673570.850987-0.524150MASTER-OAFA Observatory, San Juan\n")
    file.write(
        "W93 289.196000.865589-0.499755Korea Microlensing Telescope Network-CTIO\n"
    )
    file.write("W94 291.820190.921646-0.387713MAP, San Pedro de Atacama\n")
    file.write(
        "W95 291.820120.921639-0.387712Observatorio Panameno, San Pedro de Atacama\n"
    )
    file.write("W96 291.820060.921637-0.387717CAO, San Pedro de Atacama (since 2013)\n")
    file.write(
        "W97 291.820240.921638-0.387716Atacama Desert Observatory, San Pedro de Atacama\n"
    )
    file.write(
        "W98 291.820300.921639-0.387712Polonia Observatory, San Pedro de Atacama\n"
    )
    file.write("W99 291.820150.921638-0.387716SON, San Pedro de Atacama Station\n")
    file.write("X00 292.601250.910349-0.413802Observatorio Astronomico Tolar\n")
    file.write("X01 289.235020.862846-0.504270Observatory Hurtado, El Sauce\n")
    file.write("X02 289.235170.862833-0.504255Telescope Live, El Sauce\n")
    file.write("X03 289.203610.862286-0.505209Observatoire SADR, Poroto\n")
    file.write("X04 291.567470.664264+0.745000MCD Observatory, Saint-Anaclet\n")
    file.write(
        "X05 289.250580.864981-0.500958Simonyi Survey Telescope, Rubin Observatory\n"
    )
    file.write("X06 289.146490.862374-0.505110Skygems Chile, Rio Hurtado\n")
    file.write("X07 289.146390.862374-0.505109iTelescope Deep Sky Chile, Rio Hurtado\n")
    file.write("X08 289.235000.862852-0.504255ShAO Chile station, El Sauce\n")
    file.write("X09 289.146700.862375-0.505108Deep Random Survey, Rio Hurtado\n")
    file.write("X10 291.820400.921644-0.387717OVTLN, San Pedro de Atacama\n")
    file.write("X11 289.596040.909953-0.414324VLT Survey Telescope, Paranal\n")
    file.write("X12 295.712000.803430-0.593455Observatorio Los Cabezones\n")
    file.write("X13 295.4498 0.85269 -0.52103 Observatorio Remoto Bosque Alegre\n")
    file.write("X14 295.832220.854475-0.517879Observatorio Orbis Tertius, Cordoba\n")
    file.write("X15 291.820530.921647-0.387711ABYO, San Pedro de Atacama\n")
    file.write("X16 293.8497 0.95511 -0.29667 Astronomia Sigma Octante, Cochabamba\n")
    file.write("X31 299.479340.850485-0.524263Galileo Galilei Observatory, Oro Verde\n")
    file.write("X33 299.990390.998647-0.051941OARU, Manaus\n")
    file.write("X38 301.137110.825648-0.562299Observatorio Pueyrredon, La Lonja\n")
    file.write("X39 301.1378 0.82615 -0.56158 Observatorio Antares, Pilar\n")
    file.write("X40 301.616890.822572-0.566762Cielos de Banfield, Banfield\n")
    file.write("X50 303.824190.821025-0.568999Observatorio Astronomico de Montevideo\n")
    file.write("X57 305.406260.903659-0.426885Polo Astronomico CMF,Foz do Iguacu\n")
    file.write("X60 306.425560.895232-0.444317Guaraciaba Observatory\n")
    file.write("X70 308.433220.931623-0.362375Observatorio OATU, Tupi Paulista\n")
    file.write("X72 308.878890.868775-0.493560Waccobs, Sao Leopoldo\n")
    file.write("X74 309.494220.931569-0.362525Observatorio Campo dos Amarais\n")
    file.write(
        "X77 309.924750.900184-0.434346Centro Astron. Nevoeiro, Antonio Olinto\n"
    )
    file.write("X87 312.0889 0.96218 -0.27210 Dogsheaven Observatory, Brasilia\n")
    file.write("X88 312.491310.918012-0.395458Observatorio Adhara, Sorocaba\n")
    file.write("X89 312.217860.962401-0.271311Rocca Observatory, Brasilia\n")
    file.write("X90 312.132080.963322-0.268189Carina Observatory, Brasilia\n")
    file.write("X93 313.6047 0.92363 -0.38244 Munhoz Observatory\n")
    file.write("Y00 315.215040.935906-0.351562SONEAR Observatory, Oliveira\n")
    file.write("Y01 316.015800.940890-0.337985SONEAR 2 Observatory, Belo Horizonte\n")
    file.write(
        "Y05 316.310000.941320-0.337075SONEAR Wykrota-CEAMIG, Serra da Piedade\n"
    )
    file.write("Y16 318.687940.929268-0.368170ROCG, Campos dos Goytacazes\n")
    file.write("Y28 321.3126 0.98840 -0.15179 OASI, Nova Itacuruba\n")
    file.write("Y40 324.038890.989706-0.143217Discovery Observatory, Caruaru\n")
    file.write("Y64 343.489610.881484+0.471433ATLAS-TDO, Teide\n")
    file.write("Y65 343.490420.881484+0.471429Two-Meter Twin Telescope, TTT1, Teide\n")
    file.write("Y66 343.490530.881484+0.471429Two-Meter Twin Telescope, TTT2, Teide\n")
    file.write("Y85 351.853890.727084+0.684321Magalofes Observatory, Fene\n")
    file.write("Y88 353.011940.741819+0.668659ASERO, Valdin\n")
    file.write("Y89 353.011890.741825+0.668670Proxima Centauri Observatory, Valdin\n")
    file.write("Y90 354.5553 0.73015 +0.68115 Observatorio ESTELIA, Ladines\n")
    file.write("Y91 354.833500.802497+0.594854Ras Algethi, Ronda\n")
    file.write("Y92 354.534820.787182+0.614800JD Cassini, Piconcillo\n")
    file.write("Y93 355.433220.746699+0.663112Observatorio Azahar, Valoria la Buena\n")
    file.write(
        "Y94 354.585710.732833+0.678415LCB Lugueros observatory, Valdelugueros\n"
    )
    file.write("Y95 357.998640.785356+0.617157Pradillos Ferez\n")
    file.write("Y98 358.686920.617953+0.783613Southside Observatory, Steeple Aston\n")
    file.write("Y99 359.072990.748454+0.661036Observatorio del Lucero del Alba\n")
    file.write("Z00 353.265860.798528+0.599968BOOTES-1, Mazagon\n")
    file.write("Z01 352.133210.856462+0.515344OWL-Net, Oukaimeden\n")
    file.write("Z02 352.133310.856450+0.515339HAO observatory, Oukaimeden\n")
    file.write("Z03 355.733460.761330+0.646426Rio Cofio, Robledo de Chavela\n")
    file.write("Z04 352.982030.833809+0.550302MAO, Ain Laqsab\n")
    file.write("Z05 355.363890.802644+0.594495Observatorio Horus, Cartama\n")
    file.write("Z06 357.673240.787439+0.614746Marina Sky, Nerpio\n")
    file.write("Z07 356.360500.798537+0.600132Ad Astra Sangos Observatory, Alhendin\n")
    file.write("Z08 357.591390.794477+0.605566Telescope Live, Oria\n")
    file.write("Z09 356.8786 0.62844 +0.77527 Old Orchard Observatory, Fiddington\n")
    file.write("Z10 353.372350.786766+0.615329PGC, Fregenal de la Sierra\n")
    file.write("Z11 358.966690.601635+0.796115Appledorne Observatory, Farnsfield\n")
    file.write("Z12 359.0961 0.78494 +0.61762 La Romaneta, Monovar\n")
    file.write("Z13 355.545190.802515+0.594662Observatorio AGP GUAM 4, Malaga\n")
    file.write("Z14 353.372260.786773+0.615335ART, Fregenal de la Sierra\n")
    file.write("Z15 359.653310.630352+0.773724Southwater\n")
    file.write("Z16 358.951920.793166+0.607001Asociacion Astronomica de Cartagena\n")
    file.write("Z17 343.488270.881476+0.471456Tenerife-LCO Aqawan A #2\n")
    file.write(
        "Z18 342.108110.877671+0.478415Gran Telescopio Canarias, Roque de los Muchachos\n"
    )
    file.write("Z19 342.110940.877701+0.478380La Palma-TNG\n")
    file.write("Z20 342.1217 0.87763 +0.47850 La Palma-MERCATOR\n")
    file.write("Z21 343.488300.881468+0.471452Tenerife-LCO Aqawan A #1\n")
    file.write("Z22 343.4894 0.88148 +0.47143 MASTER-IAC Observatory, Tenerife\n")
    file.write("Z23 342.114920.877679+0.478433Nordic Optical Telescope, La Palma\n")
    file.write("Z24 343.488480.881475+0.471460Tenerife Observatory-LCO B, Tenerife\n")
    file.write("Z25 343.490310.881476+0.471450Artemis Observatory, Teide\n")
    file.write(
        "Z26 343.389690.883010+0.467899Observatorio Astronomico Arcangel, Las Zocas\n"
    )
    file.write("Z27 343.6998 0.87976 +0.47393 Observatorio Coralito, La Laguna\n")
    file.write("Z28 357.673310.787438+0.614748Northern Skygems Observatory, Nerpio\n")
    file.write("Z29 354.119440.751634+0.657576Observatorio Astronomico Sobradillo\n")
    file.write("Z30 355.525000.586571+0.807215Glyn Marsh Observatory, Douglas\n")
    file.write("Z31 343.488350.881476+0.471458Tenerife Observatory-LCO A, Tenerife\n")
    file.write("Z32 358.983720.766879+0.640130Observatorio Astrofisico de Javalambre\n")
    file.write("Z33 357.673310.787438+0.6147486ROADS Observatory 2, Nerpio\n")
    file.write("Z34 359.112330.612800+0.787622NNHS Drummonds Observatory\n")
    file.write(
        "Z35 358.8985 0.76788 +0.63877 OAO University Observatory Station Aras\n"
    )
    file.write("Z36 354.945530.805224+0.591005Cancelada\n")
    file.write(
        "Z37 357.804260.632788+0.771754Northolt Branch Observatory 3, Blandford Forum\n"
    )
    file.write("Z38 351.152940.768722+0.637456Picoto Observatory, Leiria\n")
    file.write("Z39 346.4989 0.87535 +0.48189 Observatorio Costa Teguise\n")
    file.write(
        "Z40 355.5127 0.80240 +0.59482 El Manzanillo Observatory, Puerto de la Torre\n"
    )
    file.write(
        "Z41 356.6264 0.76087 +0.64689 Irydeo Observatory, Camarma de Esteruelas\n"
    )
    file.write(
        "Z42 357.665790.631495+0.772801Rushay Farm Observatory, Sturminster Newton\n"
    )
    file.write("Z43 357.462160.664742+0.744597Landehen\n")
    file.write("Z44 351.672480.728723+0.682549Observatorio Terminus, A Coruna\n")
    file.write("Z45 355.142640.804657+0.591779Cosmos Observatory, Marbella\n")
    file.write("Z46 356.807000.623612+0.779131Cardiff\n")
    file.write("Z47 357.2925 0.59846 +0.79849 Runcorn\n")
    file.write(
        "Z48 359.749150.623799+0.778975Northolt Branch Observatory 2, Shepherd's Bush\n"
    )
    file.write("Z49 357.406310.591893+0.803336Alston Observatory\n")
    file.write("Z50 355.284310.744053+0.666069Mazariegos\n")
    file.write("Z51 356.4486 0.76313 +0.64423 Anunaki Observatory, Rivas Vaciamadrid\n")
    file.write("Z52 359.338990.604299+0.794113The Studios Observatory, Grantham\n")
    file.write("Z53 352.1336 0.85645 +0.51534 TRAPPIST-North, Oukaimeden\n")
    file.write("Z54 358.922140.623422+0.779306Greenmoor Observatory, Woodcote\n")
    file.write("Z55 354.9150 0.79391 +0.60604 Uraniborg Observatory, Ecija\n")
    file.write("Z56 350.2119 0.61577 +0.78529 Knocknaboola\n")
    file.write(
        "Z57 355.425890.803207+0.593753Observatorio Zuben, Alhaurin de la Torre\n"
    )
    file.write("Z58 355.630680.762093+0.645483ESA TBT Cebreros Observatory\n")
    file.write("Z59 357.715400.599292+0.797871Chelford Observatory\n")
    file.write("Z60 357.8506 0.73205 +0.67900 Observatorio Zaldibia\n")
    file.write("Z61 359.064000.748594+0.660857Montecanal Observatory, Zaragoza\n")
    file.write("Z62 351.629120.737181+0.673585Observatorio Forcarei\n")
    file.write("Z63 358.470020.746291+0.663495Skybor Observatory, Borja\n")
    file.write("Z64 352.1424 0.74016 +0.67021 Observatorio el Miron del Cielo\n")
    file.write("Z65 352.172520.741388+0.668906Observatorio Astronomico Corgas\n")
    file.write(
        "Z66 355.591560.783284+0.619848DeSS Deimos Sky Survey, Niefla Mountain\n"
    )
    file.write("Z67 353.523140.597320+0.799328Dunboyne Castle Observatory\n")
    file.write("Z68 353.4003 0.77964 +0.62418 Observatorio Torreaguila, Barbano\n")
    file.write("Z69 353.1870 0.79823 +0.60034 Observatorio Mazagon Huelva\n")
    file.write("Z70 353.357110.737583+0.673113Ponferrada\n")
    file.write(
        "Z71 353.609720.773272+0.632064Observatorio Norba Caesarina, Aldea Moret\n"
    )
    file.write("Z72 353.888640.599295+0.797856Cademuir Observatory, Dalkey\n")
    file.write("Z73 353.967310.795365+0.604101Observatorio Nuevos Horizontes, Camas\n")
    file.write("Z74 354.1562 0.79610 +0.60315 Amanecer de Arrakis\n")
    file.write("Z75 354.4676 0.73736 +0.67346 Observatorio Sirius, Las Lomas\n")
    file.write("Z76 354.5644 0.72675 +0.68460 Observatorio Carda, Villaviciosa\n")
    file.write("Z77 354.889580.797212+0.601739Osuna\n")
    file.write("Z78 358.324200.788031+0.613690Arroyo Observatory, Arroyo Hurtado\n")
    file.write("Z79 357.453270.797556+0.601783Calar Alto TNO Survey\n")
    file.write("Z80 359.628080.623054+0.779568Northolt Branch Observatory\n")
    file.write("Z81 355.732400.802530+0.594629Observatorio Estrella de Mar\n")
    file.write("Z82 355.959030.802135+0.595173BOOTES-2 Observatory, Algarrobo\n")
    file.write(
        "Z83 356.2881 0.76033 +0.64755 Chicharronian 3C Observatory, Tres Cantos\n"
    )
    file.write("Z84 357.451790.797523+0.601826Calar Alto-Schmidt\n")
    file.write("Z85 356.750280.801058+0.596932Observatorio Sierra Contraviesa\n")
    file.write("Z86 356.8900 0.62347 +0.77923 St. Mellons\n")
    file.write("Z87 357.102100.608005+0.791293Stanley Laver Observatory, Pontesbury\n")
    file.write(
        "Z88 357.5101 0.62716 +0.77632 Fosseway Observatoy, Stratton-on-the-Fosse\n"
    )
    file.write("Z89 357.8281 0.59942 +0.79777 Macclesfield\n")
    file.write("Z90 357.8482 0.79540 +0.60418 Albox\n")
    file.write("Z91 358.749990.631731+0.772595Curdridge\n")
    file.write("Z92 358.392220.591378+0.803713Almalex Observatory, Leeds\n")
    file.write("Z93 359.855890.782380+0.620769Observatorio Polop, Alicante\n")
    file.write("Z94 358.8565 0.62725 +0.77623 Kempshott\n")
    file.write(
        "Z95 358.8909 0.76782 +0.63883 Astronomia Para Todos Remote Observatory\n"
    )
    file.write("Z96 359.193690.747818+0.661731Observatorio Cesaraugusto\n")
    file.write("Z97 359.416470.704568+0.707270OPERA Observatory, Saint Palais\n")
    file.write("Z98 359.5216 0.77156 +0.63405 Observatorio TRZ, Betera\n")
    file.write("Z99 359.978740.595468+0.800687Clixby Observatory, Cleethorpes\n")
    file.write("</pre>\n")

    file.close()


# ---------------------------------------------------------------------------------

# ---make options.txt-------------------------------------------------------------
def make_options_txt():
    filename = directory_path + "options.txt"
    file = open(filename, "w")

    file.write("500 0 15 35 1\n")
    file.write("help Full Herget epheM Vaisa resiD Gauss constr New Quit\n")
    file.write("???? ffff hhhhhh mmmmm vvvvv ddddd ggggg llllll nnn qqqqqqqqqqqq\n")
    file.write("now\n")
    file.write("1\n")
    file.write("10 oct 2010\n")

    file.close()


# ---------------------------------------------------------------------------------

# ---make rovers.txt---------------------------------------------------------------
def make_rovers_txt():
    filename = directory_path + "rovers.txt"
    file = open(filename, "w")

    file.write(
        '     Roving observer file.  This contains "MPC codes" for observers who\n'
    )
    file.write(
        "  don't really have MPC codes,  mostly satellite observers.  They could\n"
    )
    file.write(
        "  be handled using code 247 (Roving Observer),  but it's more convenient\n"
    )
    file.write("  if they have their own codes.\n")
    file.write("\n")
    file.write(
        "     Locations can be in the MPC standard longitude/rho_cos_phi/rho_sin_phi\n"
    )
    file.write("  triplet format,  or as lon/lat/altitude.\n")
    file.write("\n")
    file.write(
        "     Any line starting with a space is assumed to be a comment.  Negative\n"
    )
    file.write(
        "  longitudes (and those between 180 and 360) are in the Western Hemisphere.\n"
    )
    file.write("\n")
    file.write("MMc 262.1339 0.86573 +0.49912 Mike McCants\n")
    file.write(
        "Ber 138.6333 0.82043 -0.56986 Anthony Beresford, Adelaide, South Australia\n"
    )
    file.write("GRR  18.5129 -33.94058 10     Greg Roberts, South Africa\n")
    file.write(
        "Fet -75.6910 44.6062  100     Kevin Fetter, Brockville, Ontario, Canada\n"
    )
    file.write(
        "PGa -98.2161 26.24316  36     Paul Gabriel, McAllen, Texas USA 78504-2940\n"
    )
    file.write("GeS -70.73669 -30.24075 2722  Gemini South\n")
    file.write("IHN -81.081444 41.547806 300  Indian Hill North\n")
    file.write("E20 151.103197 -33.770505 208 Marsfield\n")
    file.write("Pav 151.103197 -33.770505 208 Marsfield\n")
    file.write("ITE   8.87444 46.178771 210   Marco Iten Gaggiole\n")
    file.write("\n")
    file.write(
        "   When 2008 TC3 impacted the earth on 7 Oct 2008,  I added the impact point\n"
    )
    file.write(
        '   as an "observatory" so I could get impact-centered ephemerides easily:\n'
    )
    file.write("\n")
    file.write("Sud  33.13003  20.59026 10    Sudan impact site\n")
    file.write("     32.84311  20.5983 10     Sudan impact site\n")
    file.write("     32.84976  20.59616 10    Sudan alt impact site\n")
    file.write("\n")
    file.write(
        "    The centers of the Sun,  moon,  and planets are treated as 'rovers'.\n"
    )
    file.write(
        "    (Note that right now,  Find_Orb doesn't support observers on the surfaces\n"
    )
    file.write(
        "    of other planets.  That might be useful someday;  for example,  Mars-\n"
    )
    file.write(
        "    based observations of Deimos and Phobos could be used and the orbits\n"
    )
    file.write("    of those objects computed.  But it's not there yet.)\n")
    file.write("\n")
    file.write("Sun   0.0000 0.00000  0.00000 @00Sun\n")
    file.write("Mer   0.0000 0.00000  0.00000 @01Mercury\n")
    file.write("Ven   0.0000 0.00000  0.00000 @02Venus\n")
    file.write("Mar   0.0000 0.00000  0.00000 @04Mars\n")
    file.write("Jup   0.0000 0.00000  0.00000 @05Jupiter\n")
    file.write("Sat   0.0000 0.00000  0.00000 @06Saturn\n")
    file.write("Ura   0.0000 0.00000  0.00000 @07Uranus\n")
    file.write("Nep   0.0000 0.00000  0.00000 @08Neptune\n")
    file.write("Plu   0.0000 0.00000  0.00000 @09Pluto\n")
    file.write("Lun   0.0000 0.00000  0.00000 @10Luna\n")

    file.close()


# ---------------------------------------------------------------------------------

# ---make xdesig.txt---------------------------------------------------------------
def make_xdesig_txt():
    filename = directory_path + "xdesig.txt"
    file = open(filename, "w")

    file.write(
        "; Used in the xref_designation() function in 'mpc_obs.cpp'.  The idea\n"
    )
    file.write(
        "; is that if you've an object listed under two different designations,\n"
    )
    file.write(
        "; you can tell Find_Orb to replace one designation with another.  For\n"
    )
    file.write("; example,  the satellite Jupiter XVII = Jupiter 17 = Callirrhoe was\n")
    file.write("; originally given the designation S/1999 J 1.  The first line below\n")
    file.write("; maps that original designation to the permanent J17 one.\n")
    file.write(
        ";   In practice,  this has been used almost exclusively to handle the\n"
    )
    file.write(
        "; nomenclature changes for natural satellites.  But it can also be useful\n"
    )
    file.write(
        "; in testing linkages.  Suppose you're thinking that J75X99X = K08Z41Z.\n"
    )
    file.write(
        "; Just add the line '    J75X99X    K08Z41Z',  and the observations of\n"
    )
    file.write(
        "; the two will be loaded as if they were one object,  and you can try to\n"
    )
    file.write("; link them.\n")
    file.write(
        ";   Any line starting with ';' is a comment,  and you can add text freely\n"
    )
    file.write("; after the two designations/line.\n")
    file.write(";\n")
    file.write("    SJ99J010 J017S        Callirrhoe\n")
    file.write("    SJ75J010 J018S        Themisto\n")
    file.write("    SK00J010 J018S        Themisto\n")
    file.write("    SK00J080 J019S        Magaclite\n")
    file.write("    SK00J090 J020S        Taygete\n")
    file.write("    SK00J100 J021S        Chaldene\n")
    file.write("    SK00J050 J022S        Harpalyke\n")
    file.write("    SK00J020 J023S        Kalyke\n")
    file.write("    SK00J030 J024S        Iocaste\n")
    file.write("    SK00J040 J025S        Erinome\n")
    file.write("    SK00J060 J026S        Isonoe\n")
    file.write("    SK00J070 J027S        Praxidike\n")
    file.write(";\n")
    file.write(";From IAUC 8177:\n")
    file.write(";\n")
    file.write("    SK01J010 J028S        Autonoe\n")
    file.write("    SK01J020 J029S        Thyone\n")
    file.write("    SK01J030 J030S        Hermippe\n")
    file.write("    SK01J110 J031S        Aitne\n")
    file.write("    SK01J040 J032S        Eurydome\n")
    file.write("    SK01J070 J033S        Euanthe\n")
    file.write("    SK01J100 J034S        Euporie\n")
    file.write("    SK01J090 J035S        Orthosie\n")
    file.write("    SK01J050 J036S        Sponde\n")
    file.write("    SK01J080 J037S        Kale\n")
    file.write("    SK01J060 J038S        Pasithee\n")
    file.write(";\n")
    file.write("    SK00S010 S019S        Ymir\n")
    file.write("    SK00S020 S020S        Paaliaq\n")
    file.write("    SK00S040 S021S        Tarvos\n")
    file.write("    SK00S060 S022S        Ijiraq\n")
    file.write("    SK00S120 S023S        Suttung\n")
    file.write("    SK00S050 S024S        Kiviuq\n")
    file.write("    SK00S090 S025S        Mundilfari\n")
    file.write("    SK00S110 S026S        Albiorix\n")
    file.write("    SK00S080 S027S        Skadi\n")
    file.write("    SK00S100 S028S        Erriapo\n")
    file.write("    SK00S030 S029S        Siarnaq\n")
    file.write("    SK00S070 S030S        Thrym\n")
    file.write(";\n")
    file.write("    SK03S010 S031S        Narvi\n")
    file.write(";\n")
    file.write("    SJ97U010 U016S        Caliban\n")
    file.write("    SJ97U020 U017S        Sycorax\n")
    file.write("    SJ99U010 U019S        Setebos\n")
    file.write("    SJ99U020 U020S        Stephano\n")
    file.write("    SJ99U030 U018S        Prospero\n")
    file.write("    SK01U010 U021S        Trinculo\n")
    file.write("\n")
    file.write("; From IAUC 8502,  30 Mar 2005:\n")
    file.write("\n")
    file.write("    SK03J080 J039S        Hegemone\n")
    file.write("    SK03J210 J040S        Mneme\n")
    file.write("    SK03J070 J041S        Aoede\n")
    file.write("    SK03J220 J042S        Thelxinoe\n")
    file.write("    SK02J010 J043S        Arche\n")
    file.write("    SK03J110 J044S        Kallichore\n")
    file.write("    SK03J060 J045S        Helike\n")
    file.write("    SK03J200 J046S        Carpo\n")
    file.write("    SK03J010 J047S        Eukelade\n")
    file.write("    SK03J130 J048S        Cyllene\n")
    file.write("\n")
    file.write(";   McNaught find from 26 Aug 2004:\n")
    file.write("     4H42B88      65058A  65058A\n")
    file.write("     4I034AB      INTEGRA Integral\n")
    file.write(";  More McNaught finds:\n")
    file.write("     5E4EA48      XMM\n")
    file.write("     5K522D0      XMM\n")
    file.write("\n")
    file.write("    SK04S020 S033S        Saturn XXXIII = Pallene = S/2004 S 2\n")
    file.write("    SK04S050 S034S        Saturn XXXIV = Polydeuces = S/2004 S 5\n")
    file.write("    SK05S010 S035S        Saturn XXXV = Daphnis = S/2005 S 1\n")
    file.write("    SK04S100 S036S        Saturn XXXVI = Aegir = S/2004 S 10\n")
    file.write("    SK04S110 S037S        Saturn XXXVII = Bebhionn = S/2004 S 11\n")
    file.write("    SK04S150 S038S        Saturn XXXVIII = Bergelmir = S/2004 S 15\n")
    file.write("    SK04S180 S039S        Saturn XXXIX = Bestla = S/2004 S 18\n")
    file.write("    SK04S090 S040S        Saturn XL = Farbauti = S/2004 S 9\n")
    file.write("    SK04S160 S041S        Saturn XLI = Fenrir = S/2004 S 16\n")
    file.write("    SK04S080 S042S        Saturn XLII = Fornjot = S/2004 S 8\n")
    file.write("    SK04S140 S043S        Saturn XLIII = Hati = S/2004 S 14\n")
    file.write("    SK04S190 S044S        Saturn XLIV = Hyrokkin = S/2004 S 19\n")
    file.write("    SK06S020 S045S        Saturn XLV = Kari = S/2006 S 2\n")
    file.write("    SK06S050 S046S        Saturn XLVI = Loge = S/2006 S 5\n")
    file.write("    SK06S080 S047S        Saturn XLVII = Skoll = S/2006 S 8\n")
    file.write("    SK06S070 S048S        Saturn XLVIII = Surtur = S/2006 S 7\n")
    file.write("    SK07S040 S049S        Saturn XLIX = Anthe = S/2007 S 4\n")
    file.write("    SK06S060 S050S        Saturn L = Jarnsaxa = S/2006 S 6\n")
    file.write("    SK06S040 S051S        Saturn LI = Greip = S/2006 S 4\n")
    file.write("    SK07S010 S052S        Saturn LII = Tarqeq = S/2007 S 1\n")
    file.write("\n")
    file.write("    SK02N010 N009S        Neptune IX = S/2002 N1 = Halimede\n")
    file.write("    SK03N010 N010S        Neptune X = S/2003 N1 = Psamathe\n")
    file.write("    SK02N020 N011S        Neptune XI = S/2002 N2 = Sao\n")
    file.write("    SK02N030 N012S        Neptune XII = S/2002 N3 = Laomedeia\n")
    file.write("    SK02N040 N013S        Neptune XIII = S/2002 N4 = Neso\n")
    file.write("J049SK03J140 J049S        Jupiter XLIX\n")
    file.write("\n")
    file.write(
        ";  When Herschel/Planck launched in May 2009,  there was some initial\n"
    )
    file.write(
        "; confusion as to which object was which.  So five of them got temporary\n"
    )
    file.write("; designations HPO1 through HPO5.\n")
    file.write("HPO1         2009-026D    Sylda\n")
    file.write("HPO2         Herschel     Herschel\n")
    file.write("HPO3         2009-026C    Booster\n")
    file.write("HPO4         2009-026E    object5\n")
    file.write("HPO5         2009-026F    object6 (the accelerating one)\n")

    file.close()


# ---------------------------------------------------------------------------------

try:
    params = readparam.readparam()
    DETECT_MINAREA = params["dm"]
    readparam.write_used_param("dm", params["dm"])

    make_default_conv()
    make_default_sex(DETECT_MINAREA)
    make_default2_param()
    make_ObsCodes_htm()
    make_options_txt()
    make_rovers_txt()
    make_xdesig_txt()

except Exception:
    print("Some errors occur in make_default_parameter_files.py!", flush=True)
    print(traceback.format_exc(), flush=True)
    error = 1

else:
    error = 0

finally:
    errorFile = open("error.txt", "a")
    errorFile.write("{0:d} 15 106 \n".format(error))
    errorFile.close()

    if error == 1:
        print_detailed_log.print_detailed_log(dict(globals()))
