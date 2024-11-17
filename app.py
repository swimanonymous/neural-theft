from flask import Flask, render_template, request
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Load pre-trained summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Caesar Cipher Encryption
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

# Caesar Cipher Decryption
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

# Generate summary using a pre-trained model
def generate_summary(text):
    """Generate a concise summary of the decrypted message."""
    try:
        summary_result = summarizer(text, max_length=500, min_length=50, do_sample=False)
        summary = summary_result[0]["summary_text"]
        # Truncate if necessary
        if len(summary.split()) > 500:
            summary = " ".join(summary.split()[:500]) + "..."
        return summary
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Frequency-based scoring for English text
def english_frequency_score(text):
    """Calculate a frequency-based score for English text."""
    english_freq = "etaoinshrdlcumwfgypbvkjxqz"
    score = sum([english_freq.index(c.lower()) if c.lower() in english_freq else 0 for c in text])
    return score

# Flask Routes
@app.route("/", methods=["GET", "POST"])
def index():
    """Main route for the web application."""
    result1 = ""
    result = ""
    insights = []
    summary = ""
    message = ""

    if request.method == "POST":
        # Get data from the form
        message = request.form.get("message", "")
        key = request.form.get("key", "").strip()
        action = request.form.get("action", "")

        # Validate key input
        try:
            key = int(key) if key else None
        except ValueError:
            return render_template(
                "index.html",
                result1=result1,
                result=result,
                insights=insights,
                summary="Invalid key. Please provide a numeric value.",
                message=message,
            )

        # Perform the chosen action
        if action == "Encrypt":
            key = key or 3  # Default key is 3
            result1 = encrypt_caesar_cipher(message, key)
        elif action == "Decrypt":
            if key is not None:
                result = decrypt_caesar_cipher(message, key)
            else:
                # Decrypt with all possible keys and find the most probable message
                possible_decryptions = [
                    {"key": i, "text": decrypt_caesar_cipher(message, i)}
                    for i in range(26)
                ]
                for decryption in possible_decryptions:
                    decryption["english_score"] = english_frequency_score(decryption["text"])

                # Sort predictions by score (higher is better)
                insights = sorted(possible_decryptions, key=lambda x: x["english_score"], reverse=False)
                best_result = insights[0]
                result = best_result["text"]
                
                # Generate summary for the best result
                summary = generate_summary(result)

    return render_template(
        "index.html", result1=result1, result=result, insights=insights, summary=summary, message=message
    )


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
