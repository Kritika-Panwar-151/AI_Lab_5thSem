# Input
current_room = input("Enter current room (A/B): ").upper()
room_A = input("Enter status of Room A (clean/dirty): ").lower()
room_B = input("Enter status of Room B (clean/dirty): ").lower()

state = 0

while True:

    print("State " + str(state) + ": (" + current_room + ", " + room_A + ", " + room_B + ")")

    if room_A == "clean" and room_B == "clean":
        print("Goal Reached!")
        break

    if current_room == "A":

        if room_A == "dirty":
            print("Action: Suck")
            room_A = "clean"
        else:
            print("Action: Move Right")
            current_room = "B"

    else:

        if room_B == "dirty":
            print("Action: Suck")
            room_B = "clean"
        else:
            print("Action: Move Left")
            current_room = "A"

    state = state + 1
