import argparse
import logging
import os
import time
from dataclasses import dataclass

import httpx
import schedule
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

parser = argparse.ArgumentParser(description="Skyeng Telegram Bot")
parser.add_argument(
    "--once", action="store_true", help="Запустить без планировщика один раз и выйти"
)
args = parser.parse_args()

load_dotenv()

skyeng_token = os.getenv("SKYENG_TOKEN")
skyeng_student_id = os.getenv("SKYENG_STUDENT_ID")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_user_id = os.getenv("TELEGRAM_USER_ID")
start_app = os.getenv("START_APP")


@dataclass
class Word:
    word: str
    definition: str
    translation: str
    transcription: str
    example: list[str]
    image: str
    part_of_speech: str


class SkyengDictionaryApi:

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "*/*",
        }
        self.http_client = httpx.Client(headers=self.headers)

    def get_all_wordsets(self, student_id: int) -> list:
        """
        Получить все списки слов
        """
        wordsets = []
        for i in range(1, 100):
            resp = self.http_client.get(
                url=f"https://api-words.skyeng.ru/api/for-vimbox/v1/wordsets.json?studentId={student_id}&pageSize=100&page={i}",
            )

            wordsets += resp.json()["data"]
            if resp.json()["meta"]["currentPage"] == resp.json()["meta"]["lastPage"]:
                break
        return wordsets

    def get_all_meaning_ids_from_wordset(
        self, student_id: int, wordset_id: int
    ) -> list[dict]:
        """
        Получить идентификаторы значений
        """
        words = []

        for i in range(1, 100):
            resp = self.http_client.get(
                url=f"https://api-words.skyeng.ru/api/v1/wordsets/{wordset_id}/words.json?studentId={student_id}&wordsetId={wordset_id}&pageSize=100",
            )

            words += resp.json()["data"]
            if resp.json()["meta"]["currentPage"] == resp.json()["meta"]["lastPage"]:
                break
        return words

    def get_meanings(self, word_ids: list[int] | int) -> dict:
        """
        Получить значения слов
        """
        if isinstance(word_ids, int):
            word_ids = [word_ids]

        resp = self.http_client.get(
            url=f"https://dictionary.skyeng.ru/api/for-services/v2/meanings?ids={','.join(str(w) for w in word_ids)}",
        )

        return resp.json()

    def get_meaning_ids_by_meanings(self, meanings: list[dict]) -> list[int]:
        """
        Получить идентификаторы значений
        """
        return [m["meaningId"] for m in meanings]

    def get_words_from_last_lesson(self, student_id: int) -> list[Word]:
        words_store = []
        words_set = self.get_all_wordsets(student_id=student_id)[0]["id"]
        meanings = self.get_all_meaning_ids_from_wordset(
            student_id=student_id, wordset_id=words_set
        )
        meaning_ids = self.get_meaning_ids_by_meanings(meanings=meanings)
        words = self.get_meanings(word_ids=meaning_ids)
        for word in words:
            examples = [w["text"] for w in word["examples"]]
            try:
                image = word["images"][0]["url"]
            except IndexError:
                image = ""
            result = Word(
                word=word["text"],
                definition=word["definition"]["text"],
                translation=word["translation"]["text"],
                transcription=word["transcription"],
                example=examples,
                image=image,
                part_of_speech=word["partOfSpeechCode"],
            )
            words_store.append(result)
        return words_store


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.client = httpx.Client()

    def send_photo(self, url: str, caption: str):
        self.client.post(
            url=f"https://api.telegram.org/bot{self.token}/sendPhoto",
            json={
                "chat_id": telegram_user_id,
                "photo": url,
                "caption": caption,
                "parse_mode": "HTML",
            },
        )

    def send_message(self, message: str):
        self.client.post(
            url=f"https://api.telegram.org/bot{self.token}/sendMessage",
            json={"chat_id": telegram_user_id, "text": message, "parse_mode": "HTML"},
        )


def main():
    logging.info("Bot started")
    t = TelegramBot(token=telegram_bot_token)
    s = SkyengDictionaryApi(token=skyeng_token)
    r = s.get_words_from_last_lesson(student_id=skyeng_student_id)
    for word in r:
        message = f"<b>{word.word}</b> <i>[{word.transcription}]</i> - <span class=tg-spoiler>{word.translation}</span>\n\n"
        message += f"<i>{word.definition}</i>\n\n"
        message += "\n".join(str(example) for example in word.example)
        t.send_photo(url=word.image, caption=message)

    logging.info("Bot finished")


schedule.every().day.at(start_app).do(main)

if __name__ == "__main__":
    logging.info("Service started")
    if args.once:
        logging.info("Running once mode")
        main()
    else:
        logging.info("Service will start at %s", start_app)
        schedule.every().day.at(start_app).do(main)
        while True:
            schedule.run_pending()
            time.sleep(1)
