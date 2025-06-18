from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import openai

app = Flask(__name__)

# ==== PUT YOUR OPENAI API KEY HERE ====
openai.api_key = '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'  # <-- Replace with your key

# ===== OUTBOUND CALL HANDLER =====
@app.route("/outbound", methods=['GET', 'POST'])
def outbound():
    resp = VoiceResponse()
    gather = Gather(
        input='speech',
        timeout=5,
        language='en-US',
        action='/process_speech'
    )
    gather.say(
        'Hi, I am the virtual assistant from Buildn 123. '
        'How can I help you with our real estate project today?'
    )
    resp.append(gather)
    resp.redirect('/outbound')  # Repeat if nothing is said
    return Response(str(resp), mimetype='text/xml')

# ===== SPEECH PROCESSING AND GPT-4 INTEGRATION =====
@app.route("/process_speech", methods=['GET', 'POST'])
def process_speech():
    user_input = request.values.get('SpeechResult', '').strip()
    print(f"User said: {user_input}")

    resp = VoiceResponse()
    if user_input:
        # -- CONTEXT FOR GPT-4 --
        system_prompt = (
            "You are a helpful AI assistant for Buildn 123, a residential real estate project in Dallas, "
            "offering modern 2- and 3-bedroom apartments starting at $180,000. "
            "Answer user questions clearly and briefly, and provide relevant details."
        )

        # -- ASK GPT-4 FOR AN ANSWER --
        try:
            gpt_response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=100,
                temperature=0.3,
            )
            answer = gpt_response['choices'][0]['message']['content']
            print(f"GPT-4 answered: {answer}")

        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            answer = "I'm sorry, there was a problem answering your question. Please try again later."

        # -- READ GPT-4 ANSWER TO CALLER --
        resp.say(answer, language='en-US', voice='Polly.Joanna')
        resp.hangup()
    else:
        resp.say(
            'I did not hear you. Could you please repeat your question?',
            language='en-US',
            voice='Polly.Joanna'
        )
        resp.redirect('/outbound')
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
