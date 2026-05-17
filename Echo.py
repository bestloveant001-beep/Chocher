import speechrecognition as sr
import pyttsx3
import datetime
import webbrowser
import openai
from dotenv import load_dotenv
import os

# โหลดคีย์ API จากไฟล์ .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# เริ่มต้นเครื่องมือพูด
engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("กำลังฟัง... กรุณาพูดคำสั่งครับ")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("กำลังประมวลผล...")
        command = recognizer.recognize_google(audio, language='th-TH')
        print(f"คุณพูดว่า: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("ขออภัยครับ ผมไม่เข้าใจสิ่งที่คุณพูด กรุณาพูดอีกครั้งครับ")
        return ""
    except sr.RequestError:
        speak("ขออภัยครับ ระบบมีปัญหาในการเชื่อมต่อกับบริการรู้จำเสียงครับ")
        return ""

def get_ai_response(question):
    if not openai.api_key:
        return "ขออภัยครับ ยังไม่ได้ตั้งค่าคีย์ API จึงไม่สามารถตอบคำถามทั่วไปได้ครับ"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ขออภัยครับ เกิดข้อผิดพลาด: {str(e)}"

def personal_assistant():
    speak("สวัสดีครับ ผมคือ Echo ผู้ช่วยส่วนตัวของคุณ มีอะไรที่ผมสามารถช่วยเหลือไหมครับ")
    
    while True:
        command = listen()
        if not command:
            continue

        if "ลาก่อน" in command or "ปิดระบบ" in command:
            speak("ลาก่อนครับ หวังว่าจะได้ช่วยเหลือคุณอีกในครั้งต่อไปครับ")
            break

        elif "เวลา" in command:
            now = datetime.datetime.now()
            time_str = now.strftime("%H นาฬิกา %M นาที %S วินาที ครับ")
            speak(f"ขณะนี้เวลา {time_str}")

        elif "วันที่" in command:
            today = datetime.datetime.now()
            date_str = today.strftime("%d เดือน %m ปี %Y ครับ")
            speak(f"วันนี้คือวันที่ {date_str}")

        elif "เปิดเว็บ" in command or "เปิดไซต์" in command:
            speak("กรุณาบอกชื่อเว็บไซต์ที่ต้องการเปิดครับ")
            site_name = listen()
            if "กูเกิล" in site_name:
                webbrowser.open("https://www.google.co.th")
                speak("กำลังเปิดหน้าเว็บกูเกิลครับ")
            elif "ยูทูป" in site_name:
                webbrowser.open("https://www.youtube.com")
                speak("กำลังเปิดหน้าเว็บยูทูปครับ")
            else:
                speak("ขออภัยครับ ผมยังไม่สามารถเปิดเว็บไซต์ที่คุณต้องการได้ครับ")

        else:
            response = get_ai_response(command)
            speak(response)
            print(f"Echo ตอบ: {response}")

if __name__ == "__main__":
    personal_assistant()
      
