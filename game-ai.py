import random
import json
import webbrowser
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Words list for the guessing game
word_list = ["rizz", "ohio", "sigma", "tiktok", "skibidi", "gyatt", "grimace", "fanum", "mewing", "goated"]

class GameState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.word = random.choice(word_list)
        self.guessed_word = ['_'] * len(self.word)
        self.attempts_left = 10
        self.guessed_letters = []
        self.game_over = False
        self.won = False
        
    def guess(self, letter):
        if self.game_over:
            return
        
        letter = letter.lower().strip()
        if len(letter) != 1 or not letter.isalpha():
            return
            
        if letter in self.guessed_letters:
            return
            
        self.guessed_letters.append(letter)
        
        if letter in self.word:
            for i in range(len(self.word)):
                if self.word[i] == letter:
                    self.guessed_word[i] = letter
            if '_' not in self.guessed_word:
                self.game_over = True
                self.won = True
        else:
            self.attempts_left -= 1
            if self.attempts_left <= 0:
                self.game_over = True
                self.won = False
                
    def to_dict(self):
        data = {
            "guessed_word": self.guessed_word,
            "attempts_left": self.attempts_left,
            "guessed_letters": self.guessed_letters,
            "word_length": len(self.word),
            "game_over": self.game_over,
            "won": self.won
        }
        if self.game_over:
            data["word"] = self.word
        return data

# Global game state instance
game_state = GameState()

# Embedded Single Page Application (HTML, CSS, JS)
HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Slang Guesser - Level Up</title>
    <meta name="description" content="A premium word-guessing game featuring modern slang words, dynamic SVG animations, retro synthesized audio, and glowing glassmorphic design.">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        /* Modern Reset and CSS Variables */
        :root {
            --primary: #a855f7;
            --primary-glow: rgba(168, 85, 247, 0.4);
            --secondary: #3b82f6;
            --secondary-glow: rgba(59, 130, 246, 0.4);
            --success: #22c55e;
            --danger: #ef4444;
            --bg-dark: #090514;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: radial-gradient(circle at center, #1b0e2f 0%, var(--bg-dark) 100%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
            overflow-x: hidden;
        }

        /* Container & Glassmorphism Card */
        .game-container {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 24px;
            width: 100%;
            max-width: 800px;
            padding: 40px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 30px;
            position: relative;
            z-index: 2;
        }

        /* Ambient Glow Blobs */
        .glow-blob {
            position: absolute;
            width: 300px;
            height: 300px;
            background: var(--primary);
            filter: blur(120px);
            opacity: 0.15;
            border-radius: 50%;
            z-index: 1;
            pointer-events: none;
        }
        .glow-blob-1 { top: 10%; left: 10%; background: var(--primary); }
        .glow-blob-2 { bottom: 10%; right: 10%; background: var(--secondary); }

        /* Header / Title */
        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 2px;
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(168, 85, 247, 0.3);
            text-align: center;
        }

        .tagline {
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-top: -15px;
            text-align: center;
        }

        /* Game Layout Splitting */
        .game-area {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            width: 100%;
        }

        @media (max-width: 768px) {
            .game-area {
                grid-template-columns: 1fr;
            }
        }

        /* Visual Display (Hangman Box) */
        .visual-box {
            display: flex;
            justify-content: center;
            align-items: center;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.04);
            padding: 20px;
            min-height: 240px;
        }

        .hangman-svg {
            width: 200px;
            height: 200px;
        }

        .hangman-svg path, .hangman-svg line, .hangman-svg circle {
            stroke: var(--text-main);
            stroke-width: 4;
            stroke-linecap: round;
            stroke-linejoin: round;
            fill: none;
            transition: opacity 0.3s;
            opacity: 0.1; /* Default hidden parts */
        }

        /* Highlighting and Neon style for active hangman elements */
        .hangman-svg .scaffold {
            opacity: 0.3;
            stroke: var(--text-muted);
        }

        .hangman-svg .draw-part {
            opacity: 1;
            stroke: var(--secondary);
            filter: drop-shadow(0 0 4px var(--secondary-glow));
        }

        .hangman-svg .dead-part {
            stroke: var(--danger) !important;
            filter: drop-shadow(0 0 6px var(--danger)) !important;
            opacity: 1;
        }

        /* Game Status details */
        .status-box {
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 20px;
        }

        .attempts-left {
            font-size: 1.1rem;
            color: var(--text-main);
        }
        .attempts-left span {
            font-weight: 800;
            color: var(--primary);
            font-size: 1.4rem;
            text-shadow: 0 0 10px var(--primary-glow);
        }

        /* Secret Word Display */
        .word-display {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
            margin: 20px 0;
        }

        .letter-slot {
            width: 45px;
            height: 55px;
            border-bottom: 3px solid var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8rem;
            font-weight: 800;
            text-transform: uppercase;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .letter-slot.revealed {
            border-bottom-color: var(--primary);
            color: var(--primary);
            text-shadow: 0 0 10px var(--primary-glow);
            transform: scale(1.05);
        }

        /* Keyboards Styling */
        .keyboard {
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
            margin-top: 10px;
        }

        .keyboard-row {
            display: flex;
            justify-content: center;
            gap: 6px;
        }

        .key-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-main);
            font-family: inherit;
            font-size: 1.1rem;
            font-weight: 600;
            text-transform: uppercase;
            border-radius: 8px;
            width: 40px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s ease;
            user-select: none;
        }

        .key-btn:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        }

        .key-btn:active:not(:disabled) {
            transform: translateY(0);
        }

        .key-btn:disabled {
            cursor: not-allowed;
            opacity: 0.3;
        }

        .key-btn.correct {
            background: rgba(34, 197, 94, 0.2);
            border-color: var(--success);
            color: var(--success);
            text-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
            opacity: 1 !important;
        }

        .key-btn.wrong {
            background: rgba(239, 68, 68, 0.15);
            border-color: var(--danger);
            color: var(--danger);
            opacity: 0.4 !important;
        }

        /* Game Over Dialog overlay inside the card */
        .overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(9, 5, 20, 0.95);
            backdrop-filter: blur(8px);
            border-radius: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 20px;
            z-index: 10;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s ease;
        }

        .overlay.active {
            opacity: 1;
            pointer-events: all;
        }

        .overlay-title {
            font-size: 2.2rem;
            font-weight: 800;
        }

        .overlay-title.win {
            color: var(--success);
            text-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
        }

        .overlay-title.lose {
            color: var(--danger);
            text-shadow: 0 0 20px rgba(239, 68, 68, 0.4);
        }

        .overlay-text {
            color: var(--text-muted);
            font-size: 1.1rem;
            text-align: center;
        }

        .overlay-word {
            font-size: 2rem;
            font-weight: 800;
            color: var(--text-main);
            letter-spacing: 4px;
            text-transform: uppercase;
            margin: 10px 0;
        }

        .action-btn {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            border: none;
            color: white;
            font-family: inherit;
            font-size: 1.1rem;
            font-weight: 700;
            padding: 12px 28px;
            border-radius: 12px;
            cursor: pointer;
            box-shadow: 0 4px 15px var(--primary-glow);
            transition: all 0.3s ease;
        }

        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6);
        }

        .action-btn:active {
            transform: translateY(0);
        }

        /* Sound Control */
        .sound-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 1.5rem;
            transition: color 0.3s;
        }

        .sound-toggle:hover {
            color: var(--text-main);
        }

        /* Confetti Particles Canvas */
        #confetti-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 100;
        }
    </style>
</head>
<body>
    <div class="glow-blob glow-blob-1"></div>
    <div class="glow-blob glow-blob-2"></div>

    <canvas id="confetti-canvas"></canvas>

    <div class="game-container">
        <!-- Sound Toggle Button -->
        <button id="sound-btn" class="sound-toggle" title="Toggle Sound">🔊</button>

        <h1>Slang Guesser</h1>
        <p class="tagline">Level Up with AI Word Guessing Game</p>

        <!-- Game Area Grid -->
        <div class="game-area">
            <!-- Left Side: Visual Hangman Box -->
            <div class="visual-box">
                <svg class="hangman-svg" viewBox="0 0 200 200">
                    <!-- Scaffold (Permanent Parts) -->
                    <line class="scaffold" x1="20" y1="180" x2="180" y2="180" />
                    <line class="scaffold" x1="60" y1="180" x2="60" y2="20" />
                    <line class="scaffold" x1="60" y1="20" x2="140" y2="20" />
                    <line class="scaffold" x1="140" y1="20" x2="140" y2="45" />
                    
                    <!-- Hangman Parts (Indexed 1 to 10 for revealing) -->
                    <!-- 1. Ground Support Diagonal -->
                    <line id="hang-1" x1="60" y1="150" x2="90" y2="180" />
                    <!-- 2. Top Support Diagonal -->
                    <line id="hang-2" x1="60" y1="50" x2="90" y2="20" />
                    <!-- 3. Rope Knot -->
                    <circle id="hang-3" cx="140" cy="47" r="3" />
                    <!-- 4. Head -->
                    <circle id="hang-4" cx="140" cy="62" r="14" />
                    <!-- 5. Torso -->
                    <line id="hang-5" x1="140" y1="76" x2="140" y2="120" />
                    <!-- 6. Left Arm -->
                    <line id="hang-6" x1="140" y1="90" x2="115" y2="80" />
                    <!-- 7. Right Arm -->
                    <line id="hang-7" x1="140" y1="90" x2="165" y2="80" />
                    <!-- 8. Left Leg -->
                    <line id="hang-8" x1="140" y1="120" x2="120" y2="150" />
                    <!-- 9. Right Leg -->
                    <line id="hang-9" x1="140" y1="120" x2="160" y2="150" />
                    <!-- 10. Face details (Dead Eyes X X) -->
                    <path id="hang-10" d="M 133,58 L 137,62 M 137,58 L 133,62 M 143,58 L 147,62 M 147,58 L 143,62 M 136,69 Q 140,66 144,69" />
                </svg>
            </div>

            <!-- Right Side: Details & Live Data -->
            <div class="status-box">
                <div class="attempts-left">
                    Attempts Left: <span id="attempts-count">10</span>
                </div>
                <div class="word-display" id="word-container">
                    <!-- Dynamic Letter Slots -->
                </div>
            </div>
        </div>

        <!-- Virtual Keyboard -->
        <div class="keyboard" id="keyboard-container">
            <!-- Row 1 -->
            <div class="keyboard-row">
                <button class="key-btn" id="key-q">q</button>
                <button class="key-btn" id="key-w">w</button>
                <button class="key-btn" id="key-e">e</button>
                <button class="key-btn" id="key-r">r</button>
                <button class="key-btn" id="key-t">t</button>
                <button class="key-btn" id="key-y">y</button>
                <button class="key-btn" id="key-u">u</button>
                <button class="key-btn" id="key-i">i</button>
                <button class="key-btn" id="key-o">o</button>
                <button class="key-btn" id="key-p">p</button>
            </div>
            <!-- Row 2 -->
            <div class="keyboard-row">
                <button class="key-btn" id="key-a">a</button>
                <button class="key-btn" id="key-s">s</button>
                <button class="key-btn" id="key-d">d</button>
                <button class="key-btn" id="key-f">f</button>
                <button class="key-btn" id="key-g">g</button>
                <button class="key-btn" id="key-h">h</button>
                <button class="key-btn" id="key-j">j</button>
                <button class="key-btn" id="key-k">k</button>
                <button class="key-btn" id="key-l">l</button>
            </div>
            <!-- Row 3 -->
            <div class="keyboard-row">
                <button class="key-btn" id="key-z">z</button>
                <button class="key-btn" id="key-x">x</button>
                <button class="key-btn" id="key-c">c</button>
                <button class="key-btn" id="key-v">v</button>
                <button class="key-btn" id="key-b">b</button>
                <button class="key-btn" id="key-n">n</button>
                <button class="key-btn" id="key-m">m</button>
            </div>
        </div>

        <!-- Dialog Game Over Screen Overlay -->
        <div class="overlay" id="game-over-overlay">
            <h2 class="overlay-title" id="overlay-title">YOU WIN!</h2>
            <p class="overlay-text" id="overlay-reason">Congratulations! You solved the slang word.</p>
            <div class="overlay-word" id="overlay-secret-word">RIZZ</div>
            <button class="action-btn" id="play-again-btn">Play Another Round</button>
        </div>
    </div>

    <script>
        // Web Audio API Synthesizer Sound Engine
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        let soundEnabled = true;

        document.getElementById('sound-btn').addEventListener('click', () => {
            soundEnabled = !soundEnabled;
            document.getElementById('sound-btn').innerText = soundEnabled ? '🔊' : '🔇';
        });

        function playSynth(type) {
            if (!soundEnabled) return;
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }

            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            const now = audioCtx.currentTime;

            if (type === 'correct') {
                // Short bright chirp
                osc.type = 'sine';
                osc.frequency.setValueAtTime(440, now); // A4
                osc.frequency.exponentialRampToValueAtTime(880, now + 0.15); // A5
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
                osc.start(now);
                osc.stop(now + 0.15);
            } 
            else if (type === 'wrong') {
                // Short low buzz
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(180, now);
                osc.frequency.linearRampToValueAtTime(100, now + 0.25);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
                osc.start(now);
                osc.stop(now + 0.25);
            } 
            else if (type === 'win') {
                // Uplifting arpeggio
                const notes = [261.63, 329.63, 392.00, 523.25]; // C4, E4, G4, C5
                notes.forEach((freq, idx) => {
                    const singleOsc = audioCtx.createOscillator();
                    const singleGain = audioCtx.createGain();
                    singleOsc.connect(singleGain);
                    singleGain.connect(audioCtx.destination);
                    
                    singleOsc.type = 'sine';
                    singleOsc.frequency.setValueAtTime(freq, now + idx * 0.12);
                    
                    singleGain.gain.setValueAtTime(0.1, now + idx * 0.12);
                    singleGain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.12 + 0.4);
                    
                    singleOsc.start(now + idx * 0.12);
                    singleOsc.stop(now + idx * 0.12 + 0.4);
                });
            } 
            else if (type === 'lose') {
                // Dark descending drone
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(150, now);
                osc.frequency.linearRampToValueAtTime(60, now + 1.2);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.linearRampToValueAtTime(0.001, now + 1.2);
                osc.start(now);
                osc.stop(now + 1.2);
            }
        }

        // Confetti Particle Simulation
        const canvas = document.getElementById('confetti-canvas');
        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationFrameId;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        class ConfettiParticle {
            constructor() {
                this.x = canvas.width / 2;
                this.y = canvas.height / 2;
                const angle = Math.random() * Math.PI * 2;
                const speed = 3 + Math.random() * 8;
                this.vx = Math.cos(angle) * speed;
                this.vy = Math.sin(angle) * speed - 2; // Upwards bias
                this.size = 5 + Math.random() * 8;
                this.color = `hsl(${Math.random() * 360}, 85%, 60%)`;
                this.rotation = Math.random() * 360;
                this.rotationSpeed = -10 + Math.random() * 20;
                this.opacity = 1;
                this.gravity = 0.15;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.vy += this.gravity;
                this.rotation += this.rotationSpeed;
                this.opacity -= 0.01;
            }

            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate((this.rotation * Math.PI) / 180);
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = this.color;
                ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size);
                ctx.restore();
            }
        }

        function spawnConfetti() {
            cancelAnimationFrame(animationFrameId);
            particles = [];
            for (let i = 0; i < 150; i++) {
                particles.push(new ConfettiParticle());
            }
            animateConfetti();
        }

        function animateConfetti() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles = particles.filter(p => p.opacity > 0);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
            if (particles.length > 0) {
                animationFrameId = requestAnimationFrame(animateConfetti);
            }
        }

        // API Communications & Game Control
        const wordContainer = document.getElementById('word-container');
        const attemptsCount = document.getElementById('attempts-count');
        const overlay = document.getElementById('game-over-overlay');
        const overlayTitle = document.getElementById('overlay-title');
        const overlayReason = document.getElementById('overlay-reason');
        const overlaySecretWord = document.getElementById('overlay-secret-word');

        // Map characters to keyboard buttons
        const keys = document.querySelectorAll('.key-btn');

        async function initGame() {
            overlay.classList.remove('active');
            keys.forEach(k => {
                k.className = 'key-btn';
                k.disabled = false;
            });
            resetHangmanSVG();

            const res = await fetch('/api/start', { method: 'POST' });
            const data = await res.json();
            updateUI(data, false);
        }

        function resetHangmanSVG() {
            for (let i = 1; i <= 10; i++) {
                const el = document.getElementById(`hang-${i}`);
                if (el) {
                    el.className.baseVal = '';
                }
            }
        }

        function updateHangmanSVG(attemptsLeft, gameOver, won) {
            const wrongCount = 10 - attemptsLeft;
            
            // Loop through each part, reveal it if wrongCount >= index
            for (let i = 1; i <= 10; i++) {
                const el = document.getElementById(`hang-${i}`);
                if (el) {
                    if (i <= wrongCount) {
                        // Apply dead styles to everything if we lost
                        if (gameOver && !won) {
                            el.className.baseVal = 'dead-part';
                        } else {
                            el.className.baseVal = 'draw-part';
                        }
                    } else {
                        el.className.baseVal = '';
                    }
                }
            }
        }

        function updateUI(data, isGuessResponse) {
            // Update Word Slots
            wordContainer.innerHTML = '';
            data.guessed_word.forEach(char => {
                const slot = document.createElement('div');
                slot.className = 'letter-slot' + (char !== '_' ? ' revealed' : '');
                slot.innerText = char !== '_' ? char : '';
                wordContainer.appendChild(slot);
            });

            // Update Attempts Count
            const oldAttempts = parseInt(attemptsCount.innerText);
            attemptsCount.innerText = data.attempts_left;

            // Trigger click audio on guess
            if (isGuessResponse) {
                if (data.attempts_left < oldAttempts) {
                    playSynth('wrong');
                } else {
                    playSynth('correct');
                }
            }

            // Sync Hangman drawing
            updateHangmanSVG(data.attempts_left, data.game_over, data.won);

            // Sync Keyboard Visual State
            data.guessed_letters.forEach(letter => {
                const keyEl = document.getElementById(`key-${letter}`);
                if (keyEl) {
                    keyEl.disabled = true;
                    // Determine if correct or wrong
                    if (data.guessed_word.includes(letter) || (data.word && data.word.includes(letter))) {
                        keyEl.classList.add('correct');
                    } else {
                        keyEl.classList.add('wrong');
                    }
                }
            });

            // Check End Game
            if (data.game_over) {
                overlaySecretWord.innerText = data.word || '';
                if (data.won) {
                    overlayTitle.innerText = '🎉 YOU SOLVED IT!';
                    overlayTitle.className = 'overlay-title win';
                    overlayReason.innerText = 'Goated logic! You guessed the slang word.';
                    playSynth('win');
                    spawnConfetti();
                } else {
                    overlayTitle.innerText = '💀 GAME OVER';
                    overlayTitle.className = 'overlay-title lose';
                    overlayReason.innerText = "You got caught! The secret word was:";
                    playSynth('lose');
                }
                setTimeout(() => {
                    overlay.classList.add('active');
                }, 800);
            }
        }

        async function makeGuess(letter) {
            const keyEl = document.getElementById(`key-${letter}`);
            // Check if key exists and is not already disabled
            if (keyEl && keyEl.disabled) return;

            const res = await fetch('/api/guess', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ letter })
            });
            const data = await res.json();
            updateUI(data, true);
        }

        // Attach Click Listeners to Virtual Keys
        keys.forEach(btn => {
            btn.addEventListener('click', () => {
                const letter = btn.innerText.toLowerCase();
                makeGuess(letter);
            });
        });

        // Listen for Physical Keyboard Input
        document.addEventListener('keydown', (e) => {
            // Only capture single a-z character keypresses when not overlay active
            if (!overlay.classList.contains('active') && e.key.length === 1 && e.key.match(/[a-z]/i)) {
                makeGuess(e.key.toLowerCase());
            }
        });

        // Play Again Button Click Handler
        document.getElementById('play-again-btn').addEventListener('click', initGame);

        // Start initial round
        initGame();
    </script>
</body>
</html>
"""

# Custom Request Handler to route requests
class GameRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        else:
            self.send_error(404, "File not found")
            
    def do_POST(self):
        if self.path == '/api/start':
            game_state.reset()
            self.send_json_response(game_state.to_dict())
        elif self.path == '/api/guess':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                letter = data.get('letter', '')
                game_state.guess(letter)
                self.send_json_response(game_state.to_dict())
            except Exception as e:
                self.send_error(400, f"Invalid JSON: {str(e)}")
        else:
            self.send_error(404, "Endpoint not found")
            
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
            
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
        
    def log_message(self, format, *args):
        # Quiet down terminal requests logging for a clean CLI output
        pass

def open_browser():
    # Wait half a second for the server to start, then open the browser
    time.sleep(0.5)
    webbrowser.open("http://localhost:5000")

def main():
    # Start thread to open browser
    threading.Thread(target=open_browser, daemon=True).start()

    # Start local HTTP server
    server_address = ('127.0.0.1', 5000)
    httpd = HTTPServer(server_address, GameRequestHandler)
    print("\n=============================================")
    print("      [SLANG GUESSER WEB SERVER UP]          ")
    print("=============================================")
    print("Server running locally at: http://127.0.0.1:5000")
    print("Your browser should open automatically.")
    print("Press Ctrl+C in this terminal to stop the server.")
    print("=============================================\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server. Goodbye!")

if __name__ == "__main__":
    main()