from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import modes

FREQ_ALL = {0: 0.0, 1: 0.0, 2: 0.0, 3: 2.9462463887047796e-09, 4: 0.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 0.0, 9: 5.538943210764986e-07, 10: 0.002906262878963667, 11: 0.0, 12: 0.0, 13: 0.0, 14: 0.0, 15: 0.0, 16: 0.0, 17: 0.0, 18: 0.0, 19: 0.0, 20: 0.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 0.0, 25: 0.0, 26: 0.0, 27: 0.0, 28: 0.0, 29: 0.0, 30: 0.0, 31: 0.0, 32: 0.18181263778600001, 33: 0.0005428017034230251, 34: 0.0037493253905987625, 35: 1.5741794454849638e-05, 36: 8.458673381971422e-06, 37: 4.861306541362887e-07, 38: 2.1911234392797446e-05, 39: 0.0022831582839701044, 40: 0.00023481289093338223, 41: 0.0002363449390555087, 42: 0.0001195822484247496, 43: 9.118632573041293e-06, 44: 0.014210438700624498, 45: 0.0032746850973784224, 46: 0.008749037748563834, 47: 4.4812407572199694e-05, 48: 0.0003773346137405872, 49: 0.0007289072490583399, 50: 0.00045463233399464586, 51: 0.0003451262482192666, 52: 0.00031145949073553705, 53: 0.00031022501349866976, 54: 0.000294524466493262, 55: 0.0002896602137055104, 56: 0.0003610271399791063, 57: 0.00025192174371259086, 58: 0.00042196140779029854, 59: 0.0014331072759010016, 60: 2.7871490837147216e-06, 61: 2.3069109223558423e-05, 62: 3.087666215362609e-06, 63: 0.0005970303144535252, 64: 1.726500383781001e-06, 65: 0.0019080451400066006, 66: 0.0011464551797583586, 67: 0.0012103121239871461, 68: 0.0007713449820412436, 69: 0.001142498370858328, 70: 0.0007042235968137713, 71: 0.0007482022166579675, 72: 0.0014065321334748844, 73: 0.0034574348683770024, 74: 0.0003826614272113655, 75: 0.00025436418196882714, 76: 0.0008338525454240041, 77: 0.0013450704875601139, 78: 0.0008921852776739701, 79: 0.0008886144270508599, 80: 0.0008361624025927486, 81: 7.091615057612405e-05, 82: 0.0008659902010319958, 83: 0.0017116748719530385, 84: 0.002562804206200407, 85: 0.00024708695338872635, 86: 0.0002928598372836438, 87: 0.0010264398331144694, 88: 9.65308166795234e-05, 89: 0.000389402438948722, 90: 2.6498540020010787e-05, 91: 0.000203538485517281, 92: 7.188841188439663e-07, 93: 0.00021004085129715244, 94: 1.6351667457311527e-06, 95: 0.0014472639897987279, 96: 3.7122704497680225e-07, 97: 0.05982812906701693, 98: 0.010656876651323224, 99: 0.01905945055580732, 100: 0.031913272429274366, 101: 0.09656228848344754, 102: 0.0176779939253467, 103: 0.014274996851493797, 104: 0.04666710502884602, 105: 0.05030070186129646, 106: 0.0007354921097370951, 107: 0.004974003411977233, 108: 0.029905470332792613, 109: 0.018065549067809706, 110: 0.05305419008002023, 111: 0.058126218055596056, 112: 0.012891200901400546, 113: 0.0007745004119235464, 114: 0.04559727287891871, 115: 0.04787464768122778, 116: 0.06870773856303539, 117: 0.02141456796157515, 118: 0.007508903718630217, 119: 0.015830305588859107, 120: 0.001234132526039824, 121: 0.013964550869515974, 122: 0.00046391006387267716, 123: 7.200626173994481e-06, 124: 7.970774980001911e-05, 125: 7.268389840934691e-06, 126: 1.108967140708479e-05, 127: 0.0, 128: 5.204838870285864e-05, 129: 8.83873916611434e-09, 130: 1.767747833222868e-08, 131: 1.1490360915948641e-07, 132: 5.892492777409559e-09, 133: 2.9462463887047796e-09, 134: 5.8924927774095595e-08, 135: 2.9462463887047796e-09, 136: 0.0, 137: 5.892492777409559e-09, 138: 0.0, 139: 0.0, 140: 8.83873916611434e-09, 141: 0.0, 142: 2.0329100082062978e-07, 143: 6.187117416280038e-08, 144: 8.83873916611434e-09, 145: 2.9462463887047796e-09, 146: 0.0, 147: 0.0, 148: 2.9462463887047796e-09, 149: 2.9462463887047796e-09, 150: 0.0, 151: 2.6133205467811395e-06, 152: 2.8018803156582455e-06, 153: 1.7818898158886506e-05, 154: 0.0, 155: 0.0, 156: 1.5883214281507465e-05, 157: 1.5526718468474188e-05, 158: 0.0, 159: 0.0, 160: 6.776366694020994e-08, 161: 2.3569971109638237e-08, 162: 5.215445357285201e-05, 163: 1.767747833222868e-08, 164: 8.83873916611434e-09, 165: 5.892492777409559e-09, 166: 5.008618860798125e-07, 167: 5.892492777409559e-09, 168: 5.3032434996686034e-08, 169: 1.8561352248840113e-07, 170: 5.5978681385390815e-08, 171: 2.9462463887047796e-09, 172: 1.4731231943523899e-08, 173: 2.9462463887047796e-09, 174: 5.892492777409559e-09, 175: 2.0623724720933456e-08, 176: 7.660240610632426e-08, 177: 2.6516217498343017e-08, 178: 5.892492777409559e-09, 179: 1.767747833222868e-08, 180: 3.535495666445736e-08, 181: 1.1784985554819118e-08, 182: 1.3552733388041987e-07, 183: 8.83873916611434e-09, 184: 2.0623724720933456e-08, 185: 5.3032434996686034e-08, 186: 7.070991332891472e-08, 187: 1.4731231943523899e-08, 188: 2.3569971109638237e-08, 189: 2.0623724720933456e-08, 190: 8.83873916611434e-09, 191: 2.6516217498343017e-08, 192: 0.0, 193: 0.0, 194: 0.00010749085324550518, 195: 5.339482330249672e-05, 196: 0.0, 197: 0.0, 198: 0.0, 199: 0.0, 200: 0.0, 201: 0.0, 202: 0.0, 203: 0.0, 204: 0.0, 205: 0.0, 206: 0.0, 207: 0.0, 208: 0.0, 209: 0.0, 210: 0.0, 211: 0.0, 212: 0.0, 213: 0.0, 214: 0.0, 215: 0.0, 216: 0.0, 217: 0.0, 218: 0.0, 219: 0.0, 220: 0.0, 221: 0.0, 222: 0.0, 223: 0.0, 224: 0.0, 225: 0.0, 226: 0.0, 227: 0.0, 228: 0.0, 229: 0.0, 230: 0.0, 231: 0.0, 232: 0.0, 233: 0.0, 234: 0.0, 235: 0.0, 236: 0.0, 237: 0.0, 238: 0.0, 239: 0.0, 240: 0.0, 241: 0.0, 242: 0.0, 243: 0.0, 244: 0.0, 245: 0.0, 246: 0.0, 247: 0.0, 248: 0.0, 249: 0.0, 250: 0.0, 251: 0.0, 252: 0.0, 253: 0.0, 254: 0.0, 255: 0.0}

FREQ_ALPHA = {97: 0.07983659721025865, 98: 0.015263949560221991, 99: 0.02621265245863224, 100: 0.04226741725990764, 101: 0.1263508439548553, 102: 0.023771698117003227, 103: 0.019427849364159554, 104: 0.06216834223789161, 105: 0.06951947968898725, 106: 0.0014459848653599332, 107: 0.006761272188090216, 108: 0.03975178200895174, 109: 0.02510161724383835, 110: 0.06976290798232963, 111: 0.0763173855663371, 112: 0.017752087636410677, 113: 0.0010932841634927375, 114: 0.06008582273253808, 115: 0.06412453171362667, 116: 0.09216634637811191, 117: 0.028012633444928353, 118: 0.010089161865691195, 119: 0.0217989729978582, 120: 0.001720800400732555, 121: 0.018562387504284027, 122: 0.0006341914555011663}

FREQ_NONWS = {33: 0.0006660480537718686, 34: 0.0046006319869994474, 35: 1.9316062373072943e-05, 36: 1.0379265407653457e-05, 37: 5.965095061869803e-07, 38: 2.6886310287954987e-05, 39: 0.0028015629315486434, 40: 0.0002881285523248251, 41: 0.00029000846107159623, 42: 0.00014673410810374035, 43: 1.1189072252416389e-05, 44: 0.01743700320044703, 45: 0.00401822179641325, 46: 0.010735558728094377, 47: 5.498733084305437e-05, 48: 0.0004630106787023341, 49: 0.0008944099687858867, 50: 0.0005578593053951924, 51: 0.00042348921251060035, 52: 0.0003821782178003057, 53: 0.0003806634451755036, 54: 0.0003613979957302283, 55: 0.00035542928545923014, 56: 0.00044300049617660727, 57: 0.0003091220717334784, 58: 0.0005177702513702989, 59: 0.0017585027938209611, 60: 3.4199878354720204e-06, 61: 2.8307087475418522e-05, 62: 3.7887391665694266e-06, 63: 0.0007325895929893083, 64: 2.1185125492458816e-06, 65: 0.0023412781205291275, 66: 0.0014067646368818335, 67: 0.001485120679530904, 68: 0.0009464834410714459, 69: 0.0014019094110223843, 70: 0.0008641217467081017, 71: 0.0009180859733678172, 72: 0.0017258936074827395, 73: 0.004242465988230014, 74: 0.0004695469768064921, 75: 0.00031211908010092695, 76: 0.0010231837179397064, 77: 0.0016504767298550632, 78: 0.0010947612434730155, 79: 0.0010903796100093877, 80: 0.0010260180418963766, 81: 8.7018083720731e-05, 82: 0.0010626184191123583, 83: 0.002100320816911743, 84: 0.003144704121180422, 85: 0.0003031895135537643, 86: 0.00035935540257267897, 87: 0.0012594990930362175, 88: 0.00011844871188309226, 89: 0.00047781857529228486, 90: 3.2515190900883036e-05, 91: 0.00024975310742679605, 92: 8.821110273310497e-07, 93: 0.00025773187397318796, 94: 2.0064410662652976e-06, 95: 0.0017758738736829518, 96: 4.555163501791486e-07, 97: 0.07341246107852295, 98: 0.013076583783984515, 99: 0.023387011994623997, 100: 0.03915937046064174, 101: 0.11848732954700189, 102: 0.02169188743203312, 103: 0.017516219662868662, 104: 0.05726314837189545, 105: 0.06172177494433111, 106: 0.000902489961187874, 107: 0.006103380426240459, 108: 0.036695684974233915, 109: 0.022167439271201895, 110: 0.06510045901551109, 111: 0.07132412106466275, 112: 0.01581822462422983, 113: 0.0009503553300479686, 114: 0.05595040447881607, 115: 0.05874487075484565, 116: 0.08430823864477002, 117: 0.026276872793924825, 118: 0.009213844901765748, 119: 0.019424670485708517, 120: 0.001514349645334066, 121: 0.017135285077008528, 122: 0.0005692435989405428, 123: 8.835571109824121e-06, 124: 9.780586775989434e-05, 125: 8.918720919777458e-06, 126: 1.3607647159319964e-05}

FREQ_PRINTABLE = {9: 5.5407260740153e-07, 10: 0.0029071983406727866, 11: 0.0, 12: 0.0, 13: 0.0, 32: 0.18187115925083855, 33: 0.0005429764192798983, 34: 0.003750532215474558, 35: 1.5746861390140292e-05, 36: 8.461396041754215e-06, 37: 4.862871288364492e-07, 38: 2.1918287134282865e-05, 39: 0.002283893182098547, 40: 0.00023488847200688585, 41: 0.00023642101326140072, 42: 0.00011962073930432606, 43: 9.1215676590837e-06, 44: 0.014215012726384674, 45: 0.00327573914604697, 46: 0.008751853870210867, 47: 4.4826831694559957e-05, 48: 0.0003774560694028519, 49: 0.0007291418681720921, 50: 0.00045477867008256753, 51: 0.00034523733672139694, 52: 0.00031155974265343266, 53: 0.0003103248680656601, 54: 0.0002946192674016029, 55: 0.0002897534489185182, 56: 0.0003611433466264292, 57: 0.00025200283174720863, 58: 0.0004220972278300379, 59: 0.0014335685614204118, 60: 2.7880462053289753e-06, 61: 2.3076534659329682e-05, 62: 3.0886600667915078e-06, 63: 0.0005972224853002842, 64: 1.72705610604945e-06, 65: 0.0019086592975147418, 66: 0.0011468241983112392, 67: 0.001210701696677307, 68: 0.0007715932609221541, 69: 0.0011428661158019826, 70: 0.0007044502708060815, 71: 0.0007484430463948189, 72: 0.0014069848650440193, 73: 0.0034585477401528324, 74: 0.00038278459745701127, 75: 0.00025444605617027174, 76: 0.0008341209441063607, 77: 0.001345503435985491, 78: 0.0008924724523720145, 79: 0.0008889004523711067, 80: 0.0008364315447670139, 81: 7.093897691571716e-05, 82: 0.0008662689441145304, 83: 0.0017122258222172983, 84: 0.0025636291161630345, 85: 0.00024716648521132614, 86: 0.0002929541023846781, 87: 0.0010267702213830406, 88: 9.656188781331771e-05, 89: 0.0003895277789768767, 90: 2.6507069313666815e-05, 91: 0.00020360400005174094, 92: 7.191155117339007e-07, 93: 0.0002101084587992685, 94: 1.635693069722602e-06, 95: 0.0014477298320510733, 96: 3.7134653474783393e-07, 97: 0.05984738641784901, 98: 0.010660306864095194, 99: 0.019065585371181682, 100: 0.03192354460547232, 101: 0.09659336974731911, 102: 0.017683684080401465, 103: 0.014279591657094153, 104: 0.046682126137275654, 105: 0.050316892544139936, 106: 0.0007357288483717859, 107: 0.004975604433607662, 108: 0.029915096241925617, 109: 0.01807136396828876, 110: 0.053071267049790385, 111: 0.05814492759893452, 112: 0.012895350293706078, 113: 0.0007747497064675106, 114: 0.0456119496320532, 115: 0.04789005747091595, 116: 0.06872985406367062, 117: 0.021421460837126906, 118: 0.007511320668575484, 119: 0.01583540101392517, 120: 0.001234529765990293, 121: 0.013969045749424477, 122: 0.00046405938625654314, 123: 7.20294389621989e-06, 124: 7.973340596085634e-05, 125: 7.2707293747849706e-06, 126: 1.1093240926911483e-05}

FREQ_BASE64 = {43: 2.579352747574329e-06, 47: 0.00015139650316572855, 48: 0.018828739719929898, 49: 0.010183656286584335, 50: 0.023722393492817736, 51: 0.014760673494397735, 52: 0.006154645355013087, 53: 0.013537173224764675, 54: 0.00023432070307616705, 55: 0.0003624012731720556, 56: 0.002396911101647487, 57: 0.012916715009252754, 61: 0.002173168841829382, 65: 0.003305113149612865, 66: 0.04584600858833325, 67: 0.01854079458293096, 68: 0.0009277750437720143, 69: 0.004723491704235257, 70: 0.01640676952057699, 71: 0.054718648007171716, 72: 0.020831598279869915, 73: 0.0504069435538869, 74: 0.013497750715918602, 75: 0.0002821161537314766, 76: 0.006656703315715042, 77: 0.0060044367698794746, 78: 0.012861022226428627, 79: 0.0008355465920122639, 80: 0.0003478675274159979, 81: 0.010866103029276812, 82: 0.017519147468967423, 83: 0.016373074236656703, 84: 0.0018576427699618719, 85: 0.010947560581784472, 86: 0.022217358861711015, 87: 0.03151304088894388, 88: 0.022439884445704793, 89: 0.02437201653390772, 90: 0.04479834452096986, 97: 0.025539441320866454, 98: 0.03978490569497019, 99: 0.028651925929696065, 100: 0.035286218076726994, 101: 0.003929473576314084, 102: 0.0003740857853613246, 103: 0.047310233700154164, 104: 0.02637101270113996, 105: 0.013707782145265466, 106: 0.0050147484116142265, 107: 0.012069287024781465, 108: 0.038735144520913235, 109: 0.025097571207125052, 110: 0.010108731177184384, 111: 0.011899063016268734, 112: 0.013051754965063795, 113: 0.00022242824992783122, 114: 0.001244068727477782, 115: 0.011803775177845265, 116: 0.006257952193187805, 117: 0.015463699755624245, 118: 0.014647788099278766, 119: 0.008193577247075482, 120: 0.006850802928176803, 121: 0.02151193906731737, 122: 0.012351055872868543}

EN_WORDS = open('crypt/words.txt','rb').read().split(b'\n')
EN_WORDS.pop()  #remove final b''

BACKEND = default_backend()
ECB_MODE = modes.ECB()

ZERO_16 = b'\x00'*16

PRIMES_FNAME = 'crypt/primes'
