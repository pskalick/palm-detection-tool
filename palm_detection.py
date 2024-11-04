import cv2
import mediapipe as mp
import math
import os

# Initialize mediapipe Hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

# Helper function to calculate Euclidean distance between two landmarks
def distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)

# Function to mute and unmute audio on the system (using system commands)
def mute_audio():
    os.system("powershell -Command \"(New-Object -ComObject WScript.Shell).SendKeys([char]173)\"")  # Toggles mute

# Start video capture
cap = cv2.VideoCapture(0)
state_buffer = []
buffer_size = 10  # Number of frames to consider
is_muted = False  # Track the current mute state

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip and convert color to RGB
    image = cv2.flip(image, 1)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_image)

    current_state = "closed"  # Default state

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            wrist = hand_landmarks.landmark[0]
            index_base = hand_landmarks.landmark[5]
            pinky_base = hand_landmarks.landmark[17]

            # Check if the bases of the fingers are far from the wrist, indicating an open hand
            if distance(wrist, index_base) > 0.1 and distance(wrist, pinky_base) > 0.1:
                current_state = "open"

    # Add current state to buffer
    if len(state_buffer) >= buffer_size:
        state_buffer.pop(0)
    state_buffer.append(current_state)

    # Determine the final state based on buffer majority
    if state_buffer.count("open") > buffer_size // 2:
        final_state = "Palm is open"
        if not is_muted:
            mute_audio()  # Mute audio when the palm is detected as open
            is_muted = True
    else:
        final_state = "Palm is closed"
        if is_muted:
            mute_audio()  # Unmute audio when the palm is detected as closed
            is_muted = False

    # Display the current state
    cv2.putText(image, final_state, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
    cv2.imshow('Palm Detection', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()