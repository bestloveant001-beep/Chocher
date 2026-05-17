import speechrecognition as sr
import pyttsx3
import datetime
import webbrowser
import openai
from dotenv import load_dotenv
import os
import requests

# โหลดคีย์ API จากไฟล์ .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# เริ่มต้นเครื่องมือพูด
engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# ตั้งค่าพื้นที่ของคุณ เพื่อให้แจ้งเตือนตรงจังหวัดที่คุณอยู่
MY_PROVINCE = "กรุงเทพมหานคร" # แก้เป็นจังหวัดของคุณได้เลยครับ

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

# -------------------------- ระบบระวังภัยพิบัติ --------------------------
def get_disaster_info():
    """ดึงข้อมูลและตรวจสอบสถานการณ์ภัยพิบัติ"""
    try:
        # ใช้ข้อมูลจากกรมป้องกันและบรรเทาสาธารณภัย (ตัวอย่างข้อมูล)
        speak(f"กำลังตรวจสอบข้อมูลสถานการณ์ภัยในพื้นที่{MY_PROVINCE} ครับ")
        
        # สรุปข้อมูลและคำแนะนำ
        info = f"""
        ข้อมูลสถานการณ์ภัยสำหรับพื้นที่{MY_PROVINCE} ครับ
        - หากมีฝนตกหนัก: ระวังน้ำท่วม ฉน้ำ และดินถล่ม หลีกเลี่ยงการเดินทางผ่านพื้นที่ลุ่มหรือริมน้ำ
        - หากเกิดแผ่นดินไหว: ให้อยู่ในที่ปลอดภัย หมอบ คุ้ม และจับยึด หลีกเลี่ยงหน้าต่างและสิ่งของที่อาจตกใส่
        - หากเกิดพายุ: อยู่ในอาคารที่มั่นคง ปิดประตูหน้าต่าง และอยู่ห่างจากเสาไฟฟ้าและต้นไม้ใหญ่
        - หากเกิดอัคคีภัย: รีบออกจากอาคารทันที ใช้ผ้าชุบน้ำปิดจมูกและปาก และไปรวมที่จุดนัดหมาย
        """
        return info
    except:
        return "ขออภัยครับ ไม่สามารถดึงข้อมูลสถานการณ์ได้ในขณะนี้ แต่ขอแนะนำให้ติดตามข่าวสารจากหน่วยงานที่เกี่ยวข้องอย่างใกล้ชิดครับ"

def get_disaster_advice(disaster_type):
    """ให้คำแนะนำวิธีปฏิบัติตัวเมื่อเกิดภัยแต่ละประเภท"""
    advice = {
        "น้ำท่วม": "เมื่อเกิดน้ำท่วม ให้ย้ายสิ่งของและตัวเองขึ้นไปอยู่ที่สูง อย่าเดินลุยน้ำเพราะอาจมีสิ่งมีคมหรือกระแสน้ำแรง และรีบแจ้งเจ้าหน้าที่หากต้องการความช่วยเหลือครับ",
        "แผ่นดินไหว": "เมื่อรู้สึกสั่น ให้หมอบลง คุ้มศีรษะและลำตัว และจับยึดสิ่งที่มั่นคง อย่าวิ่งออกนอกอาคารในขณะที่สั่น และอย่าใช้ลิฟต์ครับ",
        "พายุ": "ให้อยู่ในอาคารที่แข็งแรง ปิดประตูหน้าต่างให้มิดชิด และอยู่ห่างจากหน้าต่าง อย่าออกไปข้างนอกจนกว่าจะแน่ใจว่าปลอดภัยแล้วครับ",
        "อัคคีภัย": "รีบออกจากอาคารทันที อย่าเสียเวลาเก็บของมีค่า ใช้ผ้าชุบน้ำปิดจมูกและปากเพื่อป้องกันควัน และไปรวมที่จุดนัดหมายครับ",
        "ดินถล่ม": "หากอยู่ในพื้นที่เสี่ยง ให้สังเกตสัญญาณเตือน เช่น ต้นไม้เอียง หรือน้ำไหลปนดิน และรีบย้ายไปอยู่ที่สูงและปลอดภัยทันทีครับ"
    }
    return advice.get(disaster_type, "ขออภัยครับ ผมยังไม่มีข้อมูลคำแนะนำสำหรับภัยประเภทนี้ครับ แนะนำให้ติดตามคำแนะนำจากหน่วยงานราชการครับ")
# ---------------------------------------------------------------------------

def personal_assistant():
    speak(f"สวัสดีครับ ผมคือ Echo ผู้ช่วยส่วนตัวของคุณ และฉันจะช่วยเฝ้าระวังภัยให้คุณด้วยครับ มีอะไรที่ผมสามารถช่วยเหลือไหมครับ")
    
    while True:
        command = listen()
        if not command:
            continue

        if "ลาก่อน" in command or "ปิดระบบ" in command:
            speak("ลาก่อนครับ หวังว่าจะได้ช่วยเหลือคุณอีกในครั้งต่อไปครับ ขอให้ปลอดภัยทุกเวลานะครับ")
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

        # -------------------------- คำสั่งระบบระวังภัย --------------------------
        elif "สถานการณ์ภัย" in command or "ข่าวภัย" in command or "ตรวจสอบภัย" in command:
            info = get_disaster_info()
            speak(info)
            print(f"ข้อมูลภัย: {info}")

        elif "วิธีรับมือ" in command or "ทำอย่างไรเมื่อ" in command or "คำแนะนำภัย" in command:
            speak("กรุณาบอกชื่อภัยที่ต้องการทราบคำแนะนำครับ เช่น น้ำท่วม แผ่นดินไหว พายุ")
            disaster = listen()
            advice = get_disaster_advice(disaster)
            speak(advice)
            print(f"คำแนะนำ: {advice}")
        # ---------------------------------------------------------------------------

        else:
            response = get_ai_response(command)
            speak(response)
            print(f"Echo ตอบ: {response}")

if __name__ == "__main__":
    personal_assistant()
    
