from __future__ import annotations

import os
from typing import List, Tuple

from dotenv import load_dotenv
from flask import Flask, render_template, request

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None

load_dotenv()

app = Flask(__name__)


def topic_keywords(topic: str) -> dict:
    text = topic.strip().lower()
    library = {
        "python": {
            "explanation": "Python is a beginner-friendly programming language known for its simple syntax, readability, and powerful libraries. It is used for web development, automation, data analysis, machine learning, and scripting.",
            "takeaways": [
                "Python is easy to read and write.",
                "It is widely used across many industries.",
                "It supports both small scripts and large applications."
            ]
        },
        "ai": {
            "explanation": "Artificial intelligence is the field of building systems that can perform tasks that normally require human intelligence, such as pattern recognition, prediction, language understanding, and decision-making.",
            "takeaways": [
                "AI learns from data and patterns.",
                "It is used in automation, healthcare, recommendation systems, and more.",
                "Ethical use and good data are critical for responsible AI."
            ]
        },
        "machine learning": {
            "explanation": "Machine learning is a branch of AI that gives computers the ability to learn from data and improve over time without being explicitly programmed for every rule.",
            "takeaways": [
                "Machine learning relies on data to identify patterns.",
                "It helps automate predictions and decision-making.",
                "The quality of data affects the model's accuracy."
            ]
        },
        "cloud computing": {
            "explanation": "Cloud computing delivers computing resources such as storage, servers, and software over the internet instead of relying on local hardware.",
            "takeaways": [
                "Cloud services reduce the need for physical infrastructure.",
                "It enables scalable and flexible systems.",
                "It allows teams to deploy software faster and more efficiently."
            ]
        },
        "cybersecurity": {
            "explanation": "Cybersecurity is the practice of protecting computers, networks, and data from attacks, misuse, and damage.",
            "takeaways": [
                "Cybersecurity protects both personal and business systems.",
                "Threats can come from malware, phishing, and weak system configuration.",
                "Strong security practices reduce risk and protect trust."
            ]
        },
        "blockchain": {
            "explanation": "Blockchain is a distributed digital ledger that records transactions in a secure, transparent, and tamper-resistant way across multiple computers.",
            "takeaways": [
                "Blockchain improves transparency and trust in transactions.",
                "It is used in finance, supply chains, and digital identity systems.",
                "Security and scalability remain important challenges."
            ]
        },
        "data science": {
            "explanation": "Data science is the field of extracting meaningful insights from data using statistics, programming, and analytical thinking.",
            "takeaways": [
                "Data science turns raw information into useful knowledge.",
                "It combines domain knowledge with mathematical analysis.",
                "Good decisions depend on clean, relevant, and trustworthy data."
            ]
        },
    }

    for key, value in library.items():
        if key in text:
            return value

    return {
        "explanation": f"{topic.strip()} is a concept that helps explain how a system, idea, or process works in a practical way. In simple terms, it focuses on the main principles, purpose, and value behind the topic so people can understand it without needing deep technical knowledge.",
        "takeaways": [
            f"{topic.strip()} revolves around a few core ideas or principles.",
            "Understanding the topic helps connect theory to practical use.",
            "Learning the basics makes it easier to explore deeper concepts and applications."
        ]
    }


def generate_with_openai(topic: str) -> Tuple[str, List[str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return generate_local_explanation(topic)

    client = OpenAI(api_key=api_key)
    prompt = (
        "Write a short, clear explanation of the topic in simple language. "
        "Then give exactly 3 key takeaways in bullet list format. "
        "Keep the response concise and beginner-friendly.\n\nTopic: "
        f"{topic}"
    )

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful educational assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=250,
        )
        output = response.choices[0].message.content.strip()
        if not output:
            raise ValueError("Empty output")

        lines = [line.strip() for line in output.splitlines() if line.strip()]
        explanation = lines[0] if lines else ""
        takeaways = []
        for line in lines[1:]:
            cleaned = line.lstrip("-*•\t ")
            if cleaned:
                takeaways.append(cleaned)

        if not explanation:
            raise ValueError("No explanation captured")

        if len(takeaways) < 3:
            fallback = generate_local_explanation(topic)
            explanation = fallback[0]
            takeaways = fallback[1][:3]

        return explanation, takeaways[:3]
    except Exception:
        return generate_local_explanation(topic)


def generate_local_explanation(topic: str) -> Tuple[str, List[str]]:
    cleaned_topic = topic.strip()
    if not cleaned_topic:
        raise ValueError("Please enter a topic first.")

    matched = topic_keywords(cleaned_topic)
    return matched["explanation"], matched["takeaways"]


def generate_topic_response(topic: str) -> dict:
    explanation, takeaways = generate_with_openai(topic)
    return {
        "topic": topic.strip(),
        "explanation": explanation,
        "takeaways": takeaways,
    }


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/generate")
def generate():
    topic = request.form.get("topic", "").strip()
    if not topic:
        return render_template("index.html", error="Please enter a topic to explain."), 400

    try:
        result = generate_topic_response(topic)
        return render_template(
            "index.html",
            topic=result["topic"],
            explanation=result["explanation"],
            takeaways=result["takeaways"],
        )
    except ValueError as exc:
        return render_template("index.html", error=str(exc)), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
