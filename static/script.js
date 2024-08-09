const socket = io();

const form = document.getElementById('form');
const input = document.getElementById('input');
const messages = document.getElementById('messages');
const username = "{{ username }}";

form.addEventListener('submit', function(e) {
    e.preventDefault();
    if (input.value) {
        const msg = input.value;
        addMessage(msg, username, 'me');
        socket.emit('message', {msg: msg, username: username});
        input.value = '';
    }
});

socket.on('message', function(data) {
    const sender = data.username === username ? 'me' : 'other';
    addMessage(data.msg, data.username, sender);
});

function addMessage(msg, username, sender) {
    const item = document.createElement('li');
    item.classList.add('message');
    item.classList.add(sender === 'me' ? 'mine' : 'other');
    item.innerHTML = `<strong>${username}: </strong>${msg}`;
    messages.appendChild(item);  // Xabarni pastga qo'shamiz
    messages.scrollTop = messages.scrollHeight;  // Scrollni pastga tushiramiz
}

// Sahifa yangilanganda xabarlarni yuklash
window.onload = function() {
    fetch('/get_messages')
        .then(response => response.json())
        .then(data => {
            data.forEach(msg => {
                const sender = msg.username === username ? 'me' : 'other';
                addMessage(msg.text, msg.username, sender);
            });
        });
};