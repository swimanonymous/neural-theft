from flask import Flask, render_template, request
from transformers import pipeline

# Initialize the Flask app
app = Flask(__name__)

# Load pre-trained summarization model for generating insights
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to encrypt a message using Caesar Cipher
def encrypt_caesar_cipher(message, key):
    """Encrypt the given message using Caesar Cipher with a provided key."""
    encrypted = ""
    for char in message:
        if char.isalpha():
            shift = key % 26
            new_char = chr((ord(char.lower()) - 97 + shift) % 26 + 97)
            encrypted += new_char.upper() if char.isupper() else new_char
        else:
            encrypted += char
    return encrypted

# Function to decrypt a message using Caesar Cipher
def decrypt_caesar_cipher(message, key):
    """Decrypt the given message using Caesar Cipher with a provided key."""
    decrypted = ""
    for char in message:
        if char.isalpha():
            shift = key % 26
            new_char = chr((ord(char.lower()) - 97 - shift + 26) % 26 + 97)
            decrypted += new_char.upper() if char.isupper() else new_char
        else:
            decrypted += char
    return decrypted

# Function to generate a summary for a given text
def generate_summary(text):
    """Generate a concise summary for the decrypted message."""
    try:
        summary_result = summarizer(text, max_length=500, min_length=50, do_sample=False)
        return summary_result[0]["summary_text"]
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Flask route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    """Render the homepage and handle encryption/decryption."""
    result1 = ""
    result = ""
    summary = ""
    message = ""

    if request.method == "POST":
        message = request.form.get("message", "")
        key = request.form.get("key", "").strip()
        action = request.form.get("action", "")

        # Handle key validation
        try:
            key = int(key) if key else None
        except ValueError:
            return render_template("index.html", summary="Invalid key. Please provide a numeric value.")

        # Encrypt or decrypt based on user action
        if action == "Encrypt":
            key = key or 3
            result1 = encrypt_caesar_cipher(message, key)
        elif action == "Decrypt":
            key = key or 3
            result = decrypt_caesar_cipher(message, key)
            if result:
                summary = generate_summary(result)

    return render_template("index.html", result1=result1, result=result, summary=summary, message=message)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
