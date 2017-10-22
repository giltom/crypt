#probability of each printable, non-whitespace character in English plaintext
EN_PROBS = {33: 0.0006462856286084933, 34: 0.0029313405722307087, 35: 0.00016731892072777211, 36: 7.0230487245735e-05, 37: 2.4598054319978966e-05, 38: 3.746205445904924e-05, 39: 0.0033524192794856136, 40: 0.0006895712506980676, 41: 0.0006916138453147443, 42: 0.00023016129978552756, 43: 1.8904865069241786e-05, 44: 0.014847359511863346, 45: 0.0027668465163983406, 46: 0.009842220430726707, 47: 7.566291973689643e-05, 48: 0.0008526746038126984, 49: 0.0016849667209185592, 50: 0.0011373340663495574, 51: 0.0006813574127714315, 52: 0.0005242514651270429, 53: 0.00047814097814206463, 54: 0.0003878756798689263, 55: 0.00036249535527022004, 56: 0.0003674931931620886, 57: 0.00047753254570305454, 58: 0.0028804060851935795, 59: 0.001387790933922064, 60: 4.780540592222061e-06, 61: 2.885708139304953e-05, 62: 1.638421639334288e-05, 63: 0.0008572813065652033, 64: 4.041729773424105e-06, 65: 0.0025088711622580665, 66: 0.001073144444033994, 67: 0.0009930486593843098, 68: 0.0009346391452393421, 69: 0.0008382895225761029, 70: 0.0007244257375613593, 71: 0.0009078681179228986, 72: 0.0009999587135130672, 73: 0.0030113494379605346, 74: 0.0005358551409281637, 75: 0.00018657146147644824, 76: 0.0009616709293153614, 77: 0.0011534140665233953, 78: 0.0007444605485887627, 79: 0.0009933528756038148, 80: 0.0006581066017092605, 81: 8.283373062522952e-05, 82: 0.0008547171984293751, 83: 0.001517213205591494, 84: 0.0022201699699477833, 85: 0.0003316391387204231, 86: 0.00016314681257456013, 87: 0.0011618452017496778, 88: 3.333340576576655e-05, 89: 0.00035328194976521027, 90: 6.8144433169129e-05, 91: 9.026529827313836e-05, 92: 2.0425946166766985e-06, 93: 9.000454151356262e-05, 94: 4.78054059222206e-07, 95: 0.00010152129839482485, 96: 3.237729764732214e-05, 97: 0.07492293551268038, 98: 0.013905245339516165, 99: 0.024443338642630687, 100: 0.03617526331000285, 101: 0.11642867542085054, 102: 0.02097827244300835, 103: 0.018636807120397916, 104: 0.05521872059695914, 105: 0.06364055549881682, 106: 0.001304392230317754, 107: 0.007297625592406763, 108: 0.0399584527563076, 109: 0.023617478525594364, 110: 0.06524329692154916, 111: 0.07112171039050498, 112: 0.016426458988394153, 113: 0.0007937870356085084, 114: 0.05605687974115545, 115: 0.06132681731164127, 116: 0.08478901518690828, 117: 0.02659232201721429, 118: 0.009729399672750267, 119: 0.01807109533049833, 120: 0.001575318503516957, 121: 0.018162620953109415, 122: 0.0007087368725268851, 123: 3.9113513936362313e-07, 124: 2.781405435474653e-06, 125: 1.7123027212140834e-05, 126: 7.822702787272463e-07}

#probability of each alphabetic character in English plaintext. Capital and lowercase counted separately!
EN_PROBS_ALPHA = {65: 0.0026377612133637613, 66: 0.0011282758690015651, 67: 0.0010440652657306023, 68: 0.0009826550374092925, 69: 0.0008813555759596319, 70: 0.0007616421844404118, 71: 0.0009545086827620256, 72: 0.0010513303150632572, 73: 0.003166053668610029, 74: 0.0005633840142870166, 75: 0.00019615633198168385, 76: 0.0010110755448615653, 77: 0.0012126692408091985, 78: 0.0007827062582916944, 79: 0.001044385110669776, 80: 0.0006919159877005913, 81: 8.70892077235242e-05, 82: 0.0008986272026750003, 83: 0.0015951580959265234, 84: 0.0023342283660881206, 85: 0.00034867667583327034, 86: 0.00017152827166532522, 87: 0.001221533514837721, 88: 3.504586690658083e-05, 89: 0.00037143135864875563, 90: 7.164526637486147e-05, 97: 0.07877200561739098, 98: 0.014619609556144324, 99: 0.02569908394124814, 100: 0.03803372125193706, 101: 0.1224100498935259, 102: 0.022056004391927935, 103: 0.019594249279377928, 104: 0.05805551183072161, 105: 0.06691000774253214, 106: 0.0013714037149075843, 107: 0.007672531785161982, 108: 0.0420112672233644, 109: 0.024830796315660455, 110: 0.06859508795850057, 111: 0.07477549741028407, 112: 0.017270347335611697, 113: 0.0008345668305719672, 114: 0.058936730330278735, 115: 0.06447740421158109, 116: 0.08914494253186056, 117: 0.027958468591569665, 118: 0.010229235152512348, 119: 0.018999474768917744, 120: 0.0016562484793086597, 121: 0.019095702403474794, 122: 0.0007451473240058933}

#probability of each alphabetic character in English plaintext. Case insensitive - lowercase keys.
EN_PROBS_LOWER = {97: 0.08166999999999999, 98: 0.01492, 99: 0.02782, 100: 0.04253, 101: 0.12702, 102: 0.02228, 103: 0.02015, 104: 0.06094, 105: 0.06966, 106: 0.00153, 107: 0.00772, 108: 0.04025, 109: 0.02406, 110: 0.06749, 111: 0.07507, 112: 0.01929, 113: 0.00095, 114: 0.05987, 115: 0.06326999999999999, 116: 0.09055999999999999, 117: 0.02758, 118: 0.00978, 119: 0.0236, 120: 0.0015, 121: 0.01974, 122: 0.00074}
#EN_PROBS_LOWERCASE = {97: 0.08140976683075474, 98: 0.01574788542514589, 99: 0.026743149206978744, 100: 0.03901637628934635, 101: 0.12329140546948554, 102: 0.02281764657636835, 103: 0.020548757962139955, 104: 0.05910684214578486, 105: 0.07007606141114217, 106: 0.0019347877291946008, 107: 0.007868688117143667, 108: 0.04302234276822597, 109: 0.026043465556469653, 110: 0.06937779421679227, 111: 0.07581988252095384, 112: 0.017962263323312286, 113: 0.0009216560382954915, 114: 0.059835357532953735, 115: 0.0660725623075076, 116: 0.09147917089794867, 117: 0.028307145267402935, 118: 0.010400763424177673, 119: 0.020221008283755462, 120: 0.0016912943462152406, 121: 0.01946713376212355, 122: 0.0008167925903807548}

#probability of each alphabetic character in English plaintext. Case insensitive - uppercase keys.
EN_PROBS_UPPER = {65: 0.08166999999999999, 66: 0.01492, 67: 0.02782, 68: 0.04253, 69: 0.12702, 70: 0.02228, 71: 0.02015, 72: 0.06094, 73: 0.06966, 74: 0.00153, 75: 0.00772, 76: 0.04025, 77: 0.02406, 78: 0.06749, 79: 0.07507, 80: 0.01929, 81: 0.00095, 82: 0.05987, 83: 0.06326999999999999, 84: 0.09055999999999999, 85: 0.02758, 86: 0.00978, 87: 0.0236, 88: 0.0015, 89: 0.01974, 90: 0.00074}

EN_WORDS = open('words.txt','rb').read().split(b'\n')
EN_WORDS.pop()  #remove final b''
