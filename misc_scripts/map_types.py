import random

ELEMENT_TYPES = {
    1: "Insect",  # Added extra
    2: "Dragon",  #
    3: "Mystic",  #
    4: "Fire",  #
    5: "Phantom",  #
    6: "Earth",  #
    7: "Neutral",  #
    8: "Telepath",  #
    9: "Iron",  #
    10: "Unknown",
    11: "Lightning",  #
    12: "Combat",
    13: "Flyer",
    14: "Leaf",  #
    15: "Ice",  #
    16: "Toxin",
    17: "Rock",
    18: "Water"
}

# print ELEMENT_TYPES.keys()

TYPES_PER_GROUP = 6
NO_OF_GROUPS = 3
MAX_GROUP_TYPE_REPEAT = 2
NO_ROUNDS = 6

remain = {i: {j: 4 for j in xrange(0, 3)} for i in xrange(1, 19)}

for round in xrange(0, NO_ROUNDS):
    type_to_choose = ELEMENT_TYPES.keys()
    for group in xrange(0, 3):
        # print "round: ", round, " - ", "group: ", group
        type_to_choose = sorted(type_to_choose, key=lambda t: -remain[t][group])
        # for i in xrange(0, len(type_to_choose)):
        #     print str(type_to_choose[i]) + ":" + str(remain[type_to_choose[i]][group]) + ",",
        # print ""
        # print type_to_chose
        max_appear = []
        for typing in type_to_choose:
            if remain[typing][group] >= remain[type_to_choose[0]][group]:
                max_appear.append(typing)
        for ran_round in xrange(0, 100):
            pos1 = random.randint(0, len(max_appear) - 1)
            pos2 = random.randint(0, len(max_appear) - 1)
            max_appear[pos1], max_appear[pos2] = max_appear[pos2], max_appear[pos1]

        if remain[type_to_choose[0]][group] > remain[type_to_choose[5]][group]:
            second_appear = []
            for typing in type_to_choose:
                if remain[type_to_choose[5]][group] <= remain[typing][group] < remain[type_to_choose[0]][group]:
                    second_appear.append(typing)

            for ran_round in xrange(0, 100):
                pos1 = random.randint(0, len(second_appear) - 1)
                pos2 = random.randint(0, len(second_appear) - 1)
                second_appear[pos1], second_appear[pos2] = second_appear[pos2], second_appear[pos1]

            max_appear.extend(second_appear)

        chosen_list = []
        for i in xrange(0, 6):
            chosen = max_appear[i]
            remain[chosen][group] -= 1
            if remain[chosen][group] < 0:
                print "ERROR!!!"
            chosen_list.append(chosen)
            # print "chosen: ", chosen, " group: ", group, " remain: ", remain[chosen][group]
        for chosen in chosen_list:
            # print str(chosen) + ",",
            type_to_choose.remove(chosen)
            # print chosen, ": ", remain[chosen][group]
            print ELEMENT_TYPES[chosen] + ",",
        print ""





