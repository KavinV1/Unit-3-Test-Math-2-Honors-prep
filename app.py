from flask import Flask, render_template_string, jsonify, request
import random
import math

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/mathquill/0.10.1/mathquill.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathquill/0.10.1/mathquill.min.js"></script>
    <title>Math Quiz Prep</title>
    <style>
        :root {
            --primary-color: #4a90e2;
            --success-color: #2ecc71;
            --error-color: #e74c3c;
            --background-color: #f5f6fa;
        }

        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0; 
            background-color: var(--background-color);
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        header h1 {
            color: var(--primary-color);
        }

        #question-container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .input-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        input[type="text"] {
            flex: 1;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }

        button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }

        #feedback-container {
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
        }

        .correct {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .incorrect {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        #stats-container {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 30px;
        }

        .stat-box {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            min-width: 150px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        sup {
            font-size: 0.6em;
            position: relative;
            top: -0.5em;
        }

        .math {
            font-size: 1.2em;
        }

        .solution-steps {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            line-height: 1.6;
        }

        .step {
            margin-bottom: 8px;
            padding-left: 20px;
        }
        .fraction {
            display: inline-block;
            vertical-align: middle;
            text-align: center;
            margin: 0 0.2em;
        }

        .numerator {
            display: block;
            border-bottom: 1px solid;
            padding: 0 0.2em;
            margin-bottom: 2px; /* Add spacing between numerator and denominator */
        }

        .denominator {
            display: block;
            padding: 0 0.2em;
            margin-top: 2px; /* Add spacing between numerator and denominator */
        }

        .numerator sup, .denominator sup {
            position: relative;
            top: -0.5em;
            font-size: 0.8em;
            margin-left: 2px;
        }
        #math-input {
            width: 100%;
            min-height: 40px;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-bottom: 10px;
            padding: 5px;
        }

        #math-keyboard {
            display: grid;
            gap: 5px;
            margin-bottom: 10px;
        }

        .keyboard-row {
            display: flex;
            gap: 5px;
        }

        .math-btn {
            padding: 8px 15px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            color: black;  /* Add this line */
            font-weight: bold;  /* Optional: makes text more visible */
        }

        .math-btn:hover {
            background: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Math Quiz Prep</h1>
            <p>Unit 3: Radical Exponents</p>
        </header>

        <main>
            <div id="question-container">
                <h2>Question:</h2>
                <p id="question-text" class="math"></p>
                <div class="input-group">
                    <button onclick="loadNextQuestion()" id="next-btn" style="display: none;">Next Question</button>
                    <input type="text" id="answer-input" style="display: none;">
                    <div id="math-input"></div>
                    <div id="math-keyboard">
                        <div class="keyboard-row">
                            <button class="math-btn" data-cmd="^">x^n</button>
                            <button class="math-btn" data-cmd="sqrt">√</button>
                            <button class="math-btn" onclick="handleNthRoot()">ⁿ√x</button>
                        </div>
                    </div>
                    <button onclick="checkAnswer()" id="submit-btn">Submit</button>
                </div>
            </div>

            <div id="feedback-container"></div>

            <div id="stats-container">
                <div class="stat-box">
                    <h3>Attempts Left</h3>
                    <p id="attempts">2</p>
                </div>
                <div class="stat-box">
                    <h3>Score</h3>
                    <p id="score">0</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        var MQ = MathQuill.getInterface(2);
        $(document).ready(function() {
            loadQuestion();
            const mathInput = document.getElementById('math-input');
            mathField = MQ.MathField(mathInput, {
                handlers: {
                    edit: function() {},
                    enter: function() {
                        checkAnswer();
                    }
                },
                autoCommands: 'sqrt'
            });
        });
        let currentQuestion = null;
        let attempts = 2;
        let score = 0;
        let mathField;

        document.addEventListener('DOMContentLoaded', function() {
            const mathInput = document.getElementById('math-input');
            mathField = MQ.MathField(mathInput, {
                handlers: {
                    edit: function() {},
                    enter: function() {
                        checkAnswer();
                    }
                },
                autoCommands: 'sqrt'
            });
            
            // Initialize keyboard buttons
            document.querySelectorAll('.math-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const cmd = btn.getAttribute('data-cmd');
                    switch(cmd) {
                        case '^':
                            mathField.cmd('^');
                            break;
                        case 'sqrt':
                            mathField.cmd('\\sqrt');
                            break;
                    }
                    mathField.focus();
                });
            });
            
            // Load first question
            loadQuestion();
        });

        function handleNthRoot() {
            const rootValue = prompt('Enter the root value (e.g., 3 for cube root):');
            if (rootValue) {
                mathField.write(`{}^${rootValue}√{}`);
                mathField.keystroke('Right');
                mathField.focus();
            }
        }

        function loadNextQuestion() {
            attempts = 2; // Reset attempts
            document.getElementById('attempts').textContent = attempts;
            document.getElementById('next-btn').style.display = 'none';
            document.getElementById('submit-btn').style.display = 'block';
            loadQuestion();
        }

        function showNextButton() {
            const nextBtn = document.getElementById('next-btn');
            const submitBtn = document.getElementById('submit-btn');
            nextBtn.style.display = 'block';
            submitBtn.style.display = 'none';
        }


        async function loadQuestion() {
            try {
                const response = await fetch('/api/question');
                if (!response.ok) throw new Error('Network response was not ok');
                currentQuestion = await response.json();
                document.getElementById('question-text').innerHTML = currentQuestion.question;
                attempts = 2;
                document.getElementById('attempts').textContent = attempts;
                document.getElementById('feedback-container').innerHTML = '';
                if (mathField) mathField.latex('');
            } catch (error) {
                console.error('Error loading question:', error);
                document.getElementById('question-text').innerHTML = 'Error loading question. Please refresh.';
            }
        }


        async function checkAnswer() {
            // If attempts are 0, don't process any more answers until next question
            if (attempts === 0) {
                return;
            }

            const userAnswer = mathField.latex();
            if (!userAnswer.trim()) {
                alert('Please enter an answer');
                return;
            }

            try {
                const response = await fetch('/api/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question: currentQuestion,
                        answer: userAnswer
                    })
                });
                
                const result = await response.json();
                const feedbackContainer = document.getElementById('feedback-container');
                
                if (result.correct) {
                    feedbackContainer.innerHTML = `
                        <div class="correct">
                            <h3>✓ Correct!</h3>
                            <div class="solution-steps">
                                ${result.explanation}
                            </div>
                        </div>
                    `;
                    score += 1;
                    document.getElementById('score').textContent = score;
                    showNextButton();
                } else {
                    attempts -= 1;
                    document.getElementById('attempts').textContent = attempts;
                    
                    if (attempts === 0) {
                        feedbackContainer.innerHTML = `
                            <div class="incorrect">
                                <h3>✗ Incorrect</h3>
                                <p>The correct answer is: ${result.correct_answer}</p>
                                <h4>Step-by-Step Solution:</h4>
                                <div class="solution-steps">
                                    ${result.explanation}
                                </div>
                            </div>
                        `;
                        showNextButton();
                    } else {
                        feedbackContainer.innerHTML = `
                            <div class="incorrect">
                                <h3>✗ Try Again</h3>
                                <p>You have ${attempts} attempt(s) left.</p>
                            </div>
                        `;
                    }
                }
            } catch (error) {
                console.error('Error checking answer:', error);
            }
        }

        document.getElementById('answer-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                checkAnswer();
            }
        });
        
        loadQuestion()
    </script>
</body>
</html>
'''

class QuestionGenerator:

    @staticmethod
    def format_fraction(num, den):
        return f'<span class="fraction"><span class="numerator">{num}</span><span class="denominator">{den}</span></span>'
    @staticmethod
    def perfect_square_factoring():
        num = random.randint(12, 50)
        squares = [i*i for i in range(1, int(math.sqrt(num)) + 1)]
        for square in reversed(squares):
            if num % square == 0:
                steps = [
                    f"1. Find the factors of {num}",
                    f"2. Look for the largest perfect square factor",
                    f"3. {square} is a perfect square ({int(math.sqrt(square))}² = {square})",
                    f"4. {num} ÷ {square} = {num//square}",
                    f"5. Therefore, {num} = {square} × {num//square}"
                ]
                return {
                    'type': 'perfect_square_factoring',
                    'question': f'Write {num} as a product where one factor is a perfect square.',
                    'answer': f'{square}×{num//square}',
                    'explanation': '<br>'.join(steps)
                }
    @staticmethod
    def cube_root_factoring():
        num = random.randint(24, 100)
        cubes = [i**3 for i in range(1, int(num**(1/3)) + 1)]
        for cube in reversed(cubes):
            if num % cube == 0:
                steps = [
                    f"1. Find the factors of {num}",
                    f"2. Look for the largest perfect cube factor",
                    f"3. {cube} is a perfect cube ({int(round(cube**(1/3)))}³ = {cube})",
                    f"4. {num} ÷ {cube} = {num//cube}",
                    f"5. Therefore, {num} = {cube} × {num//cube}"
                ]
                return {
                    'type': 'cube_root_factoring',
                    'question': f'Write {num} as a product where one factor is a perfect cube.',
                    'answer': f'{cube}×{num//cube}',
                    'explanation': '<br>'.join(steps)
                }

    @staticmethod
    def exponent_rules():
        base = random.choice(['x', 'a', 'b'])
        exp1 = random.randint(1, 5)
        exp2 = random.randint(1, 5)
        operation = random.choice(['product', 'quotient', 'power'])
        
        if operation == 'product':
            steps = [
                f"1. Using the product rule: {base}<sup>m</sup> × {base}<sup>n</sup> = {base}<sup>(m+n)</sup>",
                f"2. Substitute the values: {base}<sup>{exp1}</sup> × {base}<sup>{exp2}</sup>",
                f"3. Add the exponents: {exp1} + {exp2} = {exp1+exp2}",
                f"4. Therefore, {base}<sup>{exp1}</sup> × {base}<sup>{exp2}</sup> = {base}<sup>{exp1+exp2}</sup>"
            ]
            return {
                'type': 'exponent_rules',
                'question': f'Simplify: {base}<sup>{exp1}</sup> × {base}<sup>{exp2}</sup>',
                'answer': f'{base}<sup>{exp1+exp2}</sup>',
                'explanation': '<br>'.join(steps)
            }
        elif operation == 'quotient':
            steps = [
                f"1. Using the quotient rule: {base}<sup>m</sup> ÷ {base}<sup>n</sup> = {base}<sup>(m-n)</sup>",
                f"2. Substitute the values: {base}<sup>{exp1}</sup> ÷ {base}<sup>{exp2}</sup>",
                f"3. Subtract the exponents: {exp1} - {exp2} = {exp1-exp2}",
                f"4. Therefore, {base}<sup>{exp1}</sup> ÷ {base}<sup>{exp2}</sup> = {base}<sup>{exp1-exp2}</sup>"
            ]
            return {
                'type': 'exponent_rules',
                'question': f'Simplify: <div class="fraction"><span class="numerator">{base}<sup>{exp1}</sup></span><span class="denominator">{base}<sup>{exp2}</sup></span></div>',
                'answer': f'{base}<sup>{exp1-exp2}</sup>',
                'explanation': '<br>'.join(steps)
            }
        else:  # power
            steps = [
                f"1. Using the power rule: ({base}<sup>m</sup>)<sup>n</sup> = {base}<sup>(m×n)</sup>",
                f"2. Substitute the values: ({base}<sup>{exp1}</sup>)<sup>{exp2}</sup>",
                f"3. Multiply the exponents: {exp1} × {exp2} = {exp1*exp2}",
                f"4. Therefore, ({base}<sup>{exp1}</sup>)<sup>{exp2}</sup> = {base}<sup>{exp1*exp2}</sup>"
            ]
            return {
                'type': 'exponent_rules',
                'question': f'Simplify: ({base}<sup>{exp1}</sup>)<sup>{exp2}</sup>',
                'answer': f'{base}<sup>{exp1*exp2}</sup>',
                'explanation': '<br>'.join(steps)
            }

    @staticmethod
    def rational_exponents():
        # Use perfect powers to ensure whole number results
        perfect_powers = {
            2: [4, 16, 25, 36, 49, 64, 81, 100],  # perfect squares
            3: [8, 27, 64, 125],  # perfect cubes
            4: [16, 81, 256]  # perfect fourth powers
        }
        
        power = random.choice([2, 3, 4])
        base = random.choice(perfect_powers[power])
        result = base ** (1/power)
        
        steps = [
            f"1. The expression {base}<sup>{1}/{power}</sup> means finding the {power}th root of {base}",
            f"2. This is equivalent to finding what number, when raised to the {power}th power, equals {base}",
            f"3. {result}<sup>{power}</sup> = {base}",
            f"4. Therefore, {base}<sup>{1}/{power}</sup> = {int(result)}"
        ]
        
        return {
            'type': 'rational_exponents',
            'question': f'Simplify: {base}<sup>{1}/{power}</sup>',
            'answer': f'{int(result)}',
            'explanation': '<br>'.join(steps)
        }

    @staticmethod
    def square_root_simplification():
        perfect_square = random.randint(1, 10) ** 2
        multiplier = random.randint(2, 5)
        number = perfect_square * multiplier
        
        # Check if the entire number is a perfect square
        root = math.sqrt(number)
        if root.is_integer():
            steps = [
                f"1. Check if {number} is a perfect square",
                f"2. √{number} = {int(root)} because {int(root)}² = {number}",
                f"3. Therefore, √{number} = {int(root)}"
            ]
            return {
                'type': 'square_root_simplification',
                'question': f'Simplify: √{number}',
                'answer': f'{int(root)}',
                'explanation': '<br>'.join(steps)
            }
        else:
            steps = [
                f"1. Find the largest perfect square factor of {number}",
                f"2. {number} = {perfect_square} × {multiplier}",
                f"3. {perfect_square} is a perfect square ({int(math.sqrt(perfect_square))}² = {perfect_square})",
                f"4. √{number} = √({perfect_square} × {multiplier})",
                f"5. = √{perfect_square} × √{multiplier}",
                f"6. = {int(math.sqrt(perfect_square))}√{multiplier}"
            ]
            return {
                'type': 'square_root_simplification',
                'question': f'Simplify: √{number}',
                'answer': f'{int(math.sqrt(perfect_square))}√{multiplier}',
                'explanation': '<br>'.join(steps)
            }

    @staticmethod
    def radical_multiplication():
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        den1 = random.choice(['x', 'y', 'm'])
        den2 = random.choice(['a', 'b', 'n'])
        
        frac1 = QuestionGenerator.format_fraction(num1, den1)
        frac2 = QuestionGenerator.format_fraction(num2, den2)
        result_frac = QuestionGenerator.format_fraction(f"{num1*num2}", f"{den1}{den2}")
        
        steps = [
            f"1. Multiply terms under the radicals: √{frac1} × √{frac2}",
            f"2. Use the product rule for radicals: √({frac1} × {frac2})",
            f"3. Multiply numerators and denominators: √{result_frac}"
        ]
        
        return {
            'type': 'radical_multiplication',
            'question': f'Simplify: √{frac1} × √{frac2}',
            'answer': f'√{result_frac}',
            'explanation': '<br>'.join(steps)
        }

    @staticmethod
    def generate_word_problem():
        problem_types = [
            {
                'type': 'growth_model',
                'template': lambda h, r: f'A bacterial culture grows according to the formula P(t) = {h}t<sup>{r}</sup>, where t is time in hours. Calculate the population after 2 hours. Round all intermediate calculations to 4 decimal places and the final answer to the nearest whole number.',
                'values': {'h': random.randint(100, 500), 'r': random.choice([0.5])},  # Simplified to just use 0.5
                'formula': lambda h, r: round(h * (round(2 ** r, 4)), 0),  # Round intermediate and final results
                'steps': lambda h, r: [
                    f"1. Use the formula: P(t) = {h}t<sup>{r}</sup>",
                    f"2. Substitute t = 2: P(2) = {h}(2)<sup>{r}</sup>",
                    f"3. Calculate 2<sup>{r}</sup> = {round(2**r, 4)} (rounded to 4 decimal places)",
                    f"4. Multiply: {h} × {round(2**r, 4)} = {round(h * (round(2**r, 4)), 0)} (rounded to nearest whole number)"
                ]
            },
            {
                'type': 'growth_model',
                'template': lambda h, r: f'A bacterial culture grows according to the formula P(t) = {h}t<sup>{r}</sup>, where t is time in hours. Calculate the population after 2 hours. Round to the nearest whole number.',
                'values': {'h': random.randint(100, 500), 'r': random.choice([0.5, 0.25, 0.75])},
                'formula': lambda h, r: h * (2 ** r),
                'steps': lambda h, r: [
                    f"1. Use the formula: P(t) = {h}t<sup>{r}</sup>",
                    f"2. Substitute t = 2: P(2) = {h}(2)<sup>{r}</sup>",
                    f"3. Calculate 2<sup>{r}</sup> = {round(2**r, 4)}",
                    f"4. Multiply: {h} × {round(2**r, 4)} = {round(h * (2**r))}"
                ]
            },
            {
                'type': 'metabolic_rate',
                'template': lambda w: f'A person\'s daily caloric need (C) is modeled by C = 90w<sup>2/3</sup>, where w is weight in kilograms. Calculate the daily caloric need for someone weighing {w} kg. Round to the nearest calorie.',
                'values': {'w': random.randint(45, 100)},
                'formula': lambda w: 90 * (w ** (2/3)),
                'steps': lambda w: [
                    f"1. Use the formula: C = 90w<sup>2/3</sup>",
                    f"2. Substitute w = {w}: C = 90({w})<sup>2/3</sup>",
                    f"3. Calculate {w}<sup>2/3</sup> = {round(w**(2/3), 4)}",
                    f"4. Multiply: 90 × {round(w**(2/3), 4)} = {round(90 * (w**(2/3)))} calories"
                ]
            }
        ]
        
        chosen_problem = random.choice(problem_types)
        values = chosen_problem['values']
        result = chosen_problem['formula'](**values)
        steps = chosen_problem['steps'](**values)
        
        return {
            'type': 'word_problem',
            'question': chosen_problem['template'](**values),
            'answer': f'{round(result, 1)}',
            'explanation': '<br>'.join(steps)
        }

def generate_question():
    generators = [
        QuestionGenerator.perfect_square_factoring,
        QuestionGenerator.rational_exponents,
        QuestionGenerator.square_root_simplification,
        QuestionGenerator.generate_word_problem,
        QuestionGenerator.cube_root_factoring,
        QuestionGenerator.exponent_rules
    ]
    
    # Remove radical_multiplication from the list temporarily until fixed
    question = random.choice(generators)()
    return question

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/question', methods=['GET'])
def get_question():
    return jsonify(generate_question())

@app.route('/api/check', methods=['POST'])
def check_answer():
    data = request.get_json()
    user_answer = data['answer'].strip()
    correct_answer = data['question']['answer']
    
    def normalize_answer(answer):
        # Remove all spaces and LaTeX formatting
        answer = answer.replace(' ', '')
        answer = answer.replace('\\', '')
        answer = answer.replace('cdot', '*')
        answer = answer.replace('times', '*')
        
        # Split by multiplication operator and sort parts
        if '*' in answer or '×' in answer:
            parts = answer.replace('×', '*').split('*')
            parts = [p.strip() for p in parts]
            # Sort parts to handle commutative property
            parts.sort()
            return '*'.join(parts)
        
        # Handle superscript notation
        if '^' in answer:
            return answer
        
        # Handle HTML sup tags
        if '<sup>' in answer:
            base = answer.split('<sup>')[0]
            exp = answer.split('<sup>')[1].split('</sup>')[0]
            return f"{base}^{exp}"
            
        return answer
    
    normalized_user = normalize_answer(user_answer)
    normalized_correct = normalize_answer(correct_answer)
    
    is_correct = normalized_user == normalized_correct
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct_answer,
        'explanation': data['question']['explanation']
    })



if __name__ == '__main__':
    app.run(debug=True)
