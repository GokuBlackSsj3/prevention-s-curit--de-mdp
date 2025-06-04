const questions = [
    {
        question: "Un mot de passe court et simple est-il sécurisé ?",
        answers: [
            { text: "Oui, c'est plus facile à retenir", correct: false },
            { text: "Non, il faut au moins 20 caractères avec des lettres, chiffres et symboles", correct: true },
            { text: "Oui, si vous changez souvent de mot de passe", correct: false },
            { text: "Non, mais un mot de passe simple avec des majuscules suffit", correct: false }
        ],
        explanation: "Un mot de passe doit être long (minimum 20 caractères) et complexe pour être sécurisé. Utilisez un mélange de lettres majuscules, minuscules, chiffres et caractères spéciaux."
    },
    {
        question: "Quelle est la meilleure façon de stocker ses mots de passe ?",
        answers: [
            { text: "Dans un fichier texte crypté sur l'ordinateur", correct: false },
            { text: "Dans un gestionnaire de mots de passe sécurisé", correct: true },
            { text: "Dans un carnet papier", correct: false },
            { text: "Dans le navigateur si le PC est personnel", correct: false }
        ],
        explanation: "Un gestionnaire de mots de passe sécurisé est la meilleure solution pour stocker vos mots de passe. N'utilisez jamais un fichier texte non protégé ou un carnet non sécurisé."
    },
    {
        question: "Est-il sécurisé d'envoyer un mot de passe par email ou SMS ?",
        answers: [
            { text: "Non, ne jamais partager de mot de passe par email ou SMS", correct: true },
            { text: "Oui, si le destinataire est de confiance", correct: false },
            { text: "Oui, si le message est chiffré", correct: false },
            { text: "Non, sauf en cas d'urgence", correct: false }
        ],
        explanation: "Ne partagez jamais vos mots de passe par email ou SMS. Ces moyens de communication ne sont pas sécurisés et peuvent être interceptés."
    },
    {
        question: "La double authentification est-elle importante ?",
        answers: [
            { text: "Non, c'est une perte de temps", correct: false },
            { text: "Oui, c'est une couche de sécurité essentielle qui protège même si le mot de passe est compromis", correct: true },
            { text: "Seulement si vous utilisez un mot de passe faible", correct: false },
            { text: "Seulement pour les comptes bancaires", correct: false }
        ],
        explanation: "La double authentification ajoute une couche de sécurité cruciale. Même si quelqu'un connaît votre mot de passe, il ne pourra pas accéder à votre compte sans le second facteur. Elle est recommandée pour tous les comptes importants."
    },
    {
        question: "À quelle fréquence faut-il changer ses mots de passe ?",
        answers: [
            { text: "Jamais si le mot de passe est fort", correct: false },
            { text: "Régulièrement, tous les 3 mois, et immédiatement en cas de suspicion de compromission", correct: true },
            { text: "Seulement si vous recevez un email de sécurité", correct: false },
            { text: "Une fois par an suffit", correct: false }
        ],
        explanation: "Changez vos mots de passe régulièrement (tous les 3 mois) et immédiatement si vous suspectez qu'ils ont été compromis. Ne vous fiez pas uniquement aux notifications, soyez proactif."
    }
];

let currentQuestionIndex = 0;
let score = 0;
let username = '';

// Get DOM elements
const startContainer = document.getElementById('start-container');
const quizContainer = document.getElementById('quiz-container');
const questionElement = document.getElementById('question');
const answerButtonsElement = document.getElementById('answer-buttons');
const nextButton = document.getElementById('next-btn');
const resultContainer = document.getElementById('result-container');
const scoreElement = document.getElementById('score');
const restartButton = document.getElementById('restart-btn');
const startButton = document.getElementById('start-btn');
const usernameInput = document.getElementById('username-input');

// AI Chat elements
const aiToggleButton = document.getElementById('ai-toggle');
const aiChat = document.getElementById('ai-chat');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatButton = document.getElementById('chat-btn');

// AI Chat functionality
aiToggleButton.addEventListener('click', () => {
    aiChat.classList.toggle('hide');
});

async function sendMessage(message) {
    try {
        const response = await fetch('https://prevention-s-curit-de-mdp.onrender.com/api/ai-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: username
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error:', error);
        return "Désolé, je rencontre des difficultés techniques. Veuillez réessayer plus tard.";
    }
}

function addMessageToChat(message, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message');
    messageDiv.classList.add(isUser ? 'user-message' : 'ai-message');
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatButton.addEventListener('click', async () => {
    const message = chatInput.value.trim();
    if (message) {
        addMessageToChat(message, true);
        chatInput.value = '';
        chatInput.disabled = true;
        chatButton.disabled = true;

        const response = await sendMessage(message);
        addMessageToChat(response, false);

        chatInput.disabled = false;
        chatButton.disabled = false;
        chatInput.focus();
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatButton.click();
    }
});

// Start button event listener
startButton.addEventListener('click', () => {
    username = usernameInput.value.trim();
    if (username) {
        startContainer.classList.add('hide');
        quizContainer.classList.remove('hide');
        startQuiz();
    } else {
        alert('Veuillez entrer votre nom pour commencer');
    }
});

function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    nextButton.innerHTML = 'Question Suivante';
    showQuestion();
}

function showQuestion() {
    resetState();
    let currentQuestion = questions[currentQuestionIndex];
    questionElement.innerHTML = currentQuestion.question;

    currentQuestion.answers.forEach(answer => {
        const button = document.createElement('button');
        button.innerHTML = answer.text;
        button.classList.add('btn');
        answerButtonsElement.appendChild(button);
        if (answer.correct) {
            button.dataset.correct = answer.correct;
        }
        button.addEventListener('click', selectAnswer);
    });

    resultContainer.classList.add('hide');
}

function resetState() {
    nextButton.style.display = 'none';
    while (answerButtonsElement.firstChild) {
        answerButtonsElement.removeChild(answerButtonsElement.firstChild);
    }
}

function selectAnswer(e) {
    const selectedButton = e.target;
    const correct = selectedButton.dataset.correct === 'true';
    if (correct) {
        score++;
    }

    Array.from(answerButtonsElement.children).forEach(button => {
        button.disabled = true;
        if (button.dataset.correct === 'true') {
            button.classList.add('correct');
        } else {
            button.classList.add('wrong');
        }
    });

    // Show explanation
    const explanation = document.createElement('p');
    explanation.classList.add('explanation');
    explanation.innerHTML = questions[currentQuestionIndex].explanation;
    answerButtonsElement.appendChild(explanation);

    nextButton.style.display = 'block';
}

function showScore() {
    resetState();
    questionElement.innerHTML = `Quiz terminé, ${username} !`;
    resultContainer.classList.remove('hide');
    scoreElement.innerHTML = `Score: ${score}/${questions.length}`;
    nextButton.style.display = 'none';

    // Send survey results to backend
    const answers = questions.map(q => {
        // Find the selected answer text for each question
        const buttons = answerButtonsElement.querySelectorAll('button');
        for (const btn of buttons) {
            if (btn.dataset.correct === 'true') {
                return btn.innerText;
            }
        }
        return '';
    });

    fetch('https://prevention-s-curit-de-mdp.onrender.com/api/send-survey-results', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            score: score,
            total: questions.length,
            answers: answers
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Survey results sent:', data);
    })
    .catch((error) => {
        console.error('Error sending survey results:', error);
    });
}

function handleNextButton() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion();
    } else {
        showScore();
    }
}

nextButton.addEventListener('click', handleNextButton);
restartButton.addEventListener('click', () => {
    quizContainer.classList.add('hide');
    startContainer.classList.remove('hide');
    usernameInput.value = '';
});
