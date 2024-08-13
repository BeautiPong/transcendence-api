document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    messageInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            sendMessage(currentUserNickname);
        }
    });

    window.loginAsUser = async (nickname) => {
        currentUserNickname = nickname;
        visitorUserNickname = nickname === "user1" ? "user2" : "user1"; // 예시로 사용자 1과 사용자 2로 설정
        await openOrCreateRoom();
    };

    async function openOrCreateRoom() {

        sortedNicknames = [currentUserNickname, visitorUserNickname].sort();

        const response = await fetch('http://127.0.0.1:8000/api/chat/rooms/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user1_nickname: sortedNicknames[0],
                user2_nickname: sortedNicknames[1]
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const roomData = await response.json();
        currentRoomId = roomData.id;
        displayMessages(roomData.messages);
        setupWebSocket(currentRoomId);

        sendBtn.onclick = () => sendMessage(currentUserNickname);
    }

    function displayMessages(messages) {
        chatMessages.innerHTML = '';
        messages.forEach((message) => {
            if (message.sender_nickname && message.text) {
                const messageElem = document.createElement('div');
                messageElem.classList.add('message-bubble');
                messageElem.textContent = `${message.sender_nickname}: ${message.text}`;

                if (message.sender_nickname === currentUserNickname) {
                    messageElem.classList.add('sent');
                } else {
                    messageElem.classList.add('received');
                }

                chatMessages.appendChild(messageElem);
            }
        });
        chatMessages.scrollTop = chatMessages.scrollHeight; 
    }

    function setupWebSocket(room_id) {

        socket = new WebSocket(`ws://127.0.0.1:8000/ws/room/${room_id}/messages`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const messageElem = document.createElement('div');
            messageElem.classList.add('message-bubble');
            messageElem.textContent = `${data.sender_nickname}: ${data.message}`;

            if (data.sender_nickname === currentUserNickname) {
                messageElem.classList.add('sent');
            } else {
                messageElem.classList.add('received');
            }

            chatMessages.appendChild(messageElem);
            chatMessages.scrollTop = chatMessages.scrollHeight; 
        };
    }

    function sendMessage(senderNickname) {
        const message = messageInput.value;
        if (message) {
            const messagePayload = {
                'sender_nickname': senderNickname,
                'message': message,
                'user1_nickname': sortedNicknames[0],
                'user2_nickname': sortedNicknames[1]
            };

            socket.send(JSON.stringify(messagePayload));
            messageInput.value = ''; 
        }
    }
});
