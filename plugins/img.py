from api import send_photo, send_message, send_chat_action
from reborn import log
import requests
import json
import random
from os import environ

def requestGoogle(query):
    url = "https://www.googleapis.com/customsearch/v1?"
    url = url + "cx=006518944303354753471:um8whdniwke"
    url = url + "&searchType=image"
    url = url + "&key=" + environ["GOOGLEKEY"]

    url = url + "&q=" + query

    response = requests.get(url)
    response = json.loads(response.content)

    index = random.randint(0, len(response["items"]) - 1)

    log("Imagem escolhida: " + response["items"][index]["link"])

    return response["items"][index]


def getValidLink(query):
    supportedFormats = ["jpg", "jpeg", "png", "gif"]

    valid = False

    google_img = requestGoogle(query)
    url = google_img["link"]

    while not valid:
        for format in supportedFormats:
            if url[-5:].find(format) != -1:
                valid = True
                break

        if not valid:
            log("Formato inválido, tentando novamente...")
            google_img = requestGoogle(query)
            url = google_img["link"]

    return google_img

def on_msg_received(msg, matches):
    chat = msg["chat"]["id"]

    try:
        img = getValidLink(matches.group(1))

        link = img["link"]
        source = img["image"]["contextLink"]
        snippet = img["snippet"]
        caption_text = "[" + snippet + "](" + source + ")"

        send_message(chat, "AE pora ta aki a imag......")
        send_chat_action(chat, "upload_photo")
        sent = send_photo(chat, link, caption_text, msg["message_id"])

        while sent["ok"] == "false":
            log("sendPhoto retornou false, rentando novamente...")
            img = getValidLink(matches.group(1))
            sent = send_photo(chat, link, caption_text)

    except:
        send_message(chat, "pora n axei nd disso ai n.....") 
