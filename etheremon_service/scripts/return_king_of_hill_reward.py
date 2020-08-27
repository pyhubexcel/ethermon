# After moving win reward to quest, some forgot to claim the old win reward.
# This script is to add this amount back to the emont balance.
from django.db import transaction

from etheremon_lib import emont_bonus_manager, user_manager, transaction_manager
from etheremon_lib.emont_bonus_manager import EmontBonusType
from etheremon_lib.transaction_manager import TxnTypes, TxnAmountTypes, TxnStatus

KING_OF_HILL_PLAYERS = [
	['Hash Ketchum', '0x2fef65e4d69a38bf0dd074079f367cdf176ec0de', '1', 4000],
	['Lovely Lovely', '0x926138036ddc21ff6a9c0e0595096864963b47cf', '2', 2000],
	['()', '0x52e1319ecc564852b63ab200802c49b1d7140f93', '3', 2000],
	['number11', '0x7ebc7e83cb2b43deafa82eb0ae8b5daea3fe9a13', '4', 1000],
	['Napoleon', '0x99a811e5c62add613975456292f836115aea0164', '5', 1000],
	['SwissOne.io', '0x196a54d93375df73073076a63fed635a6d17443f', '6', 1000],
	['SwissOne.io', '0xa6fe83dcf28cc982818656ba680e03416824d5e4', '7', 1000],
	['@everest_AZ', '0x69aae7a2969d5ef1a6521ed2f2cc68b9d16360b3', '8', 1000],
	['hatoyashi', '0x088e25e6027816c753d01d7f243c367710f20497', '9', 1000],
	['hagoromo', '0x85dc15b8cfc601da2b4cfd2d92da9721cbc2680b', '10', 1000],
	['TONKA', '0xa9838c0f833d4e378fc937cc00d8b4080193815b', '11', 600],
	['hagoromo', '0x057dc43af6187a931e78a56b3293912a5b42e5ec', '12', 600],
	['EB---2', '0x2fb172b799fe972b83604739da8b5fe0cc299560', '13', 600],
	['forest gate', '0xc674d5f701bbd8a79315cd2434af18c75816856e', '15', 600],
	['Zedakazm', '0xb61ce2b4347bf9a028611f98dbdc8658a47457a2', '15', 600],
	['____0215', '0x798fc047b8628533d70544a24a9ea37f92c88b64', '16', 600],
	['Mon complex', '0x9a81d4da7d0147f0163e4ecf95f67678c40a26a5', '18', 600],
	['NewKidOnTheBlock', '0x517ab21c615a8e6f16c0c6d57d621b562538422d', '18', 600],
	['_______', '0x9b741445414034d8d8e3af518d5a07309f253c7b', '19', 600],
	['natoris', '0xea2259bbedac98bbc9bda01ceacb987886c7bb9f', '20', 600],
	['Voquila', '0x93340f248036e07dcf47c96f964a9a201c1d5383', '21', 150],
	['Star Dancer', '0x83ac654be75487b9cfcc80117cdfb4a4c70b68a1', '22', 150],
	['Lemongrass', '0x3c9c530d684a99cc39388c644f21ebeeb61c2839', '23', 150],
	['hagoromo2', '0xff60e23eb04b76c699e3d180617c3245cbcafd78', '24', 150],
	['yesman0522', '0xd768daff5aeffc055d334b5f4db1bf401a84d12e', '25', 150],
	['Blue Grass', '0x669df91f06f40d8e887d0a26e8068e14fd6d807f', '26', 150],
	['hagoromo_farm', '0x3904d7debce689933d4e10d245e714cbadb50c0e', '27', 150],
	['kasinoki_ph', '0xa7b63c5d585cacc1ae336e343e1bc4d4ba138cb4', '28', 150],
	['Lululu', '0xec94cb51585c7783a9104481dba8761422133838', '30', 150],
	['natoris.v3', '0x0c2bbdd40855df7ed68b5ec999c8f8931645e477', '30', 150],
	['Lilili', '0x70e68fc54cf52215e875a667edef0cec30b5eb2e', '31', 150],
	['GCS', '0x54371815bb3e329c0f79735207ec8d8d5ebb72a8', '32', 150],
	['maulotov', '0xf796b8fb98c7c98fd4b5424ced013820d1f2ee76', '33', 150],
	['MiMi Kawaii', '0x26b162737be70a0c8ab22672e4f135c323a18948', '34', 150],
	['Mantis', '0x56320ac9f51cc2bf4837f3b401d91aed0ada044d', '35', 150],
	['bazinga', '0x165b440662b38c8c2d2af9fca313d3af3f479851', '36', 150],
	['Mon Mommy', '0x48857c7953273e5edc1990e81a188f64042f0269', '37', 150],
	['y_taka', '0x570ce9d97c9dc429d3eb49b6d82455db7d73697f', '38', 150],
	['Baleet Mechanic', '0x6b8ff298a189bad6b61da50d1219e6f9287f9c28', '39', 150],
	['motion blue', '0xd7d560b364c8ca52ed82556c0a0995175c91528b', '40', 150],
	['blue sky fish', '0x419473f836faa97957a258d903b4822ab7d5094b', '41', 150],
	['Shadow effect', '0x685a6bdae46dcd719aa7667ec5e166eed658b885', '42', 150],
	['King Jah', '0x52b893df4883b86d98ad5be66fdae044c4c51ddb', '43', 150],
	['Santa_Tonakai', '0x61d8b2cfc0594daf7def2dd75e5e0c35bb80885c', '44', 150],
	['telepath333', '0xed63cc0074f77214e39b226f1464172fab41873d', '45', 150],
	['Cao Cao', '0x4bc217637c3212e38c4787a23d84f57574a03c85', '46', 150],
	['Lalilu', '0xb08237d62eca2bc1e336ccf22dcc88e8a3214e8c', '47', 150],
	['sea star', '0x5d457e2d69d19e4a3b0779be6a7a2d9a29ab01b2', '48', 150],
	['Ethers', '0x362cbdf5a9989035350c074dbc09c4e27c59cf5d', '49', 150],
	['blue monday', '0x71b7a04397f56498115e2d04b4b752032f618773', '50', 150],
	['Shinemon', '0xaa338d6a641b49b72a989a34b4ada03f8e7cca09', '51', 150],
	['Avocadica', '0xed2e05d734875b33538a688953429ea22690e01a', '52', 150],
	['momomomo', '0x9a2ad0035c0899d72ecdff5d2fede1269526de5d', '53', 150],
	['Causal Muel', '0xc0b6d97e6e197ad51677e4ed713419341ca020bf', '54', 150],
	['marumaru', '0xb327deb67a7725f277bae3c70a50c69255283908', '55', 150],
	['PONPON', '0x07c83c5f179a137b8188df0fddbc7f9c59817372', '56', 150],
	['Y_taka', '0xb8d10a93433e9259ece49012476b296b9a9e5f3a', '57', 150],
	['dappsmarket', '0x21ef87615a87f0fef27c16ee8e3d72e691fa95ff', '58', 150],
	['_______', '0x51c18217fd5cd24bff32f272eff9f2cac6a0dd32', '59', 150],
	['------', '0x9fb0065cf636a2bd2ff0e6c95763a73e9d1df5d3', '60', 150],
	['--=STARFIGHTER=--', '0xbafaea7f4af490bcc61209cbaaf83f3c32f81e11', '61', 150],
	['takiryu', '0x029ee1a0aaaeff97f0c84893b6761c6e8aa7d3d1', '62', 150],
	['________', '0x4641a090e41355f65cb96fba8ca06a490ba427d9', '63', 150],
	['nike33', '0x68b5d2b865da2c90f05e10c62ade13edc4461708', '64', 150],
	['_Theo_', '0x6ec05beacd505d1ab3fb1fabeb93280959a25300', '65', 150],
	['Kasinoki_ph', '0x6ea9637c53924c4e2dc7b039eca8d646f20cbdee', '66', 150],
	['______', '0xd0d0f23d8d2c66b5c445d37baa377661080436bf', '67', 150],
	['urabyakko', '0x0945255148a4e0fafb31af7964d67a827442c8fd', '68', 150],
	['Not So Casual', '0x5071d3baa369b96fc9021c13792847ba43b712f1', '69', 150],
	['Bridge Casino', '0xbbbcc68611b59f05433f381340bd3b536517ed14', '70', 150],
	['fire-emperor', '0xaa9d345a8e1daa5c37c8cd128c1a0e5ad11d7465', '71', 150],
	['chuchu', '0xde3ac413e7a7923ad599a6804dafb6e8f517dd4a', '72', 150],
	['HurrDurr', '0x191d3a78decc6ef9efe2ca4cb687c93d8f4d55c1', '73', 150],
	['childfood', '0x8b29aaad1382876d6b52dfdad73e0a5e663c1470', '74', 150],
	['peaceful', '0x537db8412023406ceae58f407c6802e61ae9e814', '76', 150],
	['syouei', '0x4550d74cc0ac86f88aabed20a6c1a4b59dfab3c5', '76', 150],
	['yama-shin', '0x68843fdd917efe8bb6f6fe9616b795e4d8e89524', '77', 150],
	['Go Anywhere', '0xa057bc6de5c0e52c1226eb18c6427a54c866d334', '78', 150],
	['Liu Bei', '0x3e7d634d85eb79d56b79a68ea035076c8149db00', '79', 150],
	['RomanPavlik', '0xe531544db533d5fdb6bdbbb1f8f5ee9545e94109', '80', 150],
	['papermoon shine', '0x3ccc500baf9b9334cb3596e59bfb35876be1db1e', '81', 150],
	['bibit bit', '0xea74ecca159831c9771972b1fd7d41661baac856', '82', 150],
	['raspberry_cheese', '0x86a58ebc045cc02b820132ac86f07aa410ce4b5a', '83', 150],
	['_________', '0x0899d938ee5cdf7a8f710b4a98e16b2d56818afe', '84', 150],
	['Yu@first', '0x3d44f67b32454ebc1f579873edf480faa80cd953', '85', 150],
	['HotDamn', '0xb56d39b3304c220df35194748154152bc543bf1e', '86', 150],
	['-Skuld-', '0xaaf12ba045fbabcd122a781f66ab900266dc2dd3', '87', 150],
	['XXXXXgoal', '0x6426942ee4d1602891ba4aba2be680dd8587f694', '88', 150],
	['______', '0xff1a9252def51ede4489c05998f5e7cf8ad2c1b3', '89', 150],
	['MotoJAx', '0x6b5bb4e60821ece7363caff836be1a4f9e3559b3', '90', 150],
	['virtual', '0x924df537c2e6ef6ea5401d676ba9956441dcc13b', '91', 150],
	['Barnicl3s', '0xab4787b17bfb2004c4b074ea64871dfa238bd50c', '92', 150],
	['Uselezzz', '0x4ce15b37851a4448a28899062906a02e51dee267', '93', 150],
	['absolut defeat', '0xfbfa46695a1e46cad60750571f7f0e5e6bbc80fb', '94', 150],
	['MILLENNIUM FALCON', '0x1d31c0addfcb9f559da854f01c7cd5ccc2a4bb96', '95', 150],
	['_________', '0x25ec8d98be8c8a1498eec9a16170059a77b242f3', '96', 150],
	['Lololo', '0x42232d71109bd15b226f06b99ee92125b72eaa2c', '97', 150],
	['natoris.v4', '0x493ee70de0a8f7f7a46f80985c2c4318895fbba4', '98', 150],
	['_______', '0xebf1a2b1165786825f781c7d4d3f24d4b5bbc771', '99', 150],
	['flowbot44', '0x954149c9febade512b1b6c5645bc7aad04053a58', '100', 150],
	['Monsforever', '0x8c93d0ac21fa8b9eab8ab4cd2dafd29503ee6ecb', '155', 100],
	['sky lock gate', '0x7d55e1ffaeb91e9dba127a8398c704c1cd881cd1', '177', 100],
	['dumdidum', '0xb682505323c4e2804fe5e6c86c227a3b01d421e9', '222', 100],
	['schyan', '0xbcce870909b3dbbe28f744f69b080dbdeeb7748a', '266', 100],
	['--=Death Star=--', '0x12d5d2f7e880a01465beadae0d5c15798805874e', '266', 100],
	['amitaho', '0xf35baabdd8c836fd69c3535e79c309e4426e5396', '288', 100]
]


def return_rewards(execute=False):
	for data in KING_OF_HILL_PLAYERS:
		name, address, rank, reward = data
		player_uid = user_manager.get_uid_by_address(address)

		if player_uid == "":
			print "player hasn't registered", address, reward
			continue

		with transaction.atomic():
			txn = transaction_manager.get_player_transactions(player_uid, TxnTypes.EVENT_KING_OF_HILL)

			if len(txn) == 0:
				print "ready to send reward", player_uid, address, reward

				if execute:
					emont_bonus_manager.add_bonus(player_uid, {
						EmontBonusType.EVENT_BONUS: reward
					})

					transaction_manager.create_transaction(
						player_uid=player_uid,
						player_address=address,
						txn_type=TxnTypes.EVENT_KING_OF_HILL,
						txn_info="",
						amount_type=TxnAmountTypes.IN_GAME_EMONT,
						amount_value=reward,
						status=TxnStatus.FINISHED
					)
