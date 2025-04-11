import random
import json
import torch
import os
from .model import NeuralNet
from .chatbot_nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

script_dir = os.path.dirname(os.path.abspath(__file__))
intents_path = os.path.join(script_dir, "intents.json")

with open(intents_path, 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

model_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(model_dir, "model.pth")

FILE = model_path
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "Mímir"

fallback_suggestions = [
    "Sorry, I didn't quite understand that. You could ask me about topics like Norway's capital (Oslo), its location, famous fjords, the Northern Lights, or the currency (NOK).",
    "I'm not sure how to respond to that. Perhaps you could ask about popular cities like Bergen or Tromsø, the cost of visiting Norway, the Sámi people, or what 'koselig' means?",
    "Hmm, I don't have information on that specific query. Why not ask about Norway's highest mountain, the Midnight Sun, the Vikings, or whether you need a visa?",
    "I couldn't find a direct answer. Maybe rephrase, or ask about something else? For example, I know about the emergency numbers, tap water safety, popular dishes, or the national day (May 17th)."
    ]
print("Welcome to the Norway FAQ Chatbot Mímir! (type 'quit' to exit)")

def generations(message):
    sentence = tokenize(message)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.70:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return {"bot_name": bot_name, "Response": random.choice(intent["responses"])}
    else:
        return {"bot_name": bot_name, "Response": random.choice(fallback_suggestions)}